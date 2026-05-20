import os
import json

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config", "settings.json")
APIS_PATH   = os.path.join(BASE_DIR, "data", "config", "apis.json")


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


def _load_cfg():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cfg(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def _get_setting(key):
    val = _load_cfg().get(key, "NOT SET")
    return _stdout(f"{key} = {val}")


def _set_setting(key, value):
    cfg = _load_cfg()
    if isinstance(value, str):
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
    cfg[key] = value
    _save_cfg(cfg)
    return _stdout(f"set {key} = {value}")


def _list_settings():
    cfg = _load_cfg()
    lines = [f"{k:<30} {'***' if k == 'api_key' else str(v)}" for k, v in cfg.items()]
    return _stdout("\n".join(lines))


def _list_providers():
    if not os.path.exists(APIS_PATH):
        return _stdout("No providers configured. Run setup.py.")
    try:
        with open(APIS_PATH, "r") as f:
            apis = json.load(f)
        lines = []
        for a in apis:
            key = a.get("key", "")
            masked = key[:6] + "***" + key[-4:] if len(key) > 10 else "***"
            lines.append(f"{a['name']:<15} {masked}  models: {', '.join(a.get('models', []))}")
        return _stdout("\n".join(lines))
    except Exception as e:
        return _stdout(f"Error: {e}")


def _switch_provider(name):
    if not os.path.exists(APIS_PATH):
        return _stdout("No providers configured.")
    try:
        with open(APIS_PATH, "r") as f:
            apis = json.load(f)
        match = next((a for a in apis if a["name"].lower() == name.lower()), None)
        if not match:
            return _stdout(f"Provider '{name}' not found. Available: {', '.join(a['name'] for a in apis)}")
        cfg = _load_cfg()
        cfg["api_key"]  = match["key"]
        cfg["url"]      = match["url"]
        cfg["provider"] = match["name"]
        if match.get("models"):
            cfg["model"] = match["models"][0]
        _save_cfg(cfg)
        return _stdout(f"Switched to {match['name']} — model: {cfg['model']}")
    except Exception as e:
        return _stdout(f"Error: {e}")


def _reset_config():
    defaults = {
        "api_key": "", "model": "", "display_name": "",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "provider": "", "max_loop": 20, "max_tokens": 700,
        "temperature": 0.2, "save_history": True,
        "max_history_entries": 100, "max_session_turns": 40,
        "timeout": 60, "show_output": True, "confirm_dangerous": True,
        "working_dir": os.path.join(BASE_DIR, "data", "sandbox"),
        "theme": "default", "stream": True,
    }
    _save_cfg(defaults)
    return _stdout("Config reset to defaults.")


ACTIONS = {
    "cfg_get":             {"description": "Get a config value, args = [key]",                        "execute": lambda a: _get_setting(a[0])},
    "cfg_set":             {"description": "Set a config value, args = [key, value]",                 "execute": lambda a: _set_setting(a[0], a[1] if len(a) > 1 else "")},
    "cfg_list":            {"description": "List all config settings",                                "execute": lambda a: _list_settings()},
    "cfg_list_providers":  {"description": "List all configured API providers",                       "execute": lambda a: _list_providers()},
    "cfg_switch_provider": {"description": "Switch active provider, args = [provider_name]",          "execute": lambda a: _switch_provider(a[0])},
    "cfg_set_model":       {"description": "Set the active model, args = [model_name]",               "execute": lambda a: _set_setting("model", a[0])},
    "cfg_set_working_dir": {"description": "Set working directory, args = [path]",                    "execute": lambda a: _set_setting("working_dir", a[0])},
    "cfg_reset":           {"description": "Reset config to defaults",                                "execute": lambda a: _reset_config()},
    "cfg_set_theme":       {"description": "Set UI theme, args = [default|dark|matrix|ocean]",        "execute": lambda a: _set_setting("theme", a[0])},
    "cfg_set_temperature": {"description": "Set model temperature 0.0-1.0, args = [value]",           "execute": lambda a: _set_setting("temperature", a[0])},
    "cfg_set_max_tokens":  {"description": "Set max tokens, args = [value]",                          "execute": lambda a: _set_setting("max_tokens", a[0])},
    "cfg_toggle_stream":   {"description": "Toggle streaming on/off",                                 "execute": lambda a: _set_setting("stream", not _load_cfg().get("stream", True))},
    "cfg_toggle_output":   {"description": "Toggle show_output on/off",                               "execute": lambda a: _set_setting("show_output", not _load_cfg().get("show_output", True))},
}
