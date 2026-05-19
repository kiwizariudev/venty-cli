"""Example optional module — not auto-loaded; import from plugins if needed."""


def greet(name: str = "world") -> str:
    return f"Hello, {name}!"
