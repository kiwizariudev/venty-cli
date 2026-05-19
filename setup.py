#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import time
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from core.paths import (
        ensure_dirs,
        CONFIG_DIR,
        CONFIG_PATH as SETTINGS_FILE,
        APIS_PATH as APIS_FILE,
        DIRS,
        default_working_dir,
    )
    ensure_dirs()
except ImportError:
    CONFIG_DIR = os.path.join(BASE_DIR, "data", "config")
    SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
    APIS_FILE = os.path.join(CONFIG_DIR, "apis.json")
    DIRS = {}
    def default_working_dir():
        return os.path.join(BASE_DIR, "data", "sandbox")
    def ensure_dirs():
        os.makedirs(CONFIG_DIR, exist_ok=True)

os.makedirs(CONFIG_DIR, exist_ok=True)

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    PURPLE = "\033[95m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"

COLORS = [C.CYAN, C.PURPLE, C.BLUE, C.GREEN, C.YELLOW]

def rc():
    return random.choice(COLORS)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def sep():
    print(f"{C.GRAY}  {'—' * 50}{C.RESET}")

def ok(msg):
    print(f"{C.GREEN}  + {msg}{C.RESET}")

def err(msg):
    print(f"{C.RED}  x {msg}{C.RESET}")

def warn(msg):
    print(f"{C.YELLOW}  ! {msg}{C.RESET}")

def info(msg):
    print(f"{C.GRAY}  > {msg}{C.RESET}")

def banner():
    clear()
    c = rc()
    print(f"""
{c}{C.BOLD}
  ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗
  ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝
  ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝
  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝
   ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║
    ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝
{C.RESET}{C.GRAY}  Setup & Build Tool  •  v1.0
{C.RESET}""")

def ask(prompt):
    try:
        return input(f"  {C.BLUE}{C.BOLD}{prompt}{C.RESET} ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return ""

def pause():
    ask("press enter to continue...")

def load_apis():
    if not os.path.exists(APIS_FILE):
        return []
    try:
        with open(APIS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_apis(apis):
    with open(APIS_FILE, "w") as f:
        json.dump(apis, f, indent=2)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

# ============================================================
# MENU
# ============================================================
def menu():
    while True:
        banner()
        sep()
        print()
        print(f"  {C.CYAN}1{C.RESET}  Setup API provider")
        print(f"  {C.CYAN}2{C.RESET}  Setup model")
        print(f"  {C.CYAN}3{C.RESET}  Setup LM Studio  {C.GRAY}(local){C.RESET}")
        print(f"  {C.CYAN}4{C.RESET}  Build & install dependencies")
        print(f"  {C.CYAN}5{C.RESET}  View current config")
        print(f"  {C.CYAN}6{C.RESET}  Remove an API")
        print(f"  {C.CYAN}7{C.RESET}  Reset config")
        print(f"  {C.CYAN}0{C.RESET}  Exit")
        print()
        sep()
        print()
        choice = ask("choice >")

        if choice == "1": setup_api()
        elif choice == "2": setup_model()
        elif choice == "3": setup_lm_studio()
        elif choice == "4": build()
        elif choice == "5": view_config()
        elif choice == "6": remove_api()
        elif choice == "7": reset_config()
        elif choice == "0":
            print()
            info("bye")
            print()
            sys.exit(0)

# ============================================================
# SETUP API
# ============================================================
def setup_api():
    banner()
    print(f"\n{C.CYAN}{C.BOLD}  Setup API Provider{C.RESET}")
    sep()

    PROVIDERS = {
        "1": {
            "name":   "Groq",
            "url":    "https://api.groq.com/openai/v1/chat/completions",
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
        },
        "2": {
            "name":   "OpenAI",
            "url":    "https://api.openai.com/v1/chat/completions",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "3": {
            "name":   "Mistral",
            "url":    "https://api.mistral.ai/v1/chat/completions",
            "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest", "open-mixtral-8x22b"]
        },
        "4": {
            "name":   "Anthropic",
            "url":    "https://api.anthropic.com/v1/messages",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
        },
        "5": {
            "name":   "Together AI",
            "url":    "https://api.together.xyz/v1/chat/completions",
            "models": ["meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1", "codellama/CodeLlama-34b-Instruct-hf"]
        },
    }

    print()
    for k, v in PROVIDERS.items():
        print(f"  {C.CYAN}{k}{C.RESET}  {v['name']}")
    print(f"  {C.CYAN}6{C.RESET}  Custom endpoint")
    print(f"  {C.CYAN}0{C.RESET}  Back")
    print()

    choice = ask("choice >")
    if choice == "0":
        return

    if choice in PROVIDERS:
        p = PROVIDERS[choice]
        name   = p["name"]
        url    = p["url"]
        models = p["models"]
    elif choice == "6":
        name   = ask("provider name >")
        url    = ask("endpoint URL >")
        models = []
        print(f"  {C.GRAY}add models one by one, empty line to stop{C.RESET}")
        while True:
            m = ask("model name >")
            if not m:
                break
            models.append(m)
        if not models:
            models = ["custom-model"]
    else:
        err("invalid choice")
        pause()
        return

    print()
    key = ask("paste your API key >")
    if not key:
        err("key cannot be empty")
        pause()
        return

    apis = load_apis()
    existing = next((i for i, a in enumerate(apis) if a["name"] == name), None)
    entry = {"name": name, "url": url, "key": key, "models": models}

    if existing is not None:
        apis[existing] = entry
        ok(f"updated {name}")
    else:
        apis.append(entry)
        ok(f"added {name}")

    save_apis(apis)
    print()
    info("go to Setup Model to activate this provider")
    print()
    pause()

# ============================================================
# SETUP MODEL
# ============================================================
def setup_model():
    banner()
    print(f"\n{C.CYAN}{C.BOLD}  Setup Model{C.RESET}")
    sep()

    apis = load_apis()
    if not apis:
        err("no APIs configured yet")
        info("run Setup API first")
        print()
        pause()
        return

    print()
    for i, a in enumerate(apis):
        print(f"  {C.CYAN}{i+1}{C.RESET}  {a['name']}")
    print(f"  {C.CYAN}0{C.RESET}  Back")
    print()

    choice = ask("select provider >")
    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(apis):
            raise ValueError
    except ValueError:
        err("invalid choice")
        pause()
        return

    api = apis[idx]
    print()
    print(f"  {C.YELLOW}provider : {api['name']}{C.RESET}")
    print(f"  {C.GRAY}available models:{C.RESET}")
    print()

    for i, m in enumerate(api["models"]):
        print(f"  {C.CYAN}{i+1}{C.RESET}  {m}")
    print(f"  {C.CYAN}c{C.RESET}  custom model name")
    print()

    mchoice = ask("select model >")

    if mchoice.lower() == "c":
        model = ask("model name >")
    else:
        try:
            midx = int(mchoice) - 1
            if midx < 0 or midx >= len(api["models"]):
                raise ValueError
            model = api["models"][midx]
        except ValueError:
            err("invalid choice")
            pause()
            return

    settings = load_settings()
    defaults = {
        "max_loop": 20, "max_tokens": 700,
        "temperature": 0.2, "save_history": True,
        "max_history_entries": 100
    }
    for k, v in defaults.items():
        if k not in settings:
            settings[k] = v

    settings["api_key"]      = api["key"]
    settings["model"]        = model
    settings["url"]          = api["url"]
    settings["provider"]     = api["name"]

    print()
    display_name = ask(f"give this model a display name  [{model}] >")
    settings["display_name"] = display_name.strip() if display_name.strip() else model

    save_settings(settings)

    print()
    ok(f"model configured")
    print(f"  {C.CYAN}provider     : {api['name']}{C.RESET}")
    print(f"  {C.CYAN}model        : {model}{C.RESET}")
    print(f"  {C.CYAN}display name : {settings['display_name']}{C.RESET}")
    print()
    pause()

# ============================================================
# SETUP LM STUDIO
# ============================================================
def setup_lm_studio():
    banner()
    print(f"\n{C.CYAN}{C.BOLD}  Setup LM Studio  {C.GRAY}(local){C.RESET}")
    sep()
    print()
    print(f"  {C.GRAY}LM Studio runs locally on your machine.{C.RESET}")
    print(f"  {C.GRAY}Make sure LM Studio is running with a model loaded{C.RESET}")
    print(f"  {C.GRAY}and the local server started before using Venty.{C.RESET}")
    print()
    sep()
    print()

    host = ask("LM Studio host  [default: 127.0.0.1] >")
    if not host:
        host = "127.0.0.1"

    port = ask("LM Studio port  [default: 1234] >")
    if not port:
        port = "1234"

    url = f"http://{host}:{port}/v1/chat/completions"

    print()
    info(f"testing connection to {url.replace('/chat/completions', '/models')} ...")

    try:
        import urllib.request
        req = urllib.request.urlopen(
            url.replace("/chat/completions", "/models"), timeout=4
        )
        data = json.loads(req.read())
        models_available = [m["id"] for m in data.get("data", [])]
        ok("LM Studio is running")
    except Exception as e:
        warn(f"could not connect: {e}")
        warn("make sure LM Studio server is started")
        models_available = []

    print()

    if models_available:
        print(f"  {C.GRAY}detected models:{C.RESET}")
        print()
        for i, m in enumerate(models_available):
            print(f"  {C.CYAN}{i+1}{C.RESET}  {m}")
        print(f"  {C.CYAN}c{C.RESET}  enter custom model name")
        print()
        mchoice = ask("select model >")
        if mchoice.lower() == "c" or not models_available:
            model = ask("model name >")
        else:
            try:
                midx = int(mchoice) - 1
                model = models_available[midx]
            except:
                model = ask("model name >")
    else:
        info("no models detected, enter manually")
        print()
        model = ask("model name  [example: liquid/lfm2.5-1.2b] >")
        if not model:
            model = "local-model"

    settings = load_settings()
    defaults = {
        "max_loop": 20, "max_tokens": 700,
        "temperature": 0.2, "save_history": True,
        "max_history_entries": 100
    }
    for k, v in defaults.items():
        if k not in settings:
            settings[k] = v

    settings["api_key"]  = "lm-studio"
    settings["model"]    = model
    settings["url"]      = url
    settings["provider"] = "LM Studio"
    settings["lm_host"]  = host
    settings["lm_port"]  = port

    print()
    display_name = ask(f"give this model a display name  [{model}] >")
    settings["display_name"] = display_name.strip() if display_name.strip() else model

    save_settings(settings)

    apis = load_apis()
    existing = next((i for i, a in enumerate(apis) if a["name"] == "LM Studio"), None)
    entry = {
        "name":   "LM Studio",
        "url":    url,
        "key":    "lm-studio",
        "models": models_available if models_available else [model]
    }
    if existing is not None:
        apis[existing] = entry
    else:
        apis.append(entry)
    save_apis(apis)

    print()
    ok("LM Studio configured")
    print(f"  {C.CYAN}host         : {host}{C.RESET}")
    print(f"  {C.CYAN}port         : {port}{C.RESET}")
    print(f"  {C.CYAN}model        : {model}{C.RESET}")
    print(f"  {C.CYAN}display name : {settings['display_name']}{C.RESET}")
    print(f"  {C.CYAN}url          : {url}{C.RESET}")
    print()
    pause()

# ============================================================
# BUILD
# ============================================================
def build():
    banner()
    print(f"\n{C.CYAN}{C.BOLD}  Build & Install{C.RESET}")
    sep()
    print()

    ensure_dirs()

    checks = [
        ("python",  ["python", "--version"]),
        ("pip",     ["pip",    "--version"]),
        ("gcc",     ["gcc",    "--version"]),
        ("g++",     ["g++",    "--version"]),
        ("node",    ["node",   "--version"]),
        ("git",     ["git",    "--version"]),
    ]

    for name, cmd in checks:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
            ver = r.stdout.strip().split("\n")[0][:40]
            ok(f"{name:<10} {C.GRAY}{ver}{C.RESET}")
        except FileNotFoundError:
            if name in ("python", "pip"):
                err(f"{name:<10} not found — required")
            else:
                warn(f"{name:<10} not found — optional")

    print()
    sep()
    print()
    info("installing python packages (requirements.txt)...")
    print()

    req = os.path.join(BASE_DIR, "requirements.txt")
    if os.path.exists(req):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", req],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok("requirements installed")
        else:
            err("pip install -r requirements.txt failed")
            if r.stderr:
                print(f"  {C.GRAY}{r.stderr[:200]}{C.RESET}")
    else:
        for pkg in ["requests", "colorama", "python-dotenv", "pyperclip"]:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg],
                           capture_output=True, text=True)
            ok(f"installed {pkg}")

    print()
    sep()
    print()
    info("creating folder structure...")
    print()

    for name, desc in DIRS.items():
        ok(f"{name:<12} {C.GRAY}{desc}{C.RESET}")
    info("data/ — config, sandbox, logs, memory, cache, runtime, scheduler")
    info("extensions/ — plugins, modules, api, bridge")

    # default settings — working_dir = sandbox
    if not os.path.exists(SETTINGS_FILE):
        save_settings({
            "api_key": "", "model": "", "url": "",
            "provider": "", "max_loop": 20, "max_tokens": 700,
            "temperature": 0.2, "save_history": True,
            "max_history_entries": 100,
            "working_dir": default_working_dir(),
            "stream": False,
        })
        ok("created data/config/settings.json (working_dir → data/sandbox/)")

    # copy layout doc if missing
    layout_src = os.path.join(BASE_DIR, "docs", "LAYOUT.txt")
    if os.path.exists(layout_src):
        info("docs/LAYOUT.txt — architecture diagram")

    print()
    sep()
    print()

    s = load_settings()
    if not s.get("api_key"):
        warn("no API configured yet — run [1] Setup API or [3] LM Studio")
    else:
        ok("build complete")
        print(f"  {C.CYAN}run:  scripts\\run.bat  or  python cli.py{C.RESET}")
        print(f"  {C.GRAY}docs: docs/LAYOUT.txt  docs/FOLDERS.txt{C.RESET}")

    print()
    pause()

# ============================================================
# VIEW CONFIG
# ============================================================
def view_config():
    banner()
    print(f"\n{C.CYAN}{C.BOLD}  Current Config{C.RESET}")
    sep()
    print()

    s = load_settings()
    if not s:
        err("no config found — run Build first")
        print()
        pause()
        return

    key = s.get("api_key", "")
    masked = key[:6] + "***" + key[-4:] if len(key) > 10 else "***"

    fields = [
        ("provider",    s.get("provider",    "not set")),
        ("model",       s.get("model",       "not set")),
        ("url",         s.get("url",         "not set")),
        ("api_key",     masked),
        ("max_tokens",  s.get("max_tokens",  "?")),
        ("temperature", s.get("temperature", "?")),
        ("max_loop",    s.get("max_loop",    "?")),
        ("save_history",s.get("save_history","?")),
    ]

    for k, v in fields:
        print(f"  {C.BOLD}{k:<20}{C.RESET}{C.GRAY}{v}{C.RESET}")

    apis = load_apis()
    if apis:
        print()
        sep()
        print(f"\n  {C.CYAN}configured providers:{C.RESET}\n")
        for a in apis:
            k   = a.get("key", "")
            mk  = k[:6] + "***" + k[-4:] if len(k) > 10 else "***"
            print(f"  {C.BOLD}{a['name']:<15}{C.RESET}{C.GRAY}{mk}  •  {len(a['models'])} models{C.RESET}")

    print()
    pause()

# ============================================================
# REMOVE API
# ============================================================
def remove_api():
    banner()
    print(f"\n{C.CYAN}{C.BOLD}  Remove API Provider{C.RESET}")
    sep()

    apis = load_apis()
    if not apis:
        err("no APIs configured")
        print()
        pause()
        return

    print()
    for i, a in enumerate(apis):
        print(f"  {C.CYAN}{i+1}{C.RESET}  {a['name']}")
    print(f"  {C.CYAN}0{C.RESET}  Back")
    print()

    choice = ask("select provider to remove >")
    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(apis):
            raise ValueError
        removed = apis.pop(idx)
        save_apis(apis)
        ok(f"removed {removed['name']}")
    except ValueError:
        err("invalid choice")

    print()
    pause()

# ============================================================
# RESET CONFIG
# ============================================================
def reset_config():
    banner()
    print(f"\n{C.RED}{C.BOLD}  Reset Config{C.RESET}")
    sep()
    print()
    warn("this will delete all config and APIs")
    print()
    confirm = ask("type YES to confirm >")
    if confirm == "YES":
        if os.path.exists(SETTINGS_FILE): os.remove(SETTINGS_FILE)
        if os.path.exists(APIS_FILE):     os.remove(APIS_FILE)
        ok("config reset")
    else:
        info("cancelled")
    print()
    pause()

# ============================================================
# ENTRY
# ============================================================
if __name__ == "__main__":
    # Enable ANSI on Windows
    if os.name == "nt":
        os.system("color")
        subprocess.run("", shell=True)
    menu()