import subprocess

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

ACTIONS = {
    "os_copy_to_clipboard": {
        "description": "Copy text to clipboard, args = [text]",
        "execute": lambda a: subprocess.run(["clip"], input=a[0].encode(), capture_output=True),
    },
    "os_get_clipboard": {
        "description": "Get clipboard content",
        "execute": lambda a: _run("powershell Get-Clipboard"),
    },
    "os_clear_clipboard": {
        "description": "Clear clipboard",
        "execute": lambda a: _run("powershell Set-Clipboard -Value $null"),
    },
}
