<p align="center">
  <strong>Venty</strong> — AI desktop assistant for Windows<br/>
  Control files, apps, browser, shell, and Git from natural language.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/>
</p>

---

## Banner

```
    ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗
    ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝
    ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝
    ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝
     ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║
      ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝
```

---

## What it does

You type in a terminal. Venty sends your message to an LLM (Groq, Mistral, OpenAI, LM Studio, …), gets back a **JSON action**, and runs it on your PC — open Chrome, write a Python file, run commands, multi-step **task plans**, and more.

See the full flow diagram: **[docs/LAYOUT.txt](docs/LAYOUT.txt)**

```
  you  →  cli.py  →  LLM API  →  JSON  →  actions/  →  Windows
```

---

## Quick start

### 1. Clone and enter the project

```powershell
cd d:\za\reflect
```

### 2. Create a virtual environment (recommended)

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

### 3. Build (folders + dependencies)

```powershell
python setup.py
```

Choose **`4` — Build & install dependencies**.

This creates:

| Path | Purpose |
|------|---------|
| `data/sandbox/` | Default workspace — files Venty creates |
| `data/runtime/` | Temp builds and scratch files |
| `data/cache/` | Action statistics |
| `data/memory/` | Chat history and notes |
| `data/logs/` | Application logs |
| `data/config/` | Settings and API keys |
| `extensions/plugins/` | Optional custom actions |

### 4. Configure an API

In `setup.py`, choose **`1` — Setup API provider** (Groq, Mistral, OpenAI, …) or **`3` — LM Studio** for local models.

### 5. Run Venty

```powershell
python cli.py
# or
scripts\run.bat
```

Example prompts:

- `hey`
- `open google in chrome`
- `make a python file hello.py with print hello world`
- `create hello.py and run it` *(multi-step task_plan)*

---

## Project layout

```
reflect/
├── cli.py                 # Main entry
├── setup.py               # Setup + build
├── requirements.txt
│
├── core/                  # Engine (agent, executor, tasks, memory)
├── actions/               # 200+ system actions
├── ui/                    # Terminal UI
│
├── data/                  # All mutable state (see data/README.md)
│   ├── config/            # settings.json, apis.json
│   ├── sandbox/           # AI workspace (default working_dir)
│   ├── runtime/           # temp / compile output
│   ├── cache/             # action stats
│   ├── memory/            # history + notes
│   ├── logs/              # log files
│   └── scheduler/         # jobs.json
│
├── extensions/            # Optional add-ons
│   ├── plugins/           # example_echo.py + your .py files
│   ├── modules/           # helper modules
│   ├── api/               # (reserved)
│   └── bridge/            # (reserved)
│
├── scripts/               # run.bat, run.ps1, setup.bat
├── docs/                  # LAYOUT.txt, FOLDERS.txt
└── assets/                # banner.txt
```

Full map: **[docs/FOLDERS.txt](docs/FOLDERS.txt)** · Flow: **[docs/LAYOUT.txt](docs/LAYOUT.txt)**

---

## Build options

### Standard (development)

```powershell
python setup.py    # menu → 4 Build
python cli.py
```

### Install deps only

```powershell
pip install -r requirements.txt
```

### Package as `.exe` (optional)

```powershell
pip install pyinstaller
pyinstaller cli.spec
# Output: dist/cli.exe
```

---

## Configuration

`data/config/settings.json`:

| Key | Description |
|-----|-------------|
| `api_key` | Provider API key |
| `url` | Chat completions endpoint |
| `model` | Model id |
| `working_dir` | Where file actions run (default: `data/sandbox/`) |
| `stream` | Stream API tokens (`false` = cleaner single-line replies) |
| `max_tokens` | Reply length limit |
| `temperature` | Model creativity |

Reload in Venty: `reload`  
View config: `config`

---

## Plugins

Venty supports **plugins** in `extensions/plugins/`.

| Command | Description |
|---------|-------------|
| `plugins` | List loaded plugins |
| `reload plugins` | Reload after editing a plugin file |

**Bundled plugins:** Web Addons (browser), Fun Pack, Dev Pack, Clipboard Plus.

Create your own: copy `extensions/plugins/_template.py` → `my_plugin.py`.  
Guide: [extensions/plugins/README.md](extensions/plugins/README.md)

Example: `open google in chrome` → uses `web_open_chrome`

---

## Multi-step tasks

Ask for several things at once. The model should return `task_plan`:

```json
{
  "action": "task_plan",
  "steps": [
    {"action": "os_write_file", "args": ["hello.py", "print('hello world')"]},
    {"action": "os_run_python", "args": ["hello.py"]}
  ],
  "message": "Created and ran hello.py"
}
```

Browser helpers: `os_open_url`, `os_open_chrome`, `os_open_edge`, `os_open_browser`

---

## CLI commands

| Command | Description |
|---------|-------------|
| `help` | List commands |
| `actions` | List all actions by category |
| `config` | Show settings |
| `history` | Conversation history |
| `memory` | Saved notes |
| `set stream false` | Disable streaming display |
| `exit` | Quit |

---

## Providers

| Provider | Setup menu | Console |
|----------|------------|---------|
| Groq | 1 | https://console.groq.com |
| Mistral | 1 | https://console.mistral.ai |
| OpenAI | 1 | https://platform.openai.com |
| LM Studio | 3 | Local `http://127.0.0.1:1234` |

---

## Security notes

- API keys live in `data/config/` — **do not commit** `settings.json` or `apis.json`.
- Default `working_dir` is `data/sandbox/` so generated files stay in one place.
- Dangerous system actions exist; use a trusted model and review what Venty runs.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `could not reach Venty AI` | Check API key, rate limits (429), or run `setup.py` |
| Rate limit 429 (Groq) | Wait a minute or switch model |
| Double JSON + message | Set `stream` to `false` in config |
| Files in wrong folder | Set `working_dir` to `sandbox` path in config |

Logs: `data/logs/venty.log`, `data/logs/errors.log`

---

## License

MIT — use and modify freely.
