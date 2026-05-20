"""
core/plugins.py — plugin loader for extensions/plugins/*.py
Each plugin file must expose:
  PLUGIN_NAME    = "My Plugin"
  PLUGIN_VERSION = "1.0.0"
  ACTIONS        = { "action_name": {"description": "...", "execute": lambda a: ...} }
"""
import os
import importlib.util

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(BASE_DIR, "extensions", "plugins")

_registry: list[dict] = []
_errors:   list[str]  = []


def load_all_plugins(actions: dict) -> tuple[dict, list]:
    """Load all .py plugins from PLUGINS_DIR into actions dict. Returns (actions, errors)."""
    global _registry, _errors
    _registry.clear()
    _errors.clear()

    if not os.path.isdir(PLUGINS_DIR):
        return actions, []

    for fname in sorted(os.listdir(PLUGINS_DIR)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        path = os.path.join(PLUGINS_DIR, fname)
        try:
            spec   = importlib.util.spec_from_file_location(f"plugins.{fname[:-3]}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_actions = getattr(module, "ACTIONS", {})
            name    = getattr(module, "PLUGIN_NAME",    fname[:-3])
            version = getattr(module, "PLUGIN_VERSION", "1.0.0")
            actions.update(plugin_actions)
            _registry.append({"name": name, "version": version,
                               "file": fname, "actions": list(plugin_actions.keys())})
        except Exception as e:
            _errors.append(f"{fname}: {e}")

    return actions, _errors


def get_registry() -> list[dict]:
    return _registry


def get_load_errors() -> list[str]:
    return _errors


def format_plugins_for_prompt(actions: dict) -> str:
    if not _registry:
        return ""
    lines = ["PLUGINS:"]
    for p in _registry:
        lines.append(f"  {p['name']} v{p['version']}: {', '.join(p['actions'])}")
    return "\n".join(lines)
