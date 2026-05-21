import os
import subprocess
import platform

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_DIR  = os.path.join(BASE_DIR, "engine")
_EXE        = os.path.join(ENGINE_DIR, "venty_engine.exe" if platform.system() == "Windows" else "venty_engine")
_AVAILABLE  = os.path.isfile(_EXE)


def _ok(text):
    return type("R", (), {"stdout": str(text)})()


def _call(*args) -> str:
    if not _AVAILABLE:
        return "venty_engine not built — run engine/build.bat (Windows) or engine/build.sh (Linux/macOS)"
    try:
        r = subprocess.run([_EXE] + list(args), capture_output=True, text=True, timeout=30)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f"engine error: {e}"


def is_available() -> bool:
    return _AVAILABLE


def build_engine() -> str:
    if platform.system() == "Windows":
        bat = os.path.join(ENGINE_DIR, "build.bat")
        r = subprocess.run(bat, shell=True, capture_output=True, text=True, cwd=ENGINE_DIR)
    else:
        sh = os.path.join(ENGINE_DIR, "build.sh")
        r = subprocess.run(["bash", sh], capture_output=True, text=True, cwd=ENGINE_DIR)
    global _AVAILABLE
    _AVAILABLE = os.path.isfile(_EXE)
    return (r.stdout + r.stderr).strip()


ACTIONS = {
    "engine_build":    {"description": "Build the C++ venty_engine binary",                                   "execute": lambda a: _ok(build_engine())},
    "engine_stat":     {"description": "Fast file/dir info via C++ engine, args = [path]",                    "execute": lambda a: _ok(_call("stat", a[0]))},
    "engine_hash":     {"description": "Fast SHA-256 hash via C++ engine, args = [path]",                     "execute": lambda a: _ok(_call("hash", a[0]))},
    "engine_count":    {"description": "Count files via C++ engine, args = [path] or [path, .ext]",           "execute": lambda a: _ok(_call("count", a[0], a[1] if len(a)>1 else ""))},
    "engine_lines":    {"description": "Count lines of code via C++ engine, args = [path] or [path, .ext]",   "execute": lambda a: _ok(_call("lines", a[0], a[1] if len(a)>1 else ""))},
    "engine_size":     {"description": "Get directory total size via C++ engine, args = [path]",              "execute": lambda a: _ok(_call("size", a[0]))},
    "engine_find":     {"description": "Find files by name pattern via C++ engine, args = [path, pattern]",   "execute": lambda a: _ok(_call("find", a[0], a[1]))},
    "engine_newer":    {"description": "Files modified in last N seconds, args = [path, seconds]",            "execute": lambda a: _ok(_call("newer", a[0], a[1]))},
    "engine_dupes":    {"description": "Find duplicate files by size via C++ engine, args = [path]",          "execute": lambda a: _ok(_call("dupes", a[0]))},
    "engine_tree":     {"description": "Fast directory tree via C++ engine, args = [path] or [path, depth]",  "execute": lambda a: _ok(_call("tree", a[0], a[1] if len(a)>1 else "3"))},
    "engine_status":   {"description": "Check if C++ engine is built and available",                          "execute": lambda a: _ok(f"venty_engine: {'available at ' + _EXE if _AVAILABLE else 'not built — run engine_build'}")},
}
