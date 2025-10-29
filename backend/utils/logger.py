import json, os
from datetime import datetime
from config import settings

os.makedirs(os.path.dirname(settings.TRACE_LOG), exist_ok=True)

def log_trace(trace: dict):
    record = {"timestamp": datetime.utcnow().isoformat() + "Z", **trace}
    with open(settings.TRACE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
