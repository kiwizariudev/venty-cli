# extensions/

Optional add-ons. Drop files here to extend Venty without touching core code.

## plugins/

Python files with an `ACTIONS` dict — auto-loaded at startup.

### Bundled plugins

| Plugin | Actions | Description |
|--------|---------|-------------|
| `dev_tools.py` | `dev_run_tests`, `dev_lint`, `dev_format`, `dev_count_lines`, ... | pytest, mypy, black, flake8, venv |
| `dev_pack.py` | `dev_*` | Dev workflow helpers |
| `media.py` | `media_play_pause`, `media_next`, `display_brightness_up`, ... | Media controls, screen brightness |
| `system_info.py` | `sysinfo_full`, `sysinfo_drives`, `sysinfo_user`, ... | Detailed system information |
| `quicknotes.py` | `note_add`, `note_list`, `note_delete`, `note_clear` | Lightweight note-taking |
| `webaddons.py` | `web_*` | Browser shortcuts |
| `clipboard_plus.py` | `clip_*` | Clipboard history |
| `fun_pack.py` | `fun_*` | Fun actions |

### Writing your own plugin

Copy `_template.py` and add your actions:

```python
PLUGIN_NAME    = "My Plugin"
PLUGIN_VERSION = "1.0.0"

ACTIONS = {
    "my_action": {
        "description": "Does something, args = [text]",
        "execute": lambda a: type("R", (), {"stdout": a[0].upper()})()
    }
}
```

Then type `reload plugins` in Venty — no restart needed.

### Plugin SDK helpers

```python
from core.plugin_sdk import ok, fail, result

ACTIONS = {
    "my_action": {
        "description": "Example, args = [text]",
        "execute": lambda a: ok(a[0].upper())
    }
}
```

## modules/

Optional Python helper files. Import them from your plugins:

```python
from extensions.modules import my_helper
```

## api/ and bridge/

Reserved for future use.
