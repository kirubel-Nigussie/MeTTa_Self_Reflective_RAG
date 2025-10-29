import json, re
from services.llm_client import generate_text
from services.cache_store import get_cached, set_cached

def _extract_json(txt):
    m = re.search(r"\{[\s\S]*\}", txt)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

def isrel_prompt(query, retrieved_docs):
    docs_summary = "\n\n".join([f"[{d['id']}] {d['text'][:600]}" for d in retrieved_docs])
    return f"""You are a quick relevance evaluator.

Query:
{query}

Retrieved documents (id + excerpt):
{docs_summary}

Question:
Do the retrieved documents contain information that is relevant and helpful for answering the user's query?

Return JSON: {{ "is_relevant": true/false, "reason": "brief", "score": 0.0 }}
"""

def issup_prompt(answer, retrieved_docs):
    docs_text = "\n\n".join([f"[{d['id']}]\n{d['text'][:1200]}" for d in retrieved_docs])
    return f"""You are a fact checker.

Generated answer:
{answer}

Retrieved context:
{docs_text}

Tasks:
1) Does the generated answer rely on and align with the evidence present in the retrieved documents?
2) Fact-Checking: List unsupported statements.
3) Grounding Checks: Identify contradictions.
4) Missing Evidence: What aspects were not covered?

Return JSON:
{{
  "fully_supported": true/false,
  "unsupported_claims": [...],
  "contradictions": [...],
  "missing_items": [...],
  "comment": "summary"
}}
"""

def isuse_prompt(answer, query):
    return f"""You are an evaluator of usefulness.

Query:
{query}

Generated answer:
{answer}

Question:
Is the generated answer clear, complete, and useful for the user’s original query?

Return JSON: {{ "useful": true/false, "score": 0.0-1.0, "comment": "..." }}
"""

def grade_relevance(query, retrieved_docs):
    key = {"type":"isrel","q":query,"ids":[d["id"] for d in retrieved_docs]}
    cached = get_cached(key)
    if cached:
        return cached
    prompt = isrel_prompt(query, retrieved_docs)
    resp = generate_text(prompt, max_output_tokens=300)
    parsed = _extract_json(resp["text"]) or {"is_relevant": True, "reason": resp["text"], "score": 1.0}
    res = {"is_relevant": bool(parsed.get("is_relevant", True)), "relevance_score": float(parsed.get("score", 1.0)), "reason": parsed.get("reason", "")}
    set_cached(key, res)
    return res

def grade_grounding(answer, retrieved_docs):
    key = {"type":"issup","answer_excerpt":answer[:1500],"ids":[d["id"] for d in retrieved_docs]}
    cached = get_cached(key)
    if cached:
        return cached
    prompt = issup_prompt(answer, retrieved_docs)
    resp = generate_text(prompt, max_output_tokens=1000)
    parsed = _extract_json(resp["text"]) or {"fully_supported": True, "unsupported_claims": [], "contradictions": [], "missing_items": [], "comment": resp["text"]}
    res = {
        "fully_supported": bool(parsed.get("fully_supported", True)),
        "unsupported_claims": parsed.get("unsupported_claims", []),
        "contradictions": parsed.get("contradictions", []),
        "missing_items": parsed.get("missing_items", []),
        "comment": parsed.get("comment","")
    }
    set_cached(key, res)
    return res

def grade_usefulness(answer, query):
    key = {"type":"isuse","a":answer[:1500],"q":query}
    cached = get_cached(key)
    if cached:
        return cached
    prompt = isuse_prompt(answer, query)
    resp = generate_text(prompt, max_output_tokens=300)
    parsed = _extract_json(resp["text"]) or {"useful": True, "score": 1.0, "comment": resp["text"]}
    res = {"useful": bool(parsed.get("useful", True)), "score": float(parsed.get("score", 1.0)), "comment": parsed.get("comment","")}
    set_cached(key, res)
    return res
