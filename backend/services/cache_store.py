import os, json, hashlib
from config import settings

CACHE_FILE = "./data/cache_store.json"
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

try:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        _cache = json.load(f)
except Exception:
    _cache = {}

def _key(obj):
    s = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def get_cached(obj):
    if not _cache:
        return None
    k = _key(obj)
    return _cache.get(k)

def set_cached(obj, value):
    k = _key(obj)
    _cache[k] = value
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False, indent=2)
