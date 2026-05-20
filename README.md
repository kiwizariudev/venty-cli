<p align="center">
  <strong>Venty</strong> — AI desktop assistant<br/>
  Control your computer from natural language.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D6?style=flat-square"/>
  <img src="https://img.shields.io/badge/actions-293+-blueviolet?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square"/>
</p>

---

```
  /\_/\    ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗
 ( o.o )   ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝
  > ^ <    ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝
           ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝
            ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║
             ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝
```

---

## What it does

You type in a terminal. Venty sends your message to an LLM, gets back a JSON action, and runs it on your machine.

```
  you  →  cli.py  →  LLM API  →  JSON  →  actions/  →  OS
```

- **293+ actions** — files, processes, git, network, browser, registry, encode, web search
- **Cross-platform** — `xp_*` actions work on Windows, macOS, Linux
- **Config actions** — `cfg_*` lets the AI change its own settings at runtime
- **Multi-step task plans** — one prompt triggers a sequence of actions
- **Persistent memory** — notes survive across sessions
- **Streaming** — spinner while waiting, clean output after
- **Suggestions** — AI proposes follow-up actions after each response
- **Plugins** — 8 bundled + drop your own `.py` in `extensions/plugins/`
- **Themes** — default, dark, matrix, ocean
- **Scheduler** — run actions on a delay or on repeat
- **Config UI** — `python config.py` for a rich management interface

---

## Quick start

```powershell
git clone <repo> && cd reflect
python -m venv env && .\env\Scripts\Activate.ps1
python setup.py        # menu → 4 Build & install
python setup.py        # menu → 1 Setup API provider
python cli.py
```

---

## Project layout

```
reflect/
├── cli.py                  main entry point
├── setup.py                setup wizard (API keys, models, build)
├── config.py               rich config management UI
│
├── core/                   engine
│   ├── agent.py            LLM communication + streaming
│   ├── executor.py         action execution + path resolution
│   ├── tasks.py            multi-step task runner
│   ├── memory.py           persistent notes (memory/notes.json)
│   ├── scheduler.py        delayed / repeating jobs
│   ├── plugins.py          plugin loader
│   ├── prompt.py           system prompt builder (cloud + local)
│   ├── paths.py            all path constants
│   ├── jsonutil.py         robust JSON extraction from LLM output
│   ├── aliases.py          command aliases
│   ├── history.py          conversation history
│   └── plugin_sdk.py       helpers for writing plugins
│
├── actions/                293+ built-in actions
│   ├── files.py            file & folder operations
│   ├── compile.py          gcc, g++, python, node, java, npm, pip
│   ├── git.py              git operations
│   ├── network.py          ping, wifi, DNS, download
│   ├── browser.py          Chrome, Edge, Firefox, URL open
│   ├── web.py              DuckDuckGo search, fetch, HTTP POST
│   ├── system.py           CPU, RAM, GPU, disk, env vars, time
│   ├── windows.py          Windows UI, settings panels
│   ├── power.py            shutdown, restart, sleep, volume
│   ├── registry.py         Windows registry read/write
│   ├── clipboard.py        clipboard read/write/clear
│   ├── encode.py           base64, md5, sha256, sha1
│   ├── crossplatform.py    xp_* — Windows + macOS + Linux
│   ├── config_actions.py   cfg_* — change config at runtime
│   └── control.py          loop_start, none, cannot_do
│
├── ui/
│   └── colors.py           ANSI colors, banner (with cat), print helpers
│
├── data/                   all mutable state (gitignored)
│   ├── config/             settings.json, apis.json, themes.json
│   ├── sandbox/            default working_dir for file actions
│   ├── memory/             history.json, notes.json, quicknotes.json
│   ├── logs/               venty.log, errors.log, sessions.log
│   ├── cache/              actions.json (usage stats)
│   └── scheduler/          jobs.json
│
└── extensions/
    └── plugins/            8 bundled plugins + your own
        ├── dev_tools.py    pytest, mypy, black, flake8, venv, line count
        ├── dev_pack.py     dev workflow helpers
        ├── media.py        play/pause, next/prev, brightness
        ├── system_info.py  full sysinfo, drives, user, home
        ├── quicknotes.py   lightweight note-taking
        ├── webaddons.py    browser shortcuts
        ├── clipboard_plus.py  clipboard history
        ├── fun_pack.py     fun actions
        └── _template.py   starter template for your own plugin
```

---

## Configuration

`data/config/settings.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `api_key` | | Provider API key |
| `model` | | Model id |
| `display_name` | | Name shown in banner |
| `url` | Groq endpoint | Chat completions URL |
| `working_dir` | `data/sandbox` | Where file actions run |
| `stream` | `true` | Streaming mode |
| `max_tokens` | `700` | Reply length limit |
| `temperature` | `0.2` | Model creativity |
| `theme` | `default` | UI theme (`default` `dark` `matrix` `ocean`) |
| `max_session_turns` | `40` | Context window limit |

Change at runtime:
- CLI: `set stream false`
- Ask Venty: `cfg_set stream false`
- Config UI: `python config.py`

---

## CLI commands

| Command | Description |
|---------|-------------|
| `help` | List all commands |
| `actions` | List all 293+ actions by category |
| `config` | Show current settings |
| `set <key> <value>` | Change a setting live |
| `reload` | Reload config from disk |
| `memory` | Show saved notes |
| `remember <text>` | Save a note to memory |
| `forget <text>` | Remove a note |
| `stats` | Action usage bar chart |
| `history` | Conversation history |
| `logs` / `errors` | View log files |
| `sessions` | Session log |
| `plugins` | List loaded plugins with action counts |
| `reload plugins` | Hot-reload plugin files |
| `jobs` | List scheduled jobs |
| `aliases` | List command aliases |
| `alias <name> = <exp>` | Create a shortcut |
| `clear` | Clear screen + session memory |
| `exit` | Quit |

---

## Action prefixes

| Prefix | Category | Platform |
|--------|----------|----------|
| `os_` | Windows-specific | Windows |
| `xp_` | Cross-platform | Win + macOS + Linux |
| `cfg_` | Config management | All |
| `web_` | Web search / fetch / HTTP | All |
| `os_git_` | Git operations | All |
| `os_compile_` | Compile C/C++/Java/C# | All |
| `memory_` | Persistent notes | All |
| `dev_` | Dev tools (plugin) | All |
| `media_` | Media controls (plugin) | Win + Linux |
| `note_` | Quick notes (plugin) | All |
| `sysinfo_` | System info (plugin) | All |
| `loop_start` | Repeat action N times | All |

---

## Multi-step tasks

Ask for several things at once:

```
make a hello.py file and run it
```

Venty returns a `task_plan` and executes each step with a progress bar:

```json
{
  "action": "task_plan",
  "steps": [
    {"action": "os_write_file", "args": ["hello.py", "print('hello')"]},
    {"action": "os_run_python", "args": ["hello.py"]}
  ],
  "message": "Creating and running hello.py",
  "suggestions": ["add error handling", "run it again"]
}
```

---

## Suggestions

After every AI response, Venty shows 2-3 follow-up suggestions. Type a number to select one instantly.

```
  ╭─ suggestions ──────────────────────────────────────
  │  1. run the script
  │  2. add error handling
  │  3. show the output
  ╰────────────────────────────────────────────────────
     type a number to select, or just keep typing
```

---

## Plugins

Drop a `.py` file in `extensions/plugins/`:

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

Then type `reload plugins` in Venty. See `_template.py` for a full example.

---

## Providers

| Provider | Setup | Console |
|----------|-------|---------|
| Groq | `setup.py` → 1 | https://console.groq.com |
| Mistral | `setup.py` → 1 | https://console.mistral.ai |
| OpenAI | `setup.py` → 1 | https://platform.openai.com |
| Anthropic | `setup.py` → 1 | https://console.anthropic.com |
| Together AI | `setup.py` → 1 | https://api.together.xyz |
| LM Studio | `setup.py` → 3 | `http://127.0.0.1:1234` (local) |

For LM Studio: use a model with at least 8k context. The system prompt is automatically shortened for local models.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `could not reach Venty AI` | Check API key, run `setup.py` |
| Rate limit 429 | Wait or `cfg_switch_provider <name>` |
| LM Studio context error | Use a larger model or `set max_tokens 300` |
| Files in wrong folder | `set working_dir <path>` |
| Raw JSON showing | `set stream false` |
| Plugin not loading | Check `plugins` command for error messages |

Logs: `data/logs/venty.log` · `data/logs/errors.log`

---

## Security

- API keys live in `data/config/` — never commit `settings.json` or `apis.json` (both gitignored)
- Default `working_dir` is `data/sandbox/` — generated files stay contained
- Registry, shutdown, and process-kill actions exist — use a trusted model

---

## License

MIT
