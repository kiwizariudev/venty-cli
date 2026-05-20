import subprocess
import platform

PLUGIN_NAME    = "Media & Display"
PLUGIN_VERSION = "1.0.0"

_OS = platform.system()

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def _ok(text):
    return type("R", (), {"stdout": str(text)})()

ACTIONS = {
    "media_play_pause": {
        "description": "Play or pause media (keyboard shortcut)",
        "execute": lambda a: _run('powershell (New-Object -ComObject WScript.Shell).SendKeys([char]179)') if _OS == "Windows" else _run("playerctl play-pause"),
    },
    "media_next": {
        "description": "Skip to next track",
        "execute": lambda a: _run('powershell (New-Object -ComObject WScript.Shell).SendKeys([char]176)') if _OS == "Windows" else _run("playerctl next"),
    },
    "media_prev": {
        "description": "Go to previous track",
        "execute": lambda a: _run('powershell (New-Object -ComObject WScript.Shell).SendKeys([char]177)') if _OS == "Windows" else _run("playerctl previous"),
    },
    "media_volume_up": {
        "description": "Increase media volume",
        "execute": lambda a: _run('powershell (New-Object -ComObject WScript.Shell).SendKeys([char]175)') if _OS == "Windows" else _run("amixer -q sset Master 5%+"),
    },
    "media_volume_down": {
        "description": "Decrease media volume",
        "execute": lambda a: _run('powershell (New-Object -ComObject WScript.Shell).SendKeys([char]174)') if _OS == "Windows" else _run("amixer -q sset Master 5%-"),
    },
    "display_brightness_up": {
        "description": "Increase screen brightness (Windows)",
        "execute": lambda a: _run("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [math]::min(100, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness + 10))"),
    },
    "display_brightness_down": {
        "description": "Decrease screen brightness (Windows)",
        "execute": lambda a: _run("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [math]::max(0, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness - 10))"),
    },
    "display_get_brightness": {
        "description": "Get current screen brightness",
        "execute": lambda a: _run("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"),
    },
    "display_resolution": {
        "description": "Get screen resolution",
        "execute": lambda a: _run("powershell (Get-WmiObject Win32_VideoController | Select-Object CurrentHorizontalResolution,CurrentVerticalResolution | Format-List)"),
    },
}
