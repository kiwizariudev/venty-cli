import subprocess
import requests
import json
import re
import os
import sys
import time
import datetime
import random
import logging
import shutil
import platform
import socket
import hashlib
import base64
import zipfile
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from core.aliases   import resolve as _resolve_alias, load_aliases, set_alias, remove_alias
    from core.scheduler import tick as _scheduler_tick, list_jobs, cancel_job, schedule_once, schedule_repeat
    from core.logger    import log_session_start, log_session_end, SESSION_PATH, read_log_tail
    from core.memory    import remember, forget, list_notes, clear_notes, get_memory_block
    from core.jsonutil  import extract_first_json
    from core.prompt    import build_system_prompt as _build_system_prompt
    from core.tasks     import run_task_plan
    from core.executor  import execute_action as _core_execute_action
    from core.plugins   import load_all_plugins, get_registry, get_load_errors, format_plugins_for_prompt
    from ui.colors      import print_banner as _ui_print_banner, print_venty as _ui_print_venty, print_success as _ui_print_success, print_error as _ui_print_error, print_warning as _ui_print_warning, print_info as _ui_print_info, print_output as _ui_print_output, print_action as _ui_print_action, print_loop_step as _ui_print_loop_step, print_separator as _ui_print_separator, print_step as _ui_print_step, Colors as UIColors
    _HAS_CORE = True
except ImportError:
    _HAS_CORE = False
    def get_memory_block(): return ""
    def remember(t, c="facts"): return "memory module not available"
    def forget(t): return "memory module not available"
    def list_notes(): return "memory module not available"
    def clear_notes(): return "memory module not available"
    def extract_first_json(text): return _extract_first_json_fallback(text)
    def _build_system_prompt(actions, cfg): return build_system_prompt_fallback()
    def run_task_plan(*a, **k): pass
    def _core_execute_action(*a, **k): return False, "core not available"
    def load_all_plugins(*a, **k): return {}, []
    def get_registry(): return []
    def get_load_errors(): return []
    def format_plugins_for_prompt(*a, **k): return ""
    def _ui_print_banner(*a, **k): pass
    def _ui_print_venty(*a, **k): pass
    def _ui_print_success(*a, **k): pass
    def _ui_print_error(*a, **k): pass
    def _ui_print_warning(*a, **k): pass
    def _ui_print_info(*a, **k): pass
    def _ui_print_output(*a, **k): pass
    def _ui_print_action(*a, **k): pass
    def _ui_print_loop_step(*a, **k): pass
    def _ui_print_separator(*a, **k): pass
    def _ui_print_step(*a, **k): pass

try:
    from core.paths import (
        ensure_dirs, CONFIG_PATH, HISTORY_PATH, LOG_PATH, ERROR_PATH,
        CACHE_PATH, ALIASES_PATH, THEMES_PATH, KEYBINDS_PATH, SANDBOX_DIR,
        RUNTIME_DIR, PLUGINS_DIR, SESSION_PATH, default_working_dir,
    )
    ensure_dirs()
except ImportError:
    CONFIG_PATH = os.path.join(BASE_DIR, "data", "config", "settings.json")
    HISTORY_PATH = os.path.join(BASE_DIR, "data", "memory", "history.json")
    LOG_PATH = os.path.join(BASE_DIR, "data", "logs", "venty.log")
    ERROR_PATH = os.path.join(BASE_DIR, "data", "logs", "errors.log")
    CACHE_PATH = os.path.join(BASE_DIR, "data", "cache", "actions.json")
    ALIASES_PATH = os.path.join(BASE_DIR, "data", "config", "aliases.json")
    THEMES_PATH = os.path.join(BASE_DIR, "data", "config", "themes.json")
    KEYBINDS_PATH = os.path.join(BASE_DIR, "data", "config", "keybinds.json")
    SESSION_PATH = os.path.join(BASE_DIR, "data", "logs", "sessions.log")
    SANDBOX_DIR = os.path.join(BASE_DIR, "data", "sandbox")
    RUNTIME_DIR = os.path.join(BASE_DIR, "data", "runtime")
    PLUGINS_DIR = os.path.join(BASE_DIR, "extensions", "plugins")
    def default_working_dir(): return SANDBOX_DIR
    def ensure_dirs():
        for f in ["data/config", "data/memory", "data/logs", "data/cache",
                  "data/sandbox", "data/runtime", "data/scheduler", "extensions/plugins"]:
            os.makedirs(os.path.join(BASE_DIR, f.replace("/", os.sep)), exist_ok=True)
    ensure_dirs()

logger = logging.getLogger("venty")
logger.setLevel(logging.DEBUG)
file_handler  = logging.FileHandler(LOG_PATH,   encoding="utf-8")
error_handler = logging.FileHandler(ERROR_PATH, encoding="utf-8")
file_handler.setLevel(logging.INFO)
error_handler.setLevel(logging.ERROR)
fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(fmt)
error_handler.setFormatter(fmt)
logger.addHandler(file_handler)
logger.addHandler(error_handler)

DEFAULT_CONFIG = {
    "api_key":             "",
    "model":               "",
    "display_name":        "",
    "url":                 "https://api.groq.com/openai/v1/chat/completions",
    "provider":            "",
    "max_loop":            20,
    "max_tokens":          700,
    "temperature":         0.2,
    "save_history":        True,
    "max_history_entries": 100,
    "max_session_turns":   40,
    "timeout":             60,
    "show_output":         True,
    "confirm_dangerous":   True,
    "working_dir":         os.path.join(BASE_DIR, "data", "sandbox"),
    "theme":               "default",
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

CONFIG  = load_config()
API_KEY = CONFIG.get("api_key", "")
MODEL   = CONFIG.get("model",   "")
URL     = CONFIG.get("url",     "https://api.groq.com/openai/v1/chat/completions")

DEFAULT_THEMES = {
    "default": {"primary":"96","secondary":"95","success":"92","error":"91","warning":"93","info":"90","user":"94"},
    "dark":    {"primary":"36","secondary":"35","success":"32","error":"31","warning":"33","info":"90","user":"34"},
    "matrix":  {"primary":"92","secondary":"32","success":"92","error":"91","warning":"93","info":"32","user":"92"},
    "ocean":   {"primary":"94","secondary":"96","success":"92","error":"91","warning":"93","info":"90","user":"95"},
}

def load_themes():
    if not os.path.exists(THEMES_PATH):
        try:
            with open(THEMES_PATH, "w") as f:
                json.dump(DEFAULT_THEMES, f, indent=2)
        except Exception:
            pass
        return DEFAULT_THEMES.copy()
    try:
        with open(THEMES_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_THEMES.copy()

_ACTIVE_THEME = {}

def apply_theme(name):
    global _ACTIVE_THEME
    themes = load_themes()
    _ACTIVE_THEME = themes.get(name, DEFAULT_THEMES["default"])

apply_theme(CONFIG.get("theme", "default"))

def _c(key):
    code = _ACTIVE_THEME.get(key, "97")
    return f"\033[{code}m"

class Colors:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    PURPLE = "\033[95m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"
    ORANGE = "\033[33m"

VENTY_COLORS = [Colors.CYAN, Colors.PURPLE, Colors.BLUE, Colors.GREEN, Colors.YELLOW]

def vc():
    if _HAS_CORE:
        from ui.colors import vc as _vc
        return _vc()
    return random.choice(VENTY_COLORS)

def print_venty(message):
    if _HAS_CORE:
        _ui_print_venty(message)
    else:
        c = vc()
        print(f"\n{c}{Colors.BOLD}Venty >{Colors.RESET} {c}{message}{Colors.RESET}")

def print_success(msg):
    if _HAS_CORE: _ui_print_success(msg)
    else: print(f"{_c('success')}  + {msg}{Colors.RESET}")

def print_error(msg):
    if _HAS_CORE: _ui_print_error(msg)
    else: print(f"{_c('error')}  x {msg}{Colors.RESET}")

def print_warning(msg):
    if _HAS_CORE: _ui_print_warning(msg)
    else: print(f"{_c('warning')}  ! {msg}{Colors.RESET}")

def print_info(msg):
    if _HAS_CORE: _ui_print_info(msg)
    else: print(f"{_c('info')}  > {msg}{Colors.RESET}")

def print_output(text):
    if _HAS_CORE: _ui_print_output(text)
    else: print(f"\n{_c('info')}{text}{Colors.RESET}")

def print_action(action, args):
    if _HAS_CORE: _ui_print_action(action, args)
    else:
        args_str = ", ".join(str(a) for a in args) if args else "no args"
        print(f"{_c('warning')}  * action: {Colors.BOLD}{action}{Colors.RESET}{_c('warning')} -> [{args_str}]{Colors.RESET}")

def print_loop_step(i, total, action, args):
    if _HAS_CORE: _ui_print_loop_step(i, total, action, args)
    else:
        args_str = ", ".join(str(a) for a in args) if args else "no args"
        print(f"{_c('secondary')}  loop [{i}/{total}] {Colors.BOLD}{action}{Colors.RESET}{_c('secondary')} -> [{args_str}]{Colors.RESET}")

def print_separator():
    if _HAS_CORE: _ui_print_separator()
    else: print(f"{_c('info')}  {'—' * 52}{Colors.RESET}")

def print_banner():
    if _HAS_CORE:
        provider = CONFIG.get("provider", "")
        display_name = CONFIG.get("display_name", "") or CONFIG.get("model", "not configured")
        _ui_print_banner(provider, display_name)
    else:
        c = random.choice(VENTY_COLORS)
        provider     = CONFIG.get("provider",     "")
        display_name = CONFIG.get("display_name", "") or CONFIG.get("model", "not configured")
        banner_lines = [
            f"  {c} .~~~.     {Colors.BOLD} ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗",
            f"  {c}(o . o)    {Colors.BOLD} ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝",
            f"  {c} ) v (     {Colors.BOLD} ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝",
            f"  {c}~~ ~ ~~    {Colors.BOLD} ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝ ",
            f"  {c}~ ~ ~ ~ ~  {Colors.BOLD}  ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║  ",
            f"  {c}           {Colors.BOLD}   ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝  "
        ]
        print("\n" + "\n".join(banner_lines))
        print(f"{Colors.RESET}{Colors.GRAY}                        Welcome to the new Venty CLI UX! /help to learn more.")
        print(f"{Colors.RESET}{Colors.GRAY}                             AI Desktop Assistant  •  {provider if provider else 'Venty'}  •  {display_name}")
        print_separator()

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    if not CONFIG.get("save_history", True):
        return
    try:
        entries = load_history()
        entries.extend(history)
        max_e = CONFIG.get("max_history_entries", 100)
        if len(entries) > max_e:
            entries = entries[-max_e:]
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save history: {e}")

def trim_session(session, max_turns):
    if len(session) <= max_turns * 2:
        return session
    return session[-(max_turns * 2):]

def log_action(action, args, success, output=None):
    try:
        data = []
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r") as f:
                data = json.load(f)
        data.append({
            "timestamp":      datetime.datetime.now().isoformat(),
            "action":         action,
            "args":           args,
            "success":        success,
            "output_preview": str(output)[:120] if output else None
        })
        data = data[-500:]
        with open(CACHE_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to log action: {e}")

def _load_aliases():
    if not os.path.exists(ALIASES_PATH):
        return {}
    try:
        with open(ALIASES_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_aliases(aliases):
    with open(ALIASES_PATH, "w") as f:
        json.dump(aliases, f, indent=2)

def resolve_alias(text):
    aliases = _load_aliases()
    for name, expansion in aliases.items():
        if text.lower().startswith(name.lower()):
            return expansion + text[len(name):]
    return text

def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

def popen(cmd, **kwargs):
    return subprocess.Popen(cmd, shell=True, **kwargs)

def stdout_obj(text):
    return type('R', (), {'stdout': str(text)})()

def file_hash(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def resolve_path(path):
    if os.path.isabs(path) or path.startswith("http"):
        return path
    return os.path.join(CONFIG.get("working_dir", BASE_DIR), path)

def _extract_first_json_fallback(text):
    clean = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

if _HAS_CORE:
    def _extract_first_json(text):
        return extract_first_json(text)
else:
    _extract_first_json = _extract_first_json_fallback

try:
    from actions import ACTIONS as _PKG_ACTIONS
    ACTIONS = dict(_PKG_ACTIONS)
except ImportError as _e:
    logger.warning(f"actions package not loaded: {_e}")
    ACTIONS = {}

ACTIONS.update({
    "memory_remember": {"description": "Save a fact/note to memory, args = [text]", "execute": lambda a: stdout_obj(remember(a[0], a[1] if len(a) > 1 else "facts"))},
    "memory_forget":   {"description": "Remove a note from memory, args = [text_to_match]", "execute": lambda a: stdout_obj(forget(a[0]))},
    "memory_list":     {"description": "List all saved notes", "execute": lambda a: stdout_obj(list_notes())},
    "memory_clear":    {"description": "Clear all saved notes", "execute": lambda a: stdout_obj(clear_notes())},
})

def reload_plugins():
    global _PLUGIN_REGISTRY
    if _HAS_CORE:
        plugin_actions, _PLUGIN_REGISTRY = load_all_plugins(PLUGINS_DIR)
        to_remove = [k for k, v in ACTIONS.items() if v.get("plugin")]
        for k in to_remove:
            del ACTIONS[k]
        ACTIONS.update(plugin_actions)
        return len(plugin_actions)
    return 0

_PLUGIN_REGISTRY = []
reload_plugins()

def build_system_prompt():
    if _HAS_CORE:
        base = _build_system_prompt(ACTIONS, CONFIG)
        block = format_plugins_for_prompt(_PLUGIN_REGISTRY)
        if block:
            return base + "\n\n" + block
        return base
    working_dir  = CONFIG.get("working_dir", BASE_DIR)
    now          = datetime.datetime.now().strftime("%A %d %B %Y  %H:%M")
    provider     = CONFIG.get("provider", "").lower()
    is_local     = provider in ("lm studio", "lmstudio") or "localhost" in CONFIG.get("url", "") or "127.0.0.1" in CONFIG.get("url", "")
    memory_block = get_memory_block()

    context_block = f"""CONTEXT:
  working_dir : {working_dir}
  datetime    : {now}
  hostname    : {socket.gethostname()}
  os          : {platform.system()} {platform.release()}

Always use absolute paths based on working_dir. Never create files outside working_dir unless explicitly asked."""

    memory_section = f"\n{memory_block}\n" if memory_block else ""

    rules = f"""Respond ONLY with a valid JSON object:
{{"action": "action_name", "args": ["arg1", "arg2"], "message": "Short reply"}}

For MULTI-STEP tasks, respond with a task plan:
{{"action": "task_plan", "steps": [{{"action": "os_write_file", "args": ["file.py", "content"]}}, {{"action": "os_run_python", "args": ["file.py"]}}], "message": "I'll create and run the file"}}

RULES:
- action must be one of the listed action names
- args are plain strings only
- Respond in same language as user
- NEVER output anything outside the JSON
- NEVER wrap JSON in markdown blocks
- cannot_do: for harmful, illegal, or impossible requests
- Use task_plan when the user asks for something that needs multiple steps"""

    if is_local:
        action_names = ", ".join(ACTIONS.keys())
        return f"""You are Venty, an AI assistant that controls a Windows computer.

{context_block}
{memory_section}
You MUST reply with ONLY a JSON object, nothing else. No explanation, no markdown, no extra text.

Format:
{{"action": "action_name", "args": ["arg1"], "message": "your reply to the user"}}

Available action names:
{action_names}

Rules: args are plain strings only; use absolute paths based on working_dir; respond in same language; ONLY output JSON."""
    else:
        return f"""You are Venty, a smart and powerful AI assistant that controls a Windows computer.

{context_block}
{memory_section}
You have access to {len(ACTIONS)} actions:
{json.dumps({k: v["description"] for k, v in ACTIONS.items()}, indent=2)}

{rules}

CANNOT DO:
- Hacking or bypassing security
- Accessing private data without permission
- Anything illegal or harmful to others"""

def _ask_streaming(messages, api_key, model, url):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model":       model,
        "messages":    messages,
        "temperature": CONFIG.get("temperature", 0.2),
        "max_tokens":  CONFIG.get("max_tokens",  700),
        "stream":      True,
    }
    full = ""
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=CONFIG.get("timeout", 60)) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line: continue
                line = line.decode("utf-8") if isinstance(line, bytes) else line
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]": break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        token = delta.get("content", "")
                        if token: full += token
                    except: pass
    except: return None
    return full.strip()

def _ask_standard(messages, api_key, model, url):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model":       model,
        "messages":    messages,
        "temperature": CONFIG.get("temperature", 0.2),
        "max_tokens":  CONFIG.get("max_tokens",  700),
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=CONFIG.get("timeout", 60))
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except: return None

def ask_venty(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    api_key  = CONFIG.get("api_key", "")
    model    = CONFIG.get("model",   "")
    url      = CONFIG.get("url",     "https://api.groq.com/openai/v1/chat/completions")
    use_stream = CONFIG.get("stream", True)
    last_raw = None

    for attempt in range(3):
        messages = [{"role": "system", "content": build_system_prompt()}] + conversation_history
        print(f"{Colors.GRAY}  thinking...{Colors.RESET}", end="\r")
        if use_stream:
            raw = _ask_streaming(messages, api_key, model, url)
        else:
            raw = _ask_standard(messages, api_key, model, url)
        if raw is None: return None
        last_raw = raw
        if _extract_first_json(raw) is not None:
            conversation_history.append({"role": "assistant", "content": raw})
            return raw
        try:
            parsed = json.loads(re.sub(r"```json|```", "", raw).strip())
            if parsed.get("action") == "task_plan":
                conversation_history.append({"role": "assistant", "content": raw})
                return raw
        except: pass
        if attempt < 2:
            conversation_history.append({"role": "assistant", "content": raw})
            conversation_history.append({"role": "user", "content": "Invalid JSON. Reply ONLY with a single valid JSON object."})
    return last_raw

def parse_response(raw):
    return _extract_first_json(raw)

def handle_task_plan(parsed):
    steps   = parsed.get("steps", [])
    message = parsed.get("message", "Running task...")
    if not steps: return
    print_venty(message)
    print_separator()
    print_info(f"task plan — {len(steps)} steps")
    print_separator()
    for i, step in enumerate(steps, 1):
        action = step.get("action", "none")
        args   = step.get("args",   [])
        print(f"{_c('secondary')}  [{i}/{len(steps)}] {Colors.BOLD}{action}{Colors.RESET}")
        print_action(action, args)
        if action in ("none", "cannot_do"): continue
        success, output = execute_action(action, args)
        if success:
            print_success(f"step {i} done")
            if output and CONFIG.get("show_output", True): print_output(str(output)[:300])
        else:
            print_error(f"step {i} failed: {output}")
            confirm = input(f"  {Colors.YELLOW}continue anyway? [y/N] >{Colors.RESET} ").strip().lower()
            if confirm != "y": return
        time.sleep(0.2)
    print_separator()
    print_success(f"task complete")

def execute_action(action_name, args):
    if action_name not in ACTIONS: return False, f"unknown action: {action_name}"
    if action_name in ("none", "cannot_do", "loop_start"): return True, None
    try:
        result = ACTIONS[action_name]["execute"](args)
        output = getattr(result, "stdout", None)
        log_action(action_name, args, True, output)
        return True, output
    except Exception as e:
        log_action(action_name, args, False, str(e))
        return False, str(e)

def handle_loop(args):
    if len(args) < 2: return
    try: count = int(args[0])
    except: return
    max_loop = CONFIG.get("max_loop", 20)
    if count > max_loop: count = max_loop
    action_name = args[1]
    action_args = args[2:] if len(args) > 2 else []
    if action_name not in ACTIONS: return
    print_info(f"starting loop x{count}")
    print_separator()
    for i in range(1, count + 1):
        print_loop_step(i, count, action_name, action_args)
        success, output = execute_action(action_name, action_args)
        if success:
            print_success(f"step {i} done")
            if output and CONFIG.get("show_output", True): print(f"{Colors.GRAY}    {str(output)[:150]}{Colors.RESET}")
        else:
            print_error(f"step {i} failed: {output}")
        time.sleep(0.3)
    print_separator()
    print_success(f"loop done")

def cmd_actions():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  actions ({len(ACTIONS)} total){Colors.RESET}")
    print_separator()
    categories = {
        "PROCESS":   [k for k in ACTIONS if any(x in k for x in ["close","open","list_proc","kill","pid","priority","service","suspend","resume"])],
        "COMPILE":   [k for k in ACTIONS if any(x in k for x in ["compile","run_exe","run_python","run_node","run_batch","run_java","pip_","npm_","git_","run_command","run_powershell"])],
        "FILES":     [k for k in ACTIONS if any(x in k for x in ["file","folder","zip","unzip","tree","search","dir","cwd","shortcut","explorer","duplicate"])],
        "NETWORK":   [k for k in ACTIONS if any(x in k for x in ["ping","ip","dns","wifi","port","netstat","arp","download","hostname","local_ip","my_ip"])],
        "WEB":       [k for k in ACTIONS if k.startswith("web_")],
        "SYSTEM":    [k for k in ACTIONS if any(x in k for x in ["cpu","ram","gpu","disk","os_info","uptime","battery","driver","hotfix","startup","motherboard","bios","system_info","screenshot","env","installed"])],
        "WINDOWS":   [k for k in ACTIONS if any(x in k for x in ["task_manager","control","device","services","event","registry","cmd","powershell","settings","calculator","notepad","paint","wordpad","sfc","chkdsk","update","display","sound","firewall","apps","bluetooth","network_set","person","privacy","magnifier","keyboard","charmap","cleanup","defrag","resource","performance","remote","snipping","narrator","scheduler","group","user","winver","reg_"])],
        "VOLUME":    [k for k in ACTIONS if "volume" in k],
        "POWER":     [k for k in ACTIONS if any(x in k for x in ["shutdown","restart","sleep","hibernate","lock","cancel_shutdown","logoff"])],
        "CLIPBOARD": [k for k in ACTIONS if "clipboard" in k],
        "TIME":      [k for k in ACTIONS if any(x in k for x in ["time","timer","sync"])],
        "ENCODE":    [k for k in ACTIONS if any(x in k for x in ["base64","md5","sha256","sha1"])],
        "CONTROL":   ["loop_start", "cannot_do", "none"],
    }
    for cat, keys in categories.items():
        keys = [k for k in keys if k in ACTIONS]
        if not keys: continue
        print(f"\n  {Colors.CYAN}{Colors.BOLD}{cat}{Colors.RESET}")
        for k in keys:
            desc = ACTIONS[k]["description"][:65]
            print(f"  {Colors.GRAY}  {Colors.BOLD}{k:<38}{Colors.RESET}{Colors.GRAY}{desc}{Colors.RESET}")
    print_separator()

def cmd_history():
    entries = load_history()
    if not entries: return
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  history ({len(entries)} entries){Colors.RESET}")
    print_separator()
    for e in entries[-20:]:
        role, content = e.get("role", "?").upper(), e.get("content", "")[:90].replace("\n", " ")
        color = Colors.BLUE if role == "USER" else Colors.CYAN
        print(f"  {color}{Colors.BOLD}{role:<12}{Colors.RESET}{Colors.GRAY}{content}{Colors.RESET}")
    print_separator()

def cmd_logs():
    if not os.path.exists(LOG_PATH): return
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  recent logs{Colors.RESET}")
    print_separator()
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[-25:]: print(f"  {Colors.GRAY}{line.rstrip()}{Colors.RESET}")
    print_separator()

def cmd_errors():
    if not os.path.exists(ERROR_PATH): return
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  recent errors{Colors.RESET}")
    print_separator()
    with open(ERROR_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[-20:]: print(f"  {Colors.RED}{line.rstrip()}{Colors.RESET}")
    print_separator()

def cmd_sessions():
    if not os.path.exists(SESSION_PATH): return
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  session log{Colors.RESET}")
    print_separator()
    with open(SESSION_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[-30:]: print(f"  {Colors.GRAY}{line.rstrip()}{Colors.RESET}")
    print_separator()

def cmd_config():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  config{Colors.RESET}")
    print_separator()
    for k, v in CONFIG.items():
        display = "***hidden***" if k == "api_key" else v
        print(f"  {Colors.BOLD}{k:<30}{Colors.RESET}{Colors.GRAY}{display}{Colors.RESET}")
    print_separator()

def cmd_set(args_str):
    parts = args_str.strip().split(" ", 1)
    if len(parts) < 2: return
    key, val = parts[0], parts[1]
    editable = ["temperature","max_tokens","max_loop","save_history","show_output","confirm_dangerous","timeout","working_dir","theme","max_session_turns","stream"]
    if key not in editable: return
    if key == "working_dir":
        if not os.path.isdir(val): return
        CONFIG[key] = val
    elif key == "theme":
        CONFIG[key] = val
        apply_theme(val)
    else:
        try:
            if val.lower() in ("true", "false"): val = val.lower() == "true"
            elif "." in val: val = float(val)
            else: val = int(val)
        except: pass
        CONFIG[key] = val
    save_config(CONFIG)
    print_success(f"set {key} = {CONFIG[key]}")

def cmd_stats():
    if not os.path.exists(CACHE_PATH): return
    try:
        with open(CACHE_PATH, "r") as f: data = json.load(f)
        total, success = len(data), sum(1 for d in data if d.get("success"))
        counts = {}
        for d in data:
            a = d.get("action", "?")
            counts[a] = counts.get(a, 0) + 1
        top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:8]
        print(f"\n{Colors.YELLOW}{Colors.BOLD}  stats{Colors.RESET}")
        print_separator()
        print(f"  {Colors.GRAY}total actions  {Colors.WHITE}{total}{Colors.RESET}")
        print(f"  {Colors.GRAY}succeeded      {Colors.GREEN}{success}{Colors.RESET}")
        print(f"  {Colors.GRAY}failed         {Colors.RED}{total - success}{Colors.RESET}")
        for name, count in top:
            bar = "█" * min(count, 20)
            print(f"  {Colors.GRAY}  {name:<35}{Colors.CYAN}{bar}{Colors.RESET} {count}")
        print_separator()
    except: pass

def cmd_aliases():
    aliases = _load_aliases()
    if not aliases: return
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  aliases{Colors.RESET}")
    print_separator()
    for name, exp in aliases.items(): print(f"  {Colors.BOLD}{name:<20}{Colors.RESET}{Colors.GRAY}{exp}{Colors.RESET}")
    print_separator()

def cmd_jobs():
    if not _HAS_CORE: return
    jobs = list_jobs()
    if not jobs: return
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  scheduled jobs{Colors.RESET}")
    print_separator()
    for j in jobs:
        repeat = "repeat" if j.get("repeat") else "once"
        print(f"  {Colors.BOLD}{j['id']}{Colors.RESET}  {Colors.GRAY}{j['label']}  [{repeat}]  run_at={j['run_at']}{Colors.RESET}")
    print_separator()

def cmd_keybinds():
    kb = {}
    if os.path.exists(KEYBINDS_PATH):
        try:
            with open(KEYBINDS_PATH, "r") as f: kb = json.load(f)
        except: pass
    if not kb: kb = {"clear":"ctrl+l","history":"ctrl+h","help":"ctrl+?","exit":"ctrl+c"}
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  keybinds{Colors.RESET}")
    print_separator()
    for action, key in kb.items(): print(f"  {Colors.BOLD}{action:<20}{Colors.RESET}{Colors.GRAY}{key}{Colors.RESET}")
    print_separator()

def cmd_reload():
    global CONFIG, API_KEY, MODEL, URL
    CONFIG  = load_config()
    API_KEY = CONFIG.get("api_key", "")
    MODEL   = CONFIG.get("model",   "")
    URL     = CONFIG.get("url",     "")
    apply_theme(CONFIG.get("theme", "default"))
    print_success("config reloaded")

def cmd_clear_history():
    if os.path.exists(HISTORY_PATH): os.remove(HISTORY_PATH)
    print_success("history cleared")

def cmd_clear_logs():
    for p in [LOG_PATH, ERROR_PATH]:
        if os.path.exists(p): open(p, "w").close()
    print_success("logs cleared")

def cmd_clear_cache():
    if os.path.exists(CACHE_PATH): os.remove(CACHE_PATH)
    print_success("cache cleared")

def cmd_plugins():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  plugins{Colors.RESET}")
    print_separator()
    if not _PLUGIN_REGISTRY:
        print_info("no plugins loaded")
    else:
        for p in _PLUGIN_REGISTRY:
            print(f"  {Colors.CYAN}{Colors.BOLD}{p['name']}{Colors.RESET} {Colors.GRAY}v{p['version']}{Colors.RESET}")
            acts = p.get("actions", [])
            print(f"    {Colors.GREEN}{len(acts)} actions:{Colors.RESET} {', '.join(acts[:6])}")
    print_separator()

def cmd_help():
    print(f"\n{Colors.YELLOW}{Colors.BOLD}  commands{Colors.RESET}")
    print_separator()
    cmds = [
        ("actions", "list all available actions"),
        ("history", "show conversation history"),
        ("sessions", "show session log"),
        ("logs", "show recent log entries"),
        ("errors", "show recent error entries"),
        ("config", "show current configuration"),
        ("set <k> <v>", "change a config value"),
        ("reload", "reload config"),
        ("stats", "show action statistics"),
        ("memory", "show all saved notes"),
        ("remember <text>", "save a note"),
        ("forget <text>", "remove a note"),
        ("clear memory", "clear all notes"),
        ("aliases", "list all aliases"),
        ("alias <name> = <exp>", "create an alias"),
        ("unalias <name>", "remove an alias"),
        ("jobs", "list scheduled jobs"),
        ("cancel <job_id>", "cancel a job"),
        ("keybinds", "show keybinds"),
        ("clear", "clear screen and memory"),
        ("clear history", "delete history file"),
        ("clear logs", "clear log files"),
        ("clear cache", "clear action cache"),
        ("plugins", "list loaded plugins"),
        ("reload plugins", "reload plugins"),
        ("help", "show this message"),
        ("exit", "quit venty"),
    ]
    for cmd, desc in cmds: print(f"  {Colors.CYAN}{Colors.BOLD}{cmd:<28}{Colors.RESET}{Colors.GRAY}{desc}{Colors.RESET}")
    print_separator()

def show_suggestions(suggestions):
    if not suggestions: return None
    print(f"\n  {Colors.YELLOW}Suggestions:{Colors.RESET}")
    for i, s in enumerate(suggestions, 1): print(f"  {Colors.CYAN}{i}. {Colors.RESET}{s}")
    print(f"\n  {Colors.GRAY}(Type number to select or just type your next message){Colors.RESET}")
    return suggestions

def main():
    if os.name == "nt":
        os.system("cls")
        os.system("color")
    print_banner()
    if _HAS_CORE: log_session_start()
    print(f"{Colors.GRAY}  connecting...{Colors.RESET}", end="", flush=True)
    try:
        _url = CONFIG.get("url", "")
        base_url = _url.split("/v1/")[0] if "/v1/" in _url else _url
        requests.get(base_url, timeout=5)
        print(f" {Colors.GREEN}connected{Colors.RESET}")
    except:
        print(f" {Colors.YELLOW}offline or unreachable{Colors.RESET}")
    now = datetime.datetime.now().strftime("%A %d %B %Y  %H:%M")
    print(f"{Colors.GRAY}  {now}{Colors.RESET}")
    print(f"{Colors.GRAY}  {len(ACTIONS)} actions available  •  type 'help' for commands{Colors.RESET}\n")
    print_separator()
    print(f" {Colors.CYAN}{CONFIG.get('display_name') or CONFIG.get('model', 'Venty')} · auto {Colors.RESET}                                                                    {Colors.GRAY}{os.getcwd()}{Colors.RESET}\n")
    print(f"  {Colors.BOLD}ask a question or describe a task ↵{Colors.RESET}")
    print_separator()
    conversation_history, session_actions, current_suggestions = [], 0, []
    BUILTIN = {
        "actions": cmd_actions, "history": cmd_history, "sessions": cmd_sessions, "logs": cmd_logs,
        "errors": cmd_errors, "config": cmd_config, "reload": cmd_reload, "stats": cmd_stats,
        "aliases": cmd_aliases, "jobs": cmd_jobs, "keybinds": cmd_keybinds,
        "memory": lambda: print_venty(list_notes()), "clear memory": lambda: print_venty(clear_notes()),
        "clear history": cmd_clear_history, "clear logs": cmd_clear_logs, "clear cache": cmd_clear_cache,
        "plugins": cmd_plugins, "help": cmd_help,
    }
    while True:
        if _HAS_CORE:
            try:
                ran = _scheduler_tick(execute_action, ACTIONS, CONFIG)
                for action, args, output in ran:
                    print_separator()
                    print_info(f"[scheduler] {action}")
                    print_action(action, args)
                    if output and CONFIG.get("show_output", True): print_output(str(output)[:300])
            except: pass
        try:
            if current_suggestions:
                user_input = input(f"\n{_c('user')}{Colors.BOLD}you >{Colors.RESET} ").strip()
                if user_input.isdigit():
                    idx = int(user_input) - 1
                    if 0 <= idx < len(current_suggestions):
                        user_input = current_suggestions[idx]
                        print(f"{_c('user')}{Colors.BOLD}selected >{Colors.RESET} {user_input}")
                current_suggestions = []
            else: user_input = input(f"\n{_c('user')}{Colors.BOLD}you >{Colors.RESET} ").strip()
        except:
            save_history(conversation_history)
            if _HAS_CORE: log_session_end(len(conversation_history) // 2, session_actions)
            print_venty("goodbye")
            break
        if not user_input: continue
        user_input = resolve_alias(user_input)
        if user_input.lower() in ["exit", "quit", "bye"]:
            save_history(conversation_history)
            if _HAS_CORE: log_session_end(len(conversation_history) // 2, session_actions)
            print_venty("goodbye")
            break
        if user_input.lower() == "clear":
            save_history(conversation_history)
            conversation_history = []
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()
            print_separator()
            print_venty("memory cleared")
            continue
        if user_input.lower().startswith("set "):
            cmd_set(user_input[4:])
            continue
        if user_input.lower() == "reload plugins":
            n = reload_plugins()
            print_success(f"reloaded plugins — {n} plugin actions, {len(ACTIONS)} total actions")
            continue
        if user_input.lower().startswith("remember "):
            print_venty(remember(user_input[9:].strip()))
            continue
        if user_input.lower().startswith("forget "):
            print_venty(forget(user_input[7:].strip()))
            continue
        if user_input.lower().startswith("alias "):
            args_str = user_input[6:]
            if "=" not in args_str: print_error("usage: alias <name> = <expansion>")
            else:
                name, expansion = args_str.split("=", 1)
                aliases = _load_aliases()
                aliases[name.strip()] = expansion.strip()
                _save_aliases(aliases)
                print_success(f"alias '{name.strip()}' added")
            continue
        if user_input.lower().startswith("unalias "):
            name = user_input[8:].strip()
            aliases = _load_aliases()
            if name in aliases:
                del aliases[name]
                _save_aliases(aliases)
                print_success(f"removed alias '{name}'")
            continue
        if user_input.lower().startswith("cancel "):
            if _HAS_CORE:
                job_id = user_input[7:].strip()
                if cancel_job(job_id): print_success(f"cancelled job {job_id}")
            continue
        if user_input.lower() in BUILTIN:
            BUILTIN[user_input.lower()]()
            continue
        if not CONFIG.get("api_key"): continue
        conversation_history = trim_session(conversation_history, CONFIG.get("max_session_turns", 40))
        raw = ask_venty(user_input, conversation_history)
        print("\r" + " " * 20 + "\r", end="")
        if raw is None: continue
        parsed = parse_response(raw)
        if parsed is None:
            print_venty(raw)
            continue
        action, args, message = parsed.get("action", "none"), parsed.get("args", []), parsed.get("message", "done")
        if action == "task_plan":
            handle_task_plan(parsed)
            session_actions += len(parsed.get("steps", []))
            current_suggestions = show_suggestions(parsed.get("suggestions", []))
            print_separator()
            continue
        print_separator()
        print_venty(message)
        if action == "cannot_do":
            if any(w in user_input.lower() for w in ("open", "website", "browser")):
                print_info("try: web_open_chrome <url>")
        elif action == "loop_start":
            handle_loop(args)
            session_actions += 1
        elif action in ("memory_remember", "memory_forget", "memory_list", "memory_clear"):
            success, output = execute_action(action, args)
            session_actions += 1
            if success and output: print_info(output)
        elif action and action != "none":
            success, output = execute_action(action, args)
            session_actions += 1
            if success:
                print_success("done")
                if output and CONFIG.get("show_output", True): print(f"\n{Colors.GRAY}{output}{Colors.RESET}")
            else: print_error(f"failed: {output}")
        current_suggestions = show_suggestions(parsed.get("suggestions", []))
        print_separator()

if __name__ == "__main__":
    main()
