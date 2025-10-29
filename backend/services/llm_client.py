import os, json, requests
from config import settings

BASE_GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def _headers():
    k = settings.GEMINI_API_KEY
    if not k:
        raise ValueError("GEMINI_API_KEY not set in env")
    return {"Content-Type": "application/json", "x-goog-api-key": k}

def generate_text(prompt: str, model: str = None, max_output_tokens: int = 1024, temperature: float = 0.0):
    """
    Send prompt to Gemini 2.0 Flash model using the modern API format.
    """
    model = model or settings.GENERATION_MODEL
    url = BASE_GENERATE_URL.format(model=model)
    
    # Modern Gemini 2.0 API format
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
            "topP": 0.8,
            "topK": 10
        }
    }
    
    resp = requests.post(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    data = resp.json()
    
    # Parse modern response format
    text = ""
    try:
        candidates = data.get("candidates", [])
        if candidates:
            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            if parts:
                text = parts[0].get("text", "")
    except Exception as e:
        print(f"Error parsing response: {e}")
        text = json.dumps(data)
    
    return {"text": text, "raw": data}
