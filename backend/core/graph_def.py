
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph
from services.vector_store import retrieve_by_text, add_pdf_to_chroma
from services.embeddings import get_embedding_model
from services.critique import grade_relevance, grade_grounding, grade_usefulness
from services.llm_client import generate_text
from config import settings


class GraphState(TypedDict):
    query: str
    retrieved: List[Dict[str, Any]]
    answer: str
    refined: str
    isrel: Dict[str, Any]
    issup: Dict[str, Any]
    isuse: Dict[str, Any]


def build_graph():
    """
    Builds a LangGraph pipeline graph using the new API.
    Compatible with langgraph 1.0+.
    """
    graph = StateGraph(GraphState)

    # --- Node: Ingest PDF ---
    def ingest_pdf(state: GraphState) -> GraphState:
        pdf_path = state.get("pdf_path")
        if not pdf_path:
            return {"status": "no_pdf"}
        add_pdf_to_chroma(pdf_path, batch_size=8)
        return {"status": "ingested", "pdf_path": pdf_path}

    # --- Node: Retrieval ---
    def retrieval(state: GraphState) -> GraphState:
        query = state["query"]
        top_k = settings.TOP_K
        docs = retrieve_by_text(query, top_k=top_k)
        return {"retrieved": docs}

    # --- Node: ISREL (Relevance critique) ---
    def isrel(state: GraphState) -> GraphState:
        query = state["query"]
        docs = state.get("retrieved", [])
        res = grade_relevance(query, docs)
        return {"isrel": res}

    # --- Node: Rewrite query ---
    def rewrite_query(state: GraphState) -> GraphState:
        query = state["query"]
        reason = state.get("isrel", {}).get("reason", "")
        p = f"Rewrite the user's query for better retrieval. Original: {query}\nReason: {reason}\nReturn only the rewritten query."
        resp = generate_text(p, max_output_tokens=128)
        return {"query": resp["text"].strip()}

    # --- Node: Generation ---
    def generation(state: GraphState) -> GraphState:
        query = state["query"]
        docs = state.get("retrieved", [])
        context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in docs])
        prompt = (
            f"User query: {query}\n\nContext:\n{context}\n\n"
            f"Provide a concise, grounded answer and cite document IDs."
        )
        resp = generate_text(prompt, max_output_tokens=800)
        return {"answer": resp["text"].strip()}

    # --- Node: ISSUP (Grounding critique) ---
    def issup(state: GraphState) -> GraphState:
        answer = state.get("answer", "")
        docs = state.get("retrieved", [])
        res = grade_grounding(answer, docs)
        return {"issup": res}

    # --- Node: ISUSE (Usefulness critique) ---
    def isuse(state: GraphState) -> GraphState:
        answer = state.get("answer", "")
        query = state.get("query", "")
        res = grade_usefulness(answer, query)
        return {"isuse": res}

    # --- Node: Refine answer ---
    def refine(state: GraphState) -> GraphState:
        answer = state.get("answer", "")
        docs = state.get("retrieved", [])
        critique = {
            "issup": state.get("issup"),
            "isuse": state.get("isuse")
        }
        doc_ids = ", ".join([d["id"] for d in docs])
        prompt = f"""Refine the previous answer using critiques.

Previous answer:
{answer}

Critiques:
{critique}

Context: documents {doc_ids}
Return the refined answer only."""
        resp = generate_text(prompt, max_output_tokens=800)
        return {"refined": resp["text"].strip()}

    # --- Add nodes ---
    graph.add_node("ingest_pdf", ingest_pdf)
    graph.add_node("retrieval", retrieval)
    graph.add_node("isrel", isrel)
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("generation", generation)
    graph.add_node("issup", issup)
    graph.add_node("isuse", isuse)
    graph.add_node("refine", refine)

    # --- Define graph flow ---
    graph.set_entry_point("retrieval")
    graph.add_edge("retrieval", "isrel")
    graph.add_edge("isrel", "generation")
    graph.add_edge("generation", "issup")
    graph.add_edge("issup", "isuse")
    graph.add_edge("isuse", "refine")

    return graph.compile()
