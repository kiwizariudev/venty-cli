import subprocess
import platform
import os
import datetime

PLUGIN_NAME    = "System Info"
PLUGIN_VERSION = "1.0.0"

_OS = platform.system()

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def _ok(text):
    return type("R", (), {"stdout": str(text)})()

def _full_sysinfo():
    lines = [
        f"OS       : {platform.system()} {platform.release()} {platform.version()}",
        f"Machine  : {platform.machine()}",
        f"Hostname : {platform.node()}",
        f"Python   : {platform.python_version()}",
        f"CPU      : {platform.processor()}",
        f"Time     : {datetime.datetime.now().strftime('%A %d %B %Y  %H:%M:%S')}",
    ]
    return _ok("\n".join(lines))

ACTIONS = {
    "sysinfo_full": {
        "description": "Get full system info summary",
        "execute": lambda a: _full_sysinfo(),
    },
    "sysinfo_cpu_cores": {
        "description": "Get CPU core count",
        "execute": lambda a: _ok(f"CPU cores: {os.cpu_count()}"),
    },
    "sysinfo_python": {
        "description": "Get Python version and path",
        "execute": lambda a: _ok(f"Python {platform.python_version()} at {os.sys.executable}"),
    },
    "sysinfo_env_path": {
        "description": "Show PATH environment variable",
        "execute": lambda a: _ok(os.environ.get("PATH", "").replace(";", "\n")),
    },
    "sysinfo_temp_dir": {
        "description": "Get system temp directory",
        "execute": lambda a: _ok(os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"),
    },
    "sysinfo_user": {
        "description": "Get current username",
        "execute": lambda a: _ok(os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"),
    },
    "sysinfo_home": {
        "description": "Get home directory",
        "execute": lambda a: _ok(os.path.expanduser("~")),
    },
    "sysinfo_drives": {
        "description": "List available drives (Windows)",
        "execute": lambda a: _run("wmic logicaldisk get caption,description,freespace,size") if _OS == "Windows" else _run("df -h"),
    },
    "sysinfo_startup_time": {
        "description": "Get system last boot time",
        "execute": lambda a: _run("powershell (gcim Win32_OperatingSystem).LastBootUpTime") if _OS == "Windows" else _run("uptime -s"),
    },
}
