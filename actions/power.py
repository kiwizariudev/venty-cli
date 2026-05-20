import subprocess

def _run(args):
    return subprocess.run(args, capture_output=True, text=True)

ACTIONS = {
    "os_volume_up": {
        "description": "Turn volume up",
        "execute": lambda a: _run(["nircmd", "changesysvolume", "5000"]),
    },
    "os_volume_down": {
        "description": "Turn volume down",
        "execute": lambda a: _run(["nircmd", "changesysvolume", "-5000"]),
    },
    "os_volume_mute": {
        "description": "Mute or unmute volume",
        "execute": lambda a: _run(["nircmd", "mutesysvolume", "2"]),
    },
    "os_volume_set": {
        "description": "Set volume 0-100, args = [level]",
        "execute": lambda a: _run(["nircmd", "setsysvolume", str(int(int(a[0]) * 655.35))]),
    },
    "os_volume_max": {
        "description": "Set volume to maximum",
        "execute": lambda a: _run(["nircmd", "setsysvolume", "65535"]),
    },
    "os_shutdown": {
        "description": "Shutdown computer, args = [delay seconds]",
        "execute": lambda a: _run(["shutdown", "/s", "/t", a[0] if a else "30"]),
    },
    "os_shutdown_now": {
        "description": "Shutdown immediately",
        "execute": lambda a: _run(["shutdown", "/s", "/t", "0"]),
    },
    "os_restart": {
        "description": "Restart computer, args = [delay seconds]",
        "execute": lambda a: _run(["shutdown", "/r", "/t", a[0] if a else "30"]),
    },
    "os_restart_now": {
        "description": "Restart immediately",
        "execute": lambda a: _run(["shutdown", "/r", "/t", "0"]),
    },
    "os_sleep": {
        "description": "Sleep the computer",
        "execute": lambda a: _run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]),
    },
    "os_hibernate": {
        "description": "Hibernate the computer",
        "execute": lambda a: _run(["shutdown", "/h"]),
    },
    "os_lock": {
        "description": "Lock the screen",
        "execute": lambda a: _run(["rundll32.exe", "user32.dll,LockWorkStation"]),
    },
    "os_cancel_shutdown": {
        "description": "Cancel pending shutdown",
        "execute": lambda a: _run(["shutdown", "/a"]),
    },
    "os_logoff": {
        "description": "Log off current user",
        "execute": lambda a: _run(["shutdown", "/l"]),
    },
}
