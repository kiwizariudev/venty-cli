# Venty plugins

Plugins add new actions Venty can run. Drop a `.py` file here (or a folder with `plugin.py`).

## Quick start

1. Copy `_template.py` → `my_plugin.py`
2. Edit `Plugin(...)` and add `@plugin.action(...)` functions
3. In Venty type: `reload plugins`
4. Type: `plugins` to list what loaded

## Required exports

```python
from core.plugin_sdk import Plugin, ok

plugin = Plugin(id="my_id", name="My Plugin", version="1.0.0", ...)

@plugin.action("my_action", "Description, args = [arg1]")
def my_action(args):
    return ok("result text")

ACTIONS = plugin.actions
PLUGIN_META = plugin.meta
```

## Bundled plugins

| File | Actions |
|------|---------|
| `webaddons.py` | `web_open_chrome`, `web_search`, `web_youtube`, `web_go`, … |
| `fun_pack.py` | `fun_dice`, `fun_coin`, `fun_joke`, `fun_8ball`, … |
| `dev_pack.py` | `dev_tree`, `dev_git_status`, `dev_count_py`, … |
| `clipboard_plus.py` | `clip_read`, `clip_write` |

## Rules

- File names starting with `_` are skipped (`_template.py` is documentation only)
- Action names must be unique across all plugins
- Use `reload plugins` in Venty after editing
- Plugins can import from `actions.*` and `core.*`

## Example prompts

- `open youtube in chrome` → `web_open_chrome` + `https://youtube.com`
- `search python tutorials` → `web_search_google`
- `go to github` → `web_go` + `github`
