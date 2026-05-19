"""
Copy this file to my_plugin.py and edit it.
Do not enable _template.py (starts with _ — skipped by loader).
"""
from core.plugin_sdk import Plugin, ok

plugin = Plugin(
    id="my_plugin",
    name="My Plugin",
    version="1.0.0",
    description="Describe what your plugin does",
    author="Your Name",
)


@plugin.action("my_hello", "Say hello, args = [name]")
def my_hello(args):
    name = args[0] if args else "world"
    return ok(f"Hello, {name}!")


ACTIONS = plugin.actions
PLUGIN_META = plugin.meta
