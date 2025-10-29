from services.vector_store import retrieve_by_text
from services.critique import grade_relevance, grade_grounding, grade_usefulness
from services.llm_client import generate_text
from config import settings
from utils.logger import log_trace

def run_pipeline(initial_query, top_k=None):
    """
    Orchestrates the Self-Reflective RAG pipeline manually
    using direct function calls instead of LangGraph.
    """
    top_k = top_k or settings.TOP_K
    trace = {"query": initial_query, "stages": [], "final_answer": None, "passed": False}

    # 1️⃣ Retrieval
    retrieved = retrieve_by_text(initial_query, top_k=top_k)
    trace["stages"].append({"stage": "retrieval", "retrieved_ids": [d["id"] for d in retrieved]})

    # 2️⃣ ISREL (Relevance check)
    isrel = grade_relevance(initial_query, retrieved)
    trace["stages"].append({"stage": "isrel", "result": isrel})

    # 3️⃣ Relevance rewrite loop
    rewrites = 0
    query = initial_query
    while not isrel.get("is_relevant", True) and rewrites < settings.MAX_REWRITE_ATTEMPTS:
        rewrites += 1
        
        # Rewrite query
        rewrite_prompt = f"Rewrite the user's query to get better retrieval results. Original: {query}\nReason: {isrel.get('reason', '')}\nReturn only the rewritten query."
        rewrite_resp = generate_text(rewrite_prompt, max_output_tokens=128)
        new_q = rewrite_resp["text"].strip()
        
        if not new_q:
            break
        query = new_q

        # Re-retrieve
        retrieved = retrieve_by_text(query, top_k=top_k)
        trace["stages"].append({"stage": "retrieval_after_rewrite", "round": rewrites, "retrieved_ids": [d["id"] for d in retrieved]})

        # Re-check relevance
        isrel = grade_relevance(query, retrieved)
        trace["stages"].append({"stage": "isrel_after_rewrite", "round": rewrites, "result": isrel})

    if not isrel.get("is_relevant", True):
        trace["stages"].append({"stage": "abort", "reason": "no_relevant_docs"})
        log_trace({"query": query, "trace": trace})
        return {"answer": "Insufficient context to answer the query.", "trace": trace}

    # 4️⃣ Generation
    context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in retrieved])
    gen_prompt = f"User query: {query}\n\nContext:\n{context}\n\nProvide a concise, grounded answer and cite document ids."
    gen_resp = generate_text(gen_prompt, max_output_tokens=800)
    answer = gen_resp["text"].strip()
    trace["stages"].append({"stage": "generation", "answer": answer})

    # 5️⃣ Critique + refinement loop
    rounds = 0
    last_ids = [d["id"] for d in retrieved]
    
    while True:
        rounds += 1
        
        # Check grounding and usefulness
        issup = grade_grounding(answer, retrieved)
        isuse = grade_usefulness(answer, query)
        trace["stages"].append({"stage": "issup", "round": rounds, "result": issup})
        trace["stages"].append({"stage": "isuse", "round": rounds, "result": isuse})

        # If both checks pass, we're done
        if issup.get("fully_supported", False) and isuse.get("useful", False):
            trace["final_answer"] = answer
            trace["passed"] = True
            break

        # Stop if max rounds reached
        if rounds >= settings.MAX_REFINEMENT_ROUNDS:
            trace["stages"].append({"stage": "stop", "reason": "max_refinement_reached", "rounds": rounds})
            break

        # Optional: guided re-retrieval if missing info
        missing = issup.get("missing_items", [])
        if missing:
            guided_q = query + " " + " ".join(missing)
            new_retrieved = retrieve_by_text(guided_q, top_k=top_k)
            new_ids = [d["id"] for d in new_retrieved]
            if set(new_ids) != set(last_ids):
                retrieved = new_retrieved
                last_ids = new_ids
                trace["stages"].append({"stage": "re_retrieval", "round": rounds, "new_ids": new_ids})
            else:
                trace["stages"].append({"stage": "re_retrieval", "round": rounds, "note": "no_new_docs"})

        # Refine answer
        doc_ids = ", ".join([d["id"] for d in retrieved])
        ref_prompt = f"""Refine the previous answer using critiques.

Previous answer:
{answer}

Critiques:
Grounding: {issup}
Usefulness: {isuse}

Context: documents {doc_ids}
Use the context to produce a corrected, fully-supported final answer. Return final answer only.
"""
        ref_resp = generate_text(ref_prompt, max_output_tokens=800)
        new_answer = ref_resp["text"].strip()
        trace["stages"].append({"stage": "refinement", "rounds": rounds, "new_answer": new_answer})
        
        if not new_answer or new_answer == answer:
            trace["stages"].append({"stage": "stop", "reason": "no_change_on_refinement"})
            break
        answer = new_answer

    trace["final_answer"] = trace.get("final_answer") or answer
    log_trace({"query": query, "trace": trace})
    return {"answer": trace["final_answer"], "trace": trace}