# data/

All **mutable** project state lives here. This folder is gitignored (except `.gitkeep` files).

| Subfolder | Contents | Notes |
|-----------|----------|-------|
| `config/` | `settings.json`, `apis.json`, `themes.json`, `aliases.json`, `keybinds.json` | API keys live here — never commit |
| `sandbox/` | Default `working_dir` — files Venty creates or edits | Safe to delete contents |
| `runtime/` | Temp compiles, build scratch, session artifacts | Auto-cleaned |
| `cache/` | `actions.json` — action usage statistics | Used by `stats` command and web dashboard |
| `memory/` | `history.json` — conversation history<br>`notes.json` — long-term memory<br>`quicknotes.json` — quick notes plugin | Cleared with `clear history` / `clear memory` |
| `logs/` | `venty.log` — all activity<br>`errors.log` — errors only<br>`sessions.log` — session start/end markers | Viewed with `logs` / `errors` / `sessions` commands |
| `scheduler/` | `jobs.json` — delayed and repeating jobs | Managed with `jobs` / `cancel` commands |

## Security

`config/settings.json` and `config/apis.json` contain your API keys.
They are in `.gitignore` — **do not commit them**.

## Web Dashboard

All files in `data/` are readable by the bridge web dashboard at `http://localhost:7432`.
The API key is masked in the config endpoint.
