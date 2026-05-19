"""
Clipboard Plus — read/write clipboard (Windows).
"""
import subprocess

from core.plugin_sdk import Plugin, ok, fail

plugin = Plugin(
    id="clipboard_plus",
    name="Clipboard Plus",
    version="1.0.0",
    description="Read and write the system clipboard",
    author="Venty",
)


@plugin.action("clip_read", "Read text from clipboard, args = []")
def clip_read(args):
    r = subprocess.run(
        "powershell -Command Get-Clipboard",
        shell=True, capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        return fail(r.stderr.strip() or "clipboard read failed")
    text = (r.stdout or "").strip()
    return ok(text if text else "(clipboard empty)")


@plugin.action("clip_write", "Write text to clipboard, args = [text]")
def clip_write(args):
    if not args:
        return fail("text required")
    text = args[0].replace("'", "''")
    r = subprocess.run(
        f"powershell -Command Set-Clipboard -Value '{text}'",
        shell=True, capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        return fail(r.stderr.strip() or "clipboard write failed")
    return ok("copied to clipboard")


ACTIONS = plugin.actions
PLUGIN_META = plugin.meta
