def _ok(text):
    return type("R", (), {"stdout": str(text)})()

def _remember(args):
    try:
        from core.memory import remember
        return _ok(remember(args[0], args[1] if len(args) > 1 else "facts"))
    except Exception as e:
        return _ok(f"memory error: {e}")

def _forget(args):
    try:
        from core.memory import forget
        return _ok(forget(args[0]))
    except Exception as e:
        return _ok(f"memory error: {e}")

def _list_notes(args):
    try:
        from core.memory import list_notes
        return _ok(list_notes())
    except Exception as e:
        return _ok(f"memory error: {e}")

def _clear_notes(args):
    try:
        from core.memory import clear_notes
        return _ok(clear_notes())
    except Exception as e:
        return _ok(f"memory error: {e}")

ACTIONS = {
    "loop_start":       {"description": "Repeat an action N times, args = [count, action_name, ...action_args]", "execute": lambda a: None},
    "cannot_do":        {"description": "Use when request is impossible, dangerous, or illegal",                  "execute": lambda a: None},
    "none":             {"description": "No action needed, just reply",                                           "execute": lambda a: None},
    "memory_remember":  {"description": "Save a fact/note to memory, args = [text] or [text, category]",         "execute": _remember},
    "memory_forget":    {"description": "Remove a note from memory, args = [text_to_match]",                     "execute": _forget},
    "memory_list":      {"description": "List all saved notes",                                                   "execute": _list_notes},
    "memory_clear":     {"description": "Clear all saved notes",                                                  "execute": _clear_notes},
}
