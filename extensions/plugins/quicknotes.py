import os
import json
import datetime

PLUGIN_NAME    = "Quick Notes"
PLUGIN_VERSION = "1.0.0"

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTES_FILE = os.path.join(BASE_DIR, "data", "memory", "quicknotes.json")

def _ok(text):
    return type("R", (), {"stdout": str(text)})()

def _load():
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save(notes):
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

def _add(text):
    notes = _load()
    notes.append({"id": len(notes) + 1, "text": text, "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    _save(notes)
    return _ok(f"Note #{len(notes)} saved: {text}")

def _list_notes():
    notes = _load()
    if not notes:
        return _ok("No quick notes yet.")
    lines = [f"#{n['id']} [{n['created']}] {n['text']}" for n in notes]
    return _ok("\n".join(lines))

def _delete(note_id):
    notes = _load()
    before = len(notes)
    notes = [n for n in notes if str(n["id"]) != str(note_id)]
    _save(notes)
    return _ok(f"Deleted {before - len(notes)} note(s).")

def _clear():
    _save([])
    return _ok("All quick notes cleared.")

ACTIONS = {
    "note_add": {
        "description": "Add a quick note, args = [text]",
        "execute": lambda a: _add(a[0]),
    },
    "note_list": {
        "description": "List all quick notes",
        "execute": lambda a: _list_notes(),
    },
    "note_delete": {
        "description": "Delete a quick note by ID, args = [id]",
        "execute": lambda a: _delete(a[0]),
    },
    "note_clear": {
        "description": "Clear all quick notes",
        "execute": lambda a: _clear(),
    },
}
