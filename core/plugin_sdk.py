from __future__ import annotations
from typing import Any, Callable

def result(text: str):
    return type("R", (), {"stdout": str(text)})()

def ok(text: str):
    return result(text)

def fail(text: str):
    return result(f"Error: {text}")

class Plugin:
    def __init__(
        self,
        id: str,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
    ):
        self.id = id
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self._actions: dict[str, dict] = {}

    @property
    def meta(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "actions": list(self._actions.keys()),
        }

    @property
    def actions(self) -> dict:
        return dict(self._actions)

    def action(self, name: str, description: str):
        def decorator(fn: Callable[[list], Any]):
            def execute(args: list):
                try:
                    out = fn(args or [])
                    if out is None:
                        return ok("done")
                    if hasattr(out, "stdout"):
                        return out
                    return ok(out)
                except IndexError:
                    return fail(f"{name} missing required arguments")
                except Exception as e:
                    return fail(str(e))

            self._actions[name] = {
                "description": description,
                "execute": execute,
                "plugin": self.id,
            }
            return fn
        return decorator

    def register(self, name: str, description: str, fn: Callable[[list], Any]):
        self.action(name, description)(fn)
