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

def load_all_plugins(plugins_dir: str = PLUGINS_DIR, disabled: list[str] | None = None) -> tuple[dict, list[dict]]:
    global _REGISTRY, _ERRORS
    _REGISTRY = []
    _ERRORS = []
    all_actions = {}
    disabled = disabled or []

    for path, pid in _discover_files(plugins_dir):
        if pid in disabled or f"{pid}.py" in disabled:
            continue
        try:
            actions, info = _load_file(path, pid)
            all_actions.update(actions)
            _REGISTRY.append(info)
        except Exception as e:
            _ERRORS.append({"id": pid, "path": path, "error": str(e)})

    return all_actions, _REGISTRY

def format_plugins_for_prompt(registry: list[dict]) -> str:
    if not registry:
        return ""
    lines = ["PLUGINS (additional actions available):"]
    for p in registry:
        lines.append(f"  - {p['name']} v{p['version']} ({p['id']}): {p['description']}")
    return "\n".join(lines)
