import json
import os
import sys
import subprocess
import random

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR  = os.path.join(BASE_DIR, "data", "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.json")
THEMES_PATH = os.path.join(CONFIG_DIR, "themes.json")
PLUGINS_DIR = os.path.join(BASE_DIR, "extensions", "plugins")
BRIDGE_DIR  = os.path.join(BASE_DIR, "bridge")
ENGINE_DIR  = os.path.join(BASE_DIR, "engine")

R  = "\033[0m"
B  = "\033[1m"
D  = "\033[2m"
COLORS = ["\033[96m", "\033[95m", "\033[94m", "\033[92m", "\033[93m"]

def _c(): return random.choice(COLORS)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def load_json(path):
    if not os.path.exists(path): return {}
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def sep(char="─", width=54):
    print(f"  {D}{'─' * width}{R}")

def header(title=""):
    c = _c()
    pet = [
        f"  {c} /\\_/\\  {R}",
        f"  {c}( o.o ) {R}",
        f"  {c} > ^ <  {R}",
        f"  {c}  ~~~   {R}",
        f"          ",
        f"          ",
    ]
    logo = [
        f"{c}{B}██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗{R}",
        f"{c}{B}██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝{R}",
        f"{c}{B}██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝ {R}",
        f"{c}{B}╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝  {R}",
        f"{c}{B} ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║   {R}",
        f"{c}{B}  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝  {R}",
    ]
    print()
    for i in range(len(logo)):
        print(f"{pet[i]}{logo[i]}")
    print(f"\n  {D}Config Lab  •  Management & Build Tool{R}")
    if title:
        print(f"\n  {c}{B}{title}{R}")
    sep()

def ask(prompt, default=""):
    val = input(f"  {B}{prompt}{R} [{D}{default}{R}] › ").strip()
    return val if val else default

def ask_secret(prompt):
    import getpass
    return getpass.getpass(f"  {B}{prompt}{R} › ")

def confirm(prompt):
    val = input(f"  {B}{prompt}{R} [y/N] › ").strip().lower()
    return val == "y"

def pause():
    input(f"\n  {D}Press Enter to continue...{R}")

def ok(msg):   print(f"  \033[92m✔  {msg}{R}")
def err(msg):  print(f"  \033[91m✘  {msg}{R}")
def warn(msg): print(f"  \033[93m⚠  {msg}{R}")
def info(msg): print(f"  {D}›  {msg}{R}")

def menu_item(key, label, desc="", active=False):
    c = "\033[96m" if not active else "\033[92m"
    bullet = "●" if active else " "
    desc_str = f"  {D}{desc}{R}" if desc else ""
    print(f"  {c}{B}{key}{R}  {bullet} {B}{label}{R}{desc_str}")


def main_menu():
    while True:
        clear()
        header()
        print()
        menu_item("1", "Themes",   "Change CLI appearance")
        menu_item("2", "Plugins",  "Enable / Disable extensions")
        menu_item("3", "Agent",    "Temperature, tokens, streaming")
        menu_item("4", "API",      "Keys, models, endpoints")
        menu_item("5", "Services", "Bridge web UI, C++ engine")
        menu_item("6", "Build",    "Install deps & setup project")
        menu_item("0", "Exit")
        sep()
        choice = input(f"\n  {B}›{R} ").strip()
        if choice == "1": theme_menu()
        elif choice == "2": plugin_menu()
        elif choice == "3": agent_menu()
        elif choice == "4": api_menu()
        elif choice == "5": services_menu()
        elif choice == "6": build_menu()
        elif choice == "0": break


def theme_menu():
    themes = load_json(THEMES_PATH)
    if not themes:
        themes = {
            "default": {}, "dark": {}, "matrix": {}, "ocean": {}
        }
    cfg = load_json(CONFIG_PATH)
    active = cfg.get("theme", "default")
    while True:
        clear()
        header("Themes")
        print()
        theme_names = list(themes.keys())
        for i, t in enumerate(theme_names, 1):
            is_active = t == active
            menu_item(str(i), t, "ACTIVE" if is_active else "", active=is_active)
        menu_item("0", "Back")
        sep()
        choice = input(f"\n  {B}›{R} ").strip()
        if choice == "0": break
        if choice.isdigit() and 1 <= int(choice) <= len(theme_names):
            selected = theme_names[int(choice) - 1]
            cfg["theme"] = selected
            active = selected
            save_json(CONFIG_PATH, cfg)
            ok(f"Theme set to {selected}")
            pause()


def plugin_menu():
    cfg = load_json(CONFIG_PATH)
    disabled = cfg.get("disabled_plugins", [])
    while True:
        clear()
        header("Plugins")
        print()
        if not os.path.isdir(PLUGINS_DIR):
            warn("plugins directory not found")
            pause()
            break
        plugins = sorted([f for f in os.listdir(PLUGINS_DIR)
                          if f.endswith(".py") and not f.startswith("_")])
        if not plugins:
            info("no plugins found in extensions/plugins/")
            pause()
            break
        for i, p in enumerate(plugins, 1):
            is_off = p in disabled
            status = f"\033[91mDISABLED{R}" if is_off else f"\033[92mENABLED{R}"
            print(f"  \033[96m{B}{i}{R}  {p:<35} {status}")
        menu_item("0", "Back")
        sep()
        info("Enter number to toggle")
        choice = input(f"\n  {B}›{R} ").strip()
        if choice == "0": break
        if choice.isdigit() and 1 <= int(choice) <= len(plugins):
            p_name = plugins[int(choice) - 1]
            if p_name in disabled:
                disabled.remove(p_name)
                ok(f"Enabled {p_name}")
            else:
                disabled.append(p_name)
                warn(f"Disabled {p_name}")
            cfg["disabled_plugins"] = disabled
            save_json(CONFIG_PATH, cfg)


def agent_menu():
    while True:
        cfg = load_json(CONFIG_PATH)
        clear()
        header("Agent Settings")
        print()
        menu_item("1", "Temperature",     f"current: {cfg.get('temperature', 0.2)}")
        menu_item("2", "Max Tokens",      f"current: {cfg.get('max_tokens', 700)}")
        menu_item("3", "Max Loop",        f"current: {cfg.get('max_loop', 20)}")
        menu_item("4", "Session Turns",   f"current: {cfg.get('max_session_turns', 40)}")
        menu_item("5", "Streaming",       f"current: {'ON' if cfg.get('stream', True) else 'OFF'}")
        menu_item("6", "Show Output",     f"current: {'ON' if cfg.get('show_output', True) else 'OFF'}")
        menu_item("0", "Back")
        sep()
        choice = input(f"\n  {B}›{R} ").strip()
        if choice == "0": break
        elif choice == "1":
            v = ask("Temperature (0.0 - 1.0)", str(cfg.get("temperature", 0.2)))
            try: cfg["temperature"] = float(v); save_json(CONFIG_PATH, cfg); ok(f"Temperature → {v}")
            except: err("Invalid value")
        elif choice == "2":
            v = ask("Max tokens", str(cfg.get("max_tokens", 700)))
            try: cfg["max_tokens"] = int(v); save_json(CONFIG_PATH, cfg); ok(f"Max tokens → {v}")
            except: err("Invalid value")
        elif choice == "3":
            v = ask("Max loop", str(cfg.get("max_loop", 20)))
            try: cfg["max_loop"] = int(v); save_json(CONFIG_PATH, cfg); ok(f"Max loop → {v}")
            except: err("Invalid value")
        elif choice == "4":
            v = ask("Max session turns", str(cfg.get("max_session_turns", 40)))
            try: cfg["max_session_turns"] = int(v); save_json(CONFIG_PATH, cfg); ok(f"Session turns → {v}")
            except: err("Invalid value")
        elif choice == "5":
            cfg["stream"] = not cfg.get("stream", True)
            save_json(CONFIG_PATH, cfg)
            ok(f"Streaming → {'ON' if cfg['stream'] else 'OFF'}")
        elif choice == "6":
            cfg["show_output"] = not cfg.get("show_output", True)
            save_json(CONFIG_PATH, cfg)
            ok(f"Show output → {'ON' if cfg['show_output'] else 'OFF'}")
        pause()


def api_menu():
    while True:
        cfg = load_json(CONFIG_PATH)
        key = cfg.get("api_key", "")
        masked = key[:6] + "***" + key[-4:] if len(key) > 10 else ("set" if key else "empty")
        clear()
        header("API Configuration")
        print()
        menu_item("1", "Provider",     f"current: {cfg.get('provider', 'not set')}")
        menu_item("2", "Model",        f"current: {cfg.get('model', 'not set')}")
        menu_item("3", "Display Name", f"current: {cfg.get('display_name', 'not set')}")
        menu_item("4", "Endpoint URL", f"current: {cfg.get('url', 'not set')[:50]}")
        menu_item("5", "API Key",      f"current: {masked}")
        menu_item("0", "Back")
        sep()
        choice = input(f"\n  {B}›{R} ").strip()
        if choice == "0": break
        elif choice == "1":
            v = ask("Provider name", cfg.get("provider", ""))
            cfg["provider"] = v; save_json(CONFIG_PATH, cfg); ok(f"Provider → {v}")
        elif choice == "2":
            v = ask("Model ID", cfg.get("model", ""))
            cfg["model"] = v; save_json(CONFIG_PATH, cfg); ok(f"Model → {v}")
        elif choice == "3":
            v = ask("Display name (shown in banner)", cfg.get("display_name", ""))
            cfg["display_name"] = v; save_json(CONFIG_PATH, cfg); ok(f"Display name → {v}")
        elif choice == "4":
            v = ask("Endpoint URL", cfg.get("url", ""))
            cfg["url"] = v; save_json(CONFIG_PATH, cfg); ok(f"URL updated")
        elif choice == "5":
            v = ask_secret("Paste API key")
            if v: cfg["api_key"] = v; save_json(CONFIG_PATH, cfg); ok("API key saved")
            else: warn("No key entered")
        pause()


def services_menu():
    while True:
        cfg = load_json(CONFIG_PATH)
        bridge_built = os.path.isdir(os.path.join(BRIDGE_DIR, "dist"))
        engine_built = os.path.isfile(os.path.join(ENGINE_DIR,
            "venty_engine.exe" if os.name == "nt" else "venty_engine"))
        clear()
        header("Services")
        print()
        bridge_status = f"\033[92mbuilt{R}" if bridge_built else f"\033[91mnot built{R}"
        engine_status = f"\033[92mbuilt{R}" if engine_built else f"\033[91mnot built{R}"
        bridge_enabled = cfg.get("enable_bridge", True)
        bridge_port    = cfg.get("bridge_port", 7432)

        menu_item("1", "Bridge (Web UI)",
                  f"{'ENABLED' if bridge_enabled else 'DISABLED'}  •  port {bridge_port}  •  {bridge_status}")
        menu_item("2", "Bridge Port",     f"current: {bridge_port}")
        menu_item("3", "Build Bridge",    "npm install + tsc (requires node.js)")
        menu_item("4", "Build Engine",    f"compile C++ venty_engine  •  {engine_status}")
        menu_item("0", "Back")
        sep()
        choice = input(f"\n  {B}›{R} ").strip()
        if choice == "0": break
        elif choice == "1":
            cfg["enable_bridge"] = not bridge_enabled
            save_json(CONFIG_PATH, cfg)
            ok(f"Bridge → {'ENABLED' if cfg['enable_bridge'] else 'DISABLED'}")
            pause()
        elif choice == "2":
            v = ask("Bridge port", str(bridge_port))
            try: cfg["bridge_port"] = int(v); save_json(CONFIG_PATH, cfg); ok(f"Port → {v}")
            except: err("Invalid port")
            pause()
        elif choice == "3":
            print()
            info("Running npm install...")
            r = subprocess.run("npm install", shell=True, cwd=BRIDGE_DIR)
            if r.returncode == 0:
                info("Building TypeScript...")
                r2 = subprocess.run("npm run build", shell=True, cwd=BRIDGE_DIR)
                if r2.returncode == 0: ok("Bridge built successfully")
                else: err("Build failed")
            else:
                err("npm install failed — is node.js installed?")
            pause()
        elif choice == "4":
            print()
            info("Building C++ engine...")
            if os.name == "nt":
                r = subprocess.run("build.bat", shell=True, cwd=ENGINE_DIR)
            else:
                r = subprocess.run("bash build.sh", shell=True, cwd=ENGINE_DIR)
            if r.returncode == 0: ok("Engine built: engine/venty_engine")
            else: err("Build failed — is g++ installed?")
            pause()


def build_menu():
    clear()
    header("Build & Install")
    print()
    info("Checking tools...")
    print()
    for name, cmd in [("python", "python --version"), ("pip", "pip --version"),
                      ("node", "node --version"), ("npm", "npm --version"),
                      ("gcc/g++", "g++ --version"), ("git", "git --version")]:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            ver = r.stdout.strip().split("\n")[0][:40]
            ok(f"{name:<10} {ver}")
        else:
            warn(f"{name:<10} not found")
    print()
    sep()
    print()
    if not confirm("Install Python dependencies?"):
        return
    pkgs = ["requests", "colorama", "python-dotenv"]
    for pkg in pkgs:
        r = subprocess.run(f"pip install {pkg}", shell=True, capture_output=True)
        if r.returncode == 0: ok(f"installed {pkg}")
        else: err(f"failed {pkg}")
    print()
    info("Creating folder structure...")
    for folder in ["data/config", "data/memory", "data/logs", "data/cache",
                   "data/sandbox", "data/runtime", "data/scheduler",
                   "extensions/plugins", "extensions/modules"]:
        os.makedirs(os.path.join(BASE_DIR, folder.replace("/", os.sep)), exist_ok=True)
    ok("Folders ready")
    print()
    ok("Build complete — run: python cli.py")
    pause()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n  {D}Exited.{R}\n")
