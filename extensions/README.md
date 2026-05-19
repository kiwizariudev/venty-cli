# extensions/

Optional add-ons. Drop files here to extend Venty without editing core code.

| Subfolder | Purpose |
|-----------|---------|
| `plugins/` | `.py` files with an `ACTIONS = {...}` dict (auto-loaded) |
| `modules/` | Optional Python helpers (import manually or from plugins) |
| `api/` | Reserved — future HTTP API |
| `bridge/` | Reserved — future Discord / webhook bridge |

See `plugins/example_echo.py` for a minimal plugin.
