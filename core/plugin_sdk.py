"""
core/plugin_sdk.py — helpers for writing Venty plugins.

Usage in a plugin file:
    from core.plugin_sdk import Plugin, ok, fail, result

    class MyPlugin(Plugin):
        NAME    = "My Plugin"
        VERSION = "1.0.0"

    def ok(msg):   return type("R", (), {"stdout": str(msg)})()
    def fail(msg): raise RuntimeError(msg)
"""


def ok(msg: str = "done"):
    """Return a stdout-compatible result object."""
    return type("R", (), {"stdout": str(msg)})()


def fail(msg: str):
    """Raise a RuntimeError to signal action failure."""
    raise RuntimeError(msg)


def result(value):
    """Wrap any value as a stdout result."""
    return type("R", (), {"stdout": str(value)})()


class Plugin:
    """Base class for structured plugins (optional — dict ACTIONS also works)."""
    NAME    = "Unnamed Plugin"
    VERSION = "1.0.0"
    ACTIONS: dict = {}

    @classmethod
    def register(cls) -> dict:
        return cls.ACTIONS
