"""
core/paths.py — centralised path definitions for the whole project.
"""
import os

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── data dirs ────────────────────────────────────────────────
DATA_DIR      = os.path.join(BASE_DIR, "data")
CONFIG_DIR    = os.path.join(DATA_DIR, "config")
MEMORY_DIR    = os.path.join(DATA_DIR, "memory")
LOGS_DIR      = os.path.join(DATA_DIR, "logs")
CACHE_DIR     = os.path.join(DATA_DIR, "cache")
SANDBOX_DIR   = os.path.join(DATA_DIR, "sandbox")
RUNTIME_DIR   = os.path.join(DATA_DIR, "runtime")
SCHEDULER_DIR = os.path.join(DATA_DIR, "scheduler")

# ── extensions ───────────────────────────────────────────────
EXT_DIR       = os.path.join(BASE_DIR, "extensions")
PLUGINS_DIR   = os.path.join(EXT_DIR, "plugins")
MODULES_DIR   = os.path.join(EXT_DIR, "modules")

# ── files ────────────────────────────────────────────────────
CONFIG_PATH   = os.path.join(CONFIG_DIR,  "settings.json")
APIS_PATH     = os.path.join(CONFIG_DIR,  "apis.json")
ALIASES_PATH  = os.path.join(CONFIG_DIR,  "aliases.json")
THEMES_PATH   = os.path.join(CONFIG_DIR,  "themes.json")
KEYBINDS_PATH = os.path.join(CONFIG_DIR,  "keybinds.json")
HISTORY_PATH  = os.path.join(MEMORY_DIR,  "history.json")
NOTES_PATH    = os.path.join(MEMORY_DIR,  "notes.json")
LOG_PATH      = os.path.join(LOGS_DIR,    "venty.log")
ERROR_PATH    = os.path.join(LOGS_DIR,    "errors.log")
SESSION_PATH  = os.path.join(LOGS_DIR,    "sessions.log")
CACHE_PATH    = os.path.join(CACHE_DIR,   "actions.json")
JOBS_PATH     = os.path.join(SCHEDULER_DIR, "jobs.json")

_ALL_DIRS = [
    CONFIG_DIR, MEMORY_DIR, LOGS_DIR, CACHE_DIR,
    SANDBOX_DIR, RUNTIME_DIR, SCHEDULER_DIR,
    EXT_DIR, PLUGINS_DIR, MODULES_DIR,
]

# alias expected by core/__init__.py
DIRS = _ALL_DIRS


def ensure_dirs() -> None:
    for d in _ALL_DIRS:
        os.makedirs(d, exist_ok=True)


def default_working_dir() -> str:
    return SANDBOX_DIR
