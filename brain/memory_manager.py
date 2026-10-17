import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN_PATH = os.path.join(BASE_DIR, "jarvis_brain.json")

def _load_brain():
    if not os.path.exists(BRAIN_PATH):
        return {
            "user_preferences": [],
            "long_term_facts": [],
            "short_term_history": []
        }
    try:
        with open(BRAIN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "user_preferences": [],
            "long_term_facts": [],
            "short_term_history": []
        }

def _save_brain(brain):
    try:
        with open(BRAIN_PATH, "w", encoding="utf-8") as f:
            json.dump(brain, f, indent=4)
    except Exception as e:
        print(f"[Memory Error] Saving failed: {e}")

def add_memory(category, content):
    brain = _load_brain()
    cat_key = "user_preferences" if category == "user_preferences" else "long_term_facts"
    if content not in brain[cat_key]:
        brain[cat_key].append(content)
        _save_brain(brain)

def add_history(role, text):
    brain = _load_brain()
    brain["short_term_history"].append({"role": role, "text": text})
    if len(brain["short_term_history"]) > 20:
        brain["short_term_history"] = brain["short_term_history"][-20:]
    _save_brain(brain)

def get_history():
    return _load_brain().get("short_term_history", [])

def get_context_string():
    brain = _load_brain()
    ctx = ""
    prefs = brain.get("user_preferences", [])
    if prefs:
        ctx += "--- USER PREFERENCES & IDENTITY ---\n"
        for p in prefs:
            ctx += f"- {p}\n"
        ctx += "\n"
        
    facts = brain.get("long_term_facts", [])
    if facts:
        ctx += "--- LEARNED FACTS ---\n"
        for f in facts:
            ctx += f"- {f}\n"
        ctx += "\n"
    return ctx

def clear_history():
    brain = _load_brain()
    brain["short_term_history"] = []
    _save_brain(brain)
