# # Note: The exact LangGraph API may vary; this file assumes Graph/Node constructors
# # where Node wraps a Python callable. Adapt imports if your installed langgraph API differs.

# from langgraph import Graph, Node
# from services.pdf_loader import pdf_to_chunks, save_pdf
# from services.vector_store import add_chunks, retrieve_by_text
# from services.embeddings import embed_texts, get_embedding_model
# from services.critique import grade_relevance, grade_grounding, grade_usefulness
# from services.llm_client import generate_text
# from config import settings

# def build_graph():
#     g = Graph(name="self_reflective_rag")

#     # Node: ingest pdf (optional)
#     def ingest_pdf(inputs):
#         pdf_path = inputs.get("pdf_path")
#         if not pdf_path:
#             return {"status": "no_pdf"}
#         chunks = pdf_to_chunks(pdf_path)
#         add_chunks(chunks)
#         return {"ingested": len(chunks), "chunks": chunks}

#     # Node: retrieval
#     def retrieval(inputs):
#         query = inputs["query"]
#         top_k = inputs.get("top_k", settings.TOP_K)
#         docs = retrieve_by_text(query, top_k=top_k)
#         return {"retrieved": docs}

#     # Node: isrel
#     def isrel(inputs):
#         query = inputs["query"]
#         docs = inputs.get("retrieved", [])
#         res = grade_relevance(query, docs)
#         return {"isrel": res}

#     # Node: rewrite query (simple)
#     def rewrite_query(inputs):
#         query = inputs["query"]
#         reason = inputs.get("isrel", {}).get("reason", "")
#         p = f"Rewrite the user's query to get better retrieval results. Original: {query}\nReason: {reason}\nReturn only the rewritten query."
#         resp = generate_text(p, max_output_tokens=128)
#         return {"rewritten": resp["text"].strip()}

#     # Node: generation
#     def generation(inputs):
#         query = inputs["query"]
#         docs = inputs.get("retrieved", [])
#         context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in docs])
#         prompt = f"User query: {query}\n\nContext:\n{context}\n\nProvide a concise, grounded answer and cite document ids."
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"answer": resp["text"].strip(), "raw": resp["raw"]}

#     # Node: issup
#     def issup(inputs):
#         answer = inputs["answer"]
#         docs = inputs.get("retrieved", [])
#         res = grade_grounding(answer, docs)
#         return {"issup": res}

#     # Node: isuse
#     def isuse(inputs):
#         answer = inputs["answer"]
#         query = inputs["query"]
#         res = grade_usefulness(answer, query)
#         return {"isuse": res}

#     # Node: refine
#     def refine(inputs):
#         answer = inputs["answer"]
#         docs = inputs.get("retrieved", [])
#         critique = {"issup": inputs.get("issup"), "isuse": inputs.get("isuse")}
#         doc_ids = ", ".join([d["id"] for d in docs])
#         prompt = f"""Refine the previous answer using critiques.

# Previous answer:
# {answer}

# Critiques:
# {critique}

# Context: documents {doc_ids}
# Use the context to produce a corrected, fully-supported final answer. Return final answer only.
# """
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"refined": resp["text"].strip(), "raw": resp["raw"]}

#     # wrap Node(callable)
#     n_ingest = Node("ingest_pdf", ingest_pdf)
#     n_retrieval = Node("retrieval", retrieval)
#     n_isrel = Node("isrel", isrel)
#     n_rewrite = Node("rewrite_query", rewrite_query)
#     n_generation = Node("generation", generation)
#     n_issup = Node("issup", issup)
#     n_isuse = Node("isuse", isuse)
#     n_refine = Node("refine", refine)

#     # add to graph
#     g.add_node(n_ingest)
#     g.add_node(n_retrieval)
#     g.add_node(n_isrel)
#     g.add_node(n_rewrite)
#     g.add_node(n_generation)
#     g.add_node(n_issup)
#     g.add_node(n_isuse)
#     g.add_node(n_refine)

#     # edges are logical in orchestrator; LangGraph graph can be used for visualization too
#     return g


















# from langgraph.graph import StateGraph, START, END
# from config import settings
# from services.pdf_loader import pdf_to_chunks, save_pdf
# from services.vector_store import add_chunks, retrieve_by_text
# from services.embeddings import embed_texts, get_embedding_model
# from services.critique import grade_relevance, grade_grounding, grade_usefulness
# from services.llm_client import generate_text


# def build_graph():
#     """Define the Self-Reflective RAG pipeline graph using LangGraph v1 API."""
#     graph = StateGraph()

#     # -------------------------
#     # Define Node Functions
#     # -------------------------

#     def ingest_pdf(state):
#         pdf_path = state.get("pdf_path")
#         if not pdf_path:
#             return {"status": "no_pdf"}
#         chunks = pdf_to_chunks(pdf_path)
#         add_chunks(chunks)
#         return {"ingested": len(chunks), "chunks": chunks}

#     def retrieval(state):
#         query = state["query"]
#         top_k = state.get("top_k", settings.TOP_K)
#         docs = retrieve_by_text(query, top_k=top_k)
#         return {"retrieved": docs}

#     def isrel(state):
#         query = state["query"]
#         docs = state.get("retrieved", [])
#         res = grade_relevance(query, docs)
#         return {"isrel": res}

#     def rewrite_query(state):
#         query = state["query"]
#         reason = state.get("isrel", {}).get("reason", "")
#         prompt = f"Rewrite the user's query to get better retrieval results.\nOriginal: {query}\nReason: {reason}\nReturn only the rewritten query."
#         resp = generate_text(prompt, max_output_tokens=128)
#         return {"rewritten": resp["text"].strip()}

#     def generation(state):
#         query = state["query"]
#         docs = state.get("retrieved", [])
#         context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in docs])
#         prompt = f"User query: {query}\n\nContext:\n{context}\n\nProvide a concise, grounded answer and cite document ids."
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"answer": resp["text"].strip(), "raw": resp["raw"]}

#     def issup(state):
#         answer = state["answer"]
#         docs = state.get("retrieved", [])
#         res = grade_grounding(answer, docs)
#         return {"issup": res}

#     def isuse(state):
#         answer = state["answer"]
#         query = state["query"]
#         res = grade_usefulness(answer, query)
#         return {"isuse": res}

#     def refine(state):
#         answer = state["answer"]
#         docs = state.get("retrieved", [])
#         critique = {"issup": state.get("issup"), "isuse": state.get("isuse")}
#         doc_ids = ", ".join([d["id"] for d in docs])
#         prompt = f"""Refine the previous answer using critiques.

# Previous answer:
# {answer}

# Critiques:
# {critique}

# Context: documents {doc_ids}
# Use the context to produce a corrected, fully-supported final answer. Return final answer only.
# """
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"refined": resp["text"].strip(), "raw": resp["raw"]}

#     # -------------------------
#     # Add Nodes to Graph
#     # -------------------------
#     graph.add_node("ingest_pdf", ingest_pdf)
#     graph.add_node("retrieval", retrieval)
#     graph.add_node("isrel", isrel)
#     graph.add_node("rewrite_query", rewrite_query)
#     graph.add_node("generation", generation)
#     graph.add_node("issup", issup)
#     graph.add_node("isuse", isuse)
#     graph.add_node("refine", refine)

#     # NOTE: We're not chaining automatically here; the orchestrator controls flow logic
#     # This graph is used as a registry of callable nodes.
#     graph.add_edge(START, "retrieval")
#     graph.add_edge("refine", END)

#     return graph









# from typing import TypedDict, List, Dict, Any
# from langgraph.graph import StateGraph
# from services.pdf_loader import pdf_to_chunks, save_pdf
# from services.vector_store import add_chunks, retrieve_by_text
# from services.embeddings import get_embedding_model
# from services.critique import grade_relevance, grade_grounding, grade_usefulness
# from services.llm_client import generate_text
# from config import settings


# # ---- Define shared state schema ----
# class GraphState(TypedDict, total=False):
#     query: str
#     top_k: int
#     pdf_path: str
#     retrieved: List[Dict[str, Any]]
#     isrel: Dict[str, Any]
#     rewritten: str
#     answer: str
#     issup: Dict[str, Any]
#     isuse: Dict[str, Any]
#     refined: str
#     ingested: int
#     chunks: List[str]


# # ---- Build the graph ----
# def build_graph():
#     graph = StateGraph(GraphState)

#     # ----- Node definitions -----

#     def ingest_pdf(state: GraphState):
#         pdf_path = state.get("pdf_path")
#         if not pdf_path:
#             return {"status": "no_pdf"}
#         chunks = pdf_to_chunks(pdf_path)
#         add_chunks(chunks)
#         return {"ingested": len(chunks), "chunks": chunks}

#     def retrieval(state: GraphState):
#         query = state["query"]
#         top_k = state.get("top_k", settings.TOP_K)
#         docs = retrieve_by_text(query, top_k=top_k)
#         return {"retrieved": docs}

#     def isrel(state: GraphState):
#         query = state["query"]
#         docs = state.get("retrieved", [])
#         res = grade_relevance(query, docs)
#         return {"isrel": res}

#     def rewrite_query(state: GraphState):
#         query = state["query"]
#         reason = state.get("isrel", {}).get("reason", "")
#         prompt = f"Rewrite the user's query to improve retrieval.\nOriginal: {query}\nReason: {reason}\nReturn only the rewritten query."
#         resp = generate_text(prompt, max_output_tokens=128)
#         return {"rewritten": resp["text"].strip()}

#     def generation(state: GraphState):
#         query = state.get("rewritten") or state["query"]
#         docs = state.get("retrieved", [])
#         context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in docs])
#         prompt = f"User query: {query}\n\nContext:\n{context}\n\nProvide a concise, grounded answer and cite document ids."
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"answer": resp["text"].strip(), "raw": resp["raw"]}

#     def issup(state: GraphState):
#         answer = state["answer"]
#         docs = state.get("retrieved", [])
#         res = grade_grounding(answer, docs)
#         return {"issup": res}

#     def isuse(state: GraphState):
#         answer = state["answer"]
#         query = state["query"]
#         res = grade_usefulness(answer, query)
#         return {"isuse": res}

#     def refine(state: GraphState):
#         answer = state["answer"]
#         docs = state.get("retrieved", [])
#         critique = {"issup": state.get("issup"), "isuse": state.get("isuse")}
#         doc_ids = ", ".join([d["id"] for d in docs])
#         prompt = f"""Refine the previous answer using critiques.

# Previous answer:
# {answer}

# Critiques:
# {critique}

# Context: documents {doc_ids}
# Produce a corrected, fully-supported final answer. Return only the refined answer.
# """
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"refined": resp["text"].strip(), "raw": resp["raw"]}

#     # ----- Add nodes to the graph -----
#     graph.add_node("ingest_pdf", ingest_pdf)
#     graph.add_node("retrieval", retrieval)
#     graph.add_node("isrel", isrel)
#     graph.add_node("rewrite_query", rewrite_query)
#     graph.add_node("generation", generation)
#     graph.add_node("issup", issup)
#     graph.add_node("isuse", isuse)
#     graph.add_node("refine", refine)

#     # ----- Define simple logical flow -----
#     graph.add_edge("retrieval", "isrel")
#     graph.add_edge("isrel", "generation")
#     graph.add_edge("generation", "issup")
#     graph.add_edge("generation", "isuse")
#     graph.add_edge("issup", "refine")
#     graph.add_edge("isuse", "refine")

#     # Set entry and finish points
#     graph.set_entry_point("retrieval")
#     graph.set_finish_point("refine")

#     # ----- Compile graph -----
#     return graph.compile()










# from typing import TypedDict, List, Dict, Any
# from langgraph.graph import StateGraph
# from langgraph.graph.state import State
# from services.vector_store import retrieve_by_text, add_pdf_to_chroma
# from services.embeddings import get_embedding_model
# from services.critique import grade_relevance, grade_grounding, grade_usefulness
# from services.llm_client import generate_text
# from config import settings


# class GraphState(TypedDict):
#     query: str
#     retrieved: List[Dict[str, Any]]
#     answer: str
#     refined: str
#     isrel: Dict[str, Any]
#     issup: Dict[str, Any]
#     isuse: Dict[str, Any]


# def build_graph():
#     """
#     Builds a LangGraph pipeline graph using the new API.
#     Compatible with langgraph 1.0+.
#     """
#     graph = StateGraph(GraphState)

#     # --- Node: Ingest PDF ---
#     def ingest_pdf(state: GraphState) -> GraphState:
#         pdf_path = state.get("pdf_path")
#         if not pdf_path:
#             return {"status": "no_pdf"}
#         add_pdf_to_chroma(pdf_path, batch_size=8)
#         return {"status": "ingested", "pdf_path": pdf_path}

#     # --- Node: Retrieval ---
#     def retrieval(state: GraphState) -> GraphState:
#         query = state["query"]
#         top_k = settings.TOP_K
#         docs = retrieve_by_text(query, top_k=top_k)
#         return {"retrieved": docs}

#     # --- Node: ISREL (Relevance critique) ---
#     def isrel(state: GraphState) -> GraphState:
#         query = state["query"]
#         docs = state.get("retrieved", [])
#         res = grade_relevance(query, docs)
#         return {"isrel": res}

#     # --- Node: Rewrite query ---
#     def rewrite_query(state: GraphState) -> GraphState:
#         query = state["query"]
#         reason = state.get("isrel", {}).get("reason", "")
#         p = f"Rewrite the user's query for better retrieval. Original: {query}\nReason: {reason}\nReturn only the rewritten query."
#         resp = generate_text(p, max_output_tokens=128)
#         return {"query": resp["text"].strip()}

#     # --- Node: Generation ---
#     def generation(state: GraphState) -> GraphState:
#         query = state["query"]
#         docs = state.get("retrieved", [])
#         context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in docs])
#         prompt = (
#             f"User query: {query}\n\nContext:\n{context}\n\n"
#             f"Provide a concise, grounded answer and cite document IDs."
#         )
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"answer": resp["text"].strip()}

#     # --- Node: ISSUP (Grounding critique) ---
#     def issup(state: GraphState) -> GraphState:
#         answer = state.get("answer", "")
#         docs = state.get("retrieved", [])
#         res = grade_grounding(answer, docs)
#         return {"issup": res}

#     # --- Node: ISUSE (Usefulness critique) ---
#     def isuse(state: GraphState) -> GraphState:
#         answer = state.get("answer", "")
#         query = state.get("query", "")
#         res = grade_usefulness(answer, query)
#         return {"isuse": res}

#     # --- Node: Refine answer ---
#     def refine(state: GraphState) -> GraphState:
#         answer = state.get("answer", "")
#         docs = state.get("retrieved", [])
#         critique = {
#             "issup": state.get("issup"),
#             "isuse": state.get("isuse")
#         }
#         doc_ids = ", ".join([d["id"] for d in docs])
#         prompt = f"""Refine the previous answer using critiques.

# Previous answer:
# {answer}

# Critiques:
# {critique}

# Context: documents {doc_ids}
# Return the refined answer only."""
#         resp = generate_text(prompt, max_output_tokens=800)
#         return {"refined": resp["text"].strip()}

#     # --- Add nodes ---
#     graph.add_node("ingest_pdf", ingest_pdf)
#     graph.add_node("retrieval", retrieval)
#     graph.add_node("isrel", isrel)
#     graph.add_node("rewrite_query", rewrite_query)
#     graph.add_node("generation", generation)
#     graph.add_node("issup", issup)
#     graph.add_node("isuse", isuse)
#     graph.add_node("refine", refine)

#     # --- Define graph flow ---
#     graph.set_entry_point("retrieval")
#     graph.add_edge("retrieval", "isrel")
#     graph.add_edge("isrel", "generation")
#     graph.add_edge("generation", "issup")
#     graph.add_edge("issup", "isuse")
#     graph.add_edge("isuse", "refine")

#     return graph.compile()









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
