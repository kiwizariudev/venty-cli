"""
core/plugins.py — discover, validate, and load plugins from extensions/plugins/
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from typing import Any

from core.paths import PLUGINS_DIR, CACHE_DIR

_REGISTRY: list[dict] = []
_ERRORS: list[dict] = []


def get_registry() -> list[dict]:
    return list(_REGISTRY)


def get_load_errors() -> list[dict]:
    return list(_ERRORS)


def _validate_actions(actions: Any, source: str) -> dict | None:
    if not isinstance(actions, dict) or not actions:
        return None
    clean = {}
    for name, spec in actions.items():
        if not isinstance(name, str) or not name.replace("_", "").isalnum():
            continue
        if not isinstance(spec, dict):
            continue
        desc = spec.get("description", "")
        exe = spec.get("execute")
        if not callable(exe):
            continue
        clean[name] = {
            "description": str(desc),
            "execute": exe,
            "plugin": spec.get("plugin", source),
        }
    return clean or None


def _load_module(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_file(path: str, plugin_id: str) -> tuple[dict, dict | None]:
    mod = _load_module(path, f"venty_plugin.{plugin_id}")
    actions = _validate_actions(getattr(mod, "ACTIONS", None), plugin_id)
    if not actions:
        raise ValueError("no valid ACTIONS dict")

    meta = getattr(mod, "PLUGIN_META", None) or getattr(mod, "PLUGIN", None) or {}
    if not isinstance(meta, dict):
        meta = {}
    info = {
        "id": meta.get("id", plugin_id),
        "name": meta.get("name", plugin_id),
        "version": meta.get("version", "1.0.0"),
        "description": meta.get("description", ""),
        "author": meta.get("author", ""),
        "path": path,
        "actions": list(actions.keys()),
        "enabled": True,
    }
    for k, v in actions.items():
        v["plugin"] = info["id"]
    return actions, info


def _discover_files(plugins_dir: str) -> list[tuple[str, str]]:
    """Return list of (path, plugin_id)."""
    found: list[tuple[str, str]] = []
    if not os.path.isdir(plugins_dir):
        return found

    skip = {"_sdk.py", "_template.py", "__init__.py"}

    for fname in sorted(os.listdir(plugins_dir)):
        if fname.startswith("_") or fname in skip:
            continue
        full = os.path.join(plugins_dir, fname)
        if fname.endswith(".py") and os.path.isfile(full):
            found.append((full, fname[:-3]))
        elif os.path.isdir(full):
            for candidate in ("plugin.py", "__init__.py"):
                p = os.path.join(full, candidate)
                if os.path.isfile(p):
                    found.append((p, os.path.basename(full)))
                    break
    return found


def load_all_plugins(plugins_dir: str | None = None) -> tuple[dict, list[dict]]:
    """
    Load every plugin. Returns (actions_dict, registry_list).
  """
    global _REGISTRY, _ERRORS
    plugins_dir = plugins_dir or PLUGINS_DIR
    merged: dict = {}
    registry: list[dict] = []
    errors: list[dict] = []

    # ensure project root importable inside plugins
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)

    for path, plugin_id in _discover_files(plugins_dir):
        try:
            actions, info = _load_file(path, plugin_id)
            overlap = set(merged) & set(actions)
            if overlap:
                raise ValueError(f"action names already exist: {', '.join(sorted(overlap)[:5])}")
            merged.update(actions)
            registry.append(info)
        except Exception as e:
            errors.append({"id": plugin_id, "path": path, "error": str(e)})

    _REGISTRY = registry
    _ERRORS = errors
    _save_registry_cache(registry, errors)
    return merged, registry


def _save_registry_cache(registry: list, errors: list) -> None:
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        path = os.path.join(CACHE_DIR, "plugins_registry.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"plugins": registry, "errors": errors}, f, indent=2)
    except Exception:
        pass


def format_plugins_for_prompt(registry: list[dict] | None = None) -> str:
    """Short block injected into system prompt."""
    registry = registry or _REGISTRY
    if not registry:
        return ""
    lines = ["INSTALLED PLUGINS (use these action names — never cannot_do for browser/web):"]
    for p in registry:
        acts = ", ".join(p.get("actions", [])[:8])
        if len(p.get("actions", [])) > 8:
            acts += ", …"
        lines.append(f"- {p['name']} ({p['id']}): {acts}")
    lines.append(
        "For 'open website' / 'go to google' / browser: use web_open_chrome, web_open_url, "
        "os_open_chrome, or web_search — NOT cannot_do."
    )
    return "\n".join(lines)
