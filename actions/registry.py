"""
actions/registry.py — Windows registry operations
"""
import subprocess


def _run(args):
    return subprocess.run(args, capture_output=True, text=True)


ACTIONS = {
    "os_reg_read": {
        "description": "Read registry key, args = [key_path, value_name]",
        "execute": lambda a: _run(["reg", "query", a[0], "/v", a[1]]),
    },
    "os_reg_write": {
        "description": "Write registry string value, args = [key_path, value_name, data]",
        "execute": lambda a: _run(["reg", "add", a[0], "/v", a[1], "/t", "REG_SZ", "/d", a[2], "/f"]),
    },
    "os_reg_delete": {
        "description": "Delete registry value, args = [key_path, value_name]",
        "execute": lambda a: _run(["reg", "delete", a[0], "/v", a[1], "/f"]),
    },
    "os_reg_export": {
        "description": "Export registry key to file, args = [key_path, output_file]",
        "execute": lambda a: _run(["reg", "export", a[0], a[1], "/y"]),
    },
}
