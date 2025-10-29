import re

def clean_text(t: str) -> str:
    if not t:
        return ""
    # normalize whitespace, strip weird characters
    t = re.sub(r"\s+", " ", t).strip()
    return t
