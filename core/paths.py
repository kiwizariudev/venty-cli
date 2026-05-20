import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC_CORE     = os.path.join(BASE_DIR, "core")
SRC_ACTIONS  = os.path.join(BASE_DIR, "actions")
SRC_UI       = os.path.join(BASE_DIR, "ui")

DATA_DIR     = os.path.join(BASE_DIR, "data")
CONFIG_DIR   = os.path.join(DATA_DIR, "config")
SANDBOX_DIR  = os.path.join(DATA_DIR, "sandbox")
RUNTIME_DIR  = os.path.join(DATA_DIR, "runtime")
CACHE_DIR    = os.path.join(DATA_DIR, "cache")
MEMORY_DIR   = os.path.join(DATA_DIR, "memory")
LOGS_DIR     = os.path.join(DATA_DIR, "logs")
SCHEDULER_DIR = os.path.join(DATA_DIR, "scheduler")

CONFIG_PATH   = os.path.join(CONFIG_DIR, "settings.json")
APIS_PATH     = os.path.join(CONFIG_DIR, "apis.json")
KEYBINDS_PATH = os.path.join(CONFIG_DIR, "keybinds.json")
THEMES_PATH   = os.path.join(CONFIG_DIR, "themes.json")
ALIASES_PATH  = os.path.join(CONFIG_DIR, "aliases.json")
HISTORY_PATH  = os.path.join(MEMORY_DIR, "history.json")
NOTES_PATH    = os.path.join(MEMORY_DIR, "notes.json")
CACHE_PATH    = os.path.join(CACHE_DIR, "actions.json")
LOG_PATH      = os.path.join(LOGS_DIR, "venty.log")
ERROR_PATH    = os.path.join(LOGS_DIR, "errors.log")
SESSION_PATH  = os.path.join(LOGS_DIR, "sessions.log")
JOBS_PATH     = os.path.join(SCHEDULER_DIR, "jobs.json")

EXTENSIONS_DIR = os.path.join(BASE_DIR, "extensions")
PLUGINS_DIR    = os.path.join(EXTENSIONS_DIR, "plugins")
MODULES_DIR    = os.path.join(EXTENSIONS_DIR, "modules")
API_DIR        = os.path.join(EXTENSIONS_DIR, "api")
BRIDGE_DIR     = os.path.join(EXTENSIONS_DIR, "bridge")
ASSETS_DIR     = os.path.join(BASE_DIR, "assets")
DOCS_DIR       = os.path.join(BASE_DIR, "docs")
SCRIPTS_DIR    = os.path.join(BASE_DIR, "scripts")
BUILD_DIR      = os.path.join(BASE_DIR, "build")
DIST_DIR       = os.path.join(BASE_DIR, "dist")

_LEGACY_DATA_DIRS = ("config", "sandbox", "runtime", "cache", "memory", "logs", "scheduler")
_LEGACY_EXT_DIRS  = ("plugins",)

DIRS = {
    "core":        "engine — agent, executor, config, memory, tasks",
    "actions":     "system actions (files, browser, shell, git, …)",
    "ui":          "terminal colors and command helpers",
    "data":        "all mutable state",
    "extensions":  "plugins, optional modules, future api/bridge",
    "docs":        "documentation",
    "assets":      "static files",
    "scripts":     "launch scripts",
    "build":       "PyInstaller build output",
    "dist":        "packaged .exe",
}

def _migrate_legacy() -> None:
    for name in _LEGACY_DATA_DIRS:
        old = os.path.join(BASE_DIR, name)
        new = os.path.join(DATA_DIR, name)
        if os.path.isdir(old) and not os.path.isdir(new):
            os.makedirs(DATA_DIR, exist_ok=True)
            shutil.move(old, new)
        elif os.path.isdir(old) and os.path.isdir(new):
            for item in os.listdir(old):
                src = os.path.join(old, item)
                dst = os.path.join(new, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            try:
                if not os.listdir(old):
                    os.rmdir(old)
            except OSError:
                pass

    old_plugins = os.path.join(BASE_DIR, "plugins")
    if os.path.isdir(old_plugins):
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        for item in os.listdir(old_plugins):
            src = os.path.join(old_plugins, item)
            dst = os.path.join(PLUGINS_DIR, item)
            if not os.path.exists(dst):
                shutil.move(src, dst)
        try:
            if not os.listdir(old_plugins):
                os.rmdir(old_plugins)
        except OSError:
            pass

def ensure_dirs() -> None:
    _migrate_legacy()
    for d in (DATA_DIR, CONFIG_DIR, SANDBOX_DIR, RUNTIME_DIR, CACHE_DIR,
              MEMORY_DIR, LOGS_DIR, SCHEDULER_DIR, EXTENSIONS_DIR,
              PLUGINS_DIR, MODULES_DIR, API_DIR, BRIDGE_DIR, ASSETS_DIR,
              DOCS_DIR, SCRIPTS_DIR):
        os.makedirs(d, exist_ok=True)

def default_working_dir() -> str:
    return SANDBOX_DIR
