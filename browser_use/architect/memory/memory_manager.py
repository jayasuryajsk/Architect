import json
from datetime import datetime
import os

MEMORY_PATH = "browser_use/architect/memory/memory.json"

def _load_memory():
    if not os.path.exists(MEMORY_PATH):
        return {"logs": [], "tasks": []}
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)

def _save_memory(memory):
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def log_message(agent, message):
    memory = _load_memory()
    memory["logs"].append({
        "agent": agent,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    })
    _save_memory(memory)

def save_task_result(agent, task_id, result):
    memory = _load_memory()
    memory["tasks"].append({
        "agent": agent,
        "task_id": task_id,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    _save_memory(memory)