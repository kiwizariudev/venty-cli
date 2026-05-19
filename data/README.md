# data/

All **mutable** project state lives here (not source code).

| Subfolder | Contents |
|-----------|----------|
| `config/` | `settings.json`, `apis.json`, themes, aliases, keybinds |
| `sandbox/` | Default workspace — files Venty creates or edits |
| `runtime/` | Temp compiles, build scratch, session artifacts |
| `cache/` | Action usage statistics |
| `memory/` | Chat `history.json` + long-term `notes.json` |
| `logs/` | `venty.log`, `errors.log`, `sessions.log` |
| `scheduler/` | `jobs.json` — delayed/repeat tasks |

Do not commit secrets (`config/settings.json`, `config/apis.json`).
