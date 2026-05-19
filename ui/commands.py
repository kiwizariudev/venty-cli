"""
ui/commands.py — all built-in CLI commands (help, history, stats, config, etc.)
"""
import os

from core.config  import save_config, load_apis, load_keybinds, BASE_DIR
from core.history import load_history, clear_history, clear_cache, get_stats
from core.aliases import load_aliases, set_alias, remove_alias
from core.logger  import LOG_PATH, ERROR_PATH, SESSION_PATH, read_log_tail, clear_logs
from core.scheduler import list_jobs, cancel_job
from ui.colors    import (
    BOLD, RESET, _THEME,
    print_venty, print_success, print_error, print_warning, print_info, print_separator,
)


# ── actions ───────────────────────────────────────────────────────────────────

def cmd_actions(actions: dict) -> None:
    print(f"\n{_THEME['warning']}{BOLD}  actions ({len(actions)} total){RESET}")
    print_separator()
    categories = {
        "FILES":     [k for k in actions if any(x in k for x in ["file","folder","zip","unzip","tree","search","cwd","shortcut","explorer","duplicate"])],
        "PROCESS":   [k for k in actions if any(x in k for x in ["close","open","list_proc","kill","pid","priority","service","suspend","resume"])],
        "COMPILE":   [k for k in actions if any(x in k for x in ["compile","run_exe","run_python","run_node","run_batch","run_java","pip_","npm_","run_command","run_powershell"])],
        "GIT":       [k for k in actions if "git" in k],
        "NETWORK":   [k for k in actions if any(x in k for x in ["ping","ip","dns","wifi","port","netstat","arp","download","hostname","local_ip","my_ip","open_url"])],
        "SYSTEM":    [k for k in actions if any(x in k for x in ["cpu","ram","gpu","disk","os_info","uptime","battery","driver","hotfix","startup","motherboard","bios","system_info","screenshot","env","installed","time","timer","sync"])],
        "WINDOWS":   [k for k in actions if any(x in k for x in ["task_manager","control","device","services","event","registry","cmd","powershell","settings","calculator","notepad","paint","wordpad","sfc","chkdsk","update","display","sound","firewall","apps","bluetooth","network_set","person","privacy","magnifier","keyboard","charmap","cleanup","defrag","resource","performance","remote","snipping","narrator","scheduler","group","user","winver","reg_","recycle","explorer","shortcut","search_content"])],
        "POWER":     [k for k in actions if any(x in k for x in ["shutdown","restart","sleep","hibernate","lock","cancel_shutdown","logoff","volume"])],
        "CLIPBOARD": [k for k in actions if "clipboard" in k],
        "ENCODE":    [k for k in actions if any(x in k for x in ["base64","md5","sha256","sha1"])],
        "WEB":       [k for k in actions if k.startswith("web_")],
        "CONTROL":   ["loop_start", "cannot_do", "none"],
    }
    for cat, keys in categories.items():
        keys = [k for k in keys if k in actions]
        if not keys:
            continue
        print(f"\n  {_THEME['primary']}{BOLD}{cat}{RESET}")
        for k in keys:
            desc = actions[k]["description"][:65]
            print(f"  {_THEME['info']}  {BOLD}{k:<38}{RESET}{_THEME['info']}{desc}{RESET}")
    print_separator()


# ── history ───────────────────────────────────────────────────────────────────

def cmd_history() -> None:
    entries = load_history()
    if not entries:
        print_venty("no history saved yet")
        return
    print(f"\n{_THEME['warning']}{BOLD}  history ({len(entries)} entries){RESET}")
    print_separator()
    for e in entries[-20:]:
        role    = e.get("role", "?").upper()
        content = e.get("content", "")[:90].replace("\n", " ")
        color   = _THEME["user"] if role == "USER" else _THEME["primary"]
        print(f"  {color}{BOLD}{role:<12}{RESET}{_THEME['info']}{content}{RESET}")
    print_separator()


# ── logs ──────────────────────────────────────────────────────────────────────

def cmd_logs() -> None:
    lines = read_log_tail(LOG_PATH, 25)
    if not lines:
        print_venty("no logs yet")
        return
    print(f"\n{_THEME['warning']}{BOLD}  recent logs{RESET}")
    print_separator()
    for line in lines:
        print(f"  {_THEME['info']}{line.rstrip()}{RESET}")
    print_separator()


def cmd_errors() -> None:
    lines = read_log_tail(ERROR_PATH, 20)
    if not lines:
        print_venty("no errors logged")
        return
    print(f"\n{_THEME['warning']}{BOLD}  recent errors{RESET}")
    print_separator()
    for line in lines:
        print(f"  {_THEME['error']}{line.rstrip()}{RESET}")
    print_separator()


def cmd_sessions() -> None:
    lines = read_log_tail(SESSION_PATH, 30)
    if not lines:
        print_venty("no session log yet")
        return
    print(f"\n{_THEME['warning']}{BOLD}  session log{RESET}")
    print_separator()
    for line in lines:
        print(f"  {_THEME['info']}{line.rstrip()}{RESET}")
    print_separator()


# ── config ────────────────────────────────────────────────────────────────────

def cmd_config(cfg: dict) -> None:
    print(f"\n{_THEME['warning']}{BOLD}  config{RESET}")
    print_separator()
    for k, v in cfg.items():
        display = "***hidden***" if k == "api_key" else v
        print(f"  {BOLD}{k:<30}{RESET}{_THEME['info']}{display}{RESET}")
    print_separator()


def cmd_set(args_str: str, cfg: dict) -> None:
    parts = args_str.strip().split(" ", 1)
    if len(parts) < 2:
        print_error("usage: set <key> <value>")
        print_info("editable: temperature, max_tokens, max_loop, save_history, show_output, confirm_dangerous, timeout, working_dir, theme, max_session_turns")
        return
    key, val = parts[0], parts[1]
    editable = ["temperature", "max_tokens", "max_loop", "save_history", "show_output",
                "confirm_dangerous", "timeout", "working_dir", "theme", "max_session_turns"]
    if key not in editable:
        print_error(f"'{key}' is not editable here")
        return
    if key == "working_dir":
        if not os.path.isdir(val):
            print_error(f"directory not found: {val}")
            return
        cfg[key] = val
    else:
        try:
            if val.lower() in ("true", "false"):
                val = val.lower() == "true"
            elif "." in val:
                val = float(val)
            else:
                val = int(val)
        except Exception:
            pass
        cfg[key] = val
    save_config(cfg)
    print_success(f"set {key} = {cfg[key]}")


def cmd_reload(cfg: dict) -> dict:
    from core.config import load_config
    new_cfg = load_config()
    cfg.update(new_cfg)
    print_success("config reloaded")
    print_info(f"provider : {cfg.get('provider', 'unknown')}")
    print_info(f"model    : {cfg.get('model', 'unknown')}")
    return cfg


# ── stats ─────────────────────────────────────────────────────────────────────

def cmd_stats() -> None:
    s = get_stats()
    if s["total"] == 0:
        print_venty("no stats yet")
        return
    print(f"\n{_THEME['warning']}{BOLD}  stats{RESET}")
    print_separator()
    print(f"  {_THEME['info']}total actions  {_THEME['primary']}{BOLD}{s['total']}{RESET}")
    print(f"  {_THEME['info']}succeeded      {_THEME['success']}{s['success']}{RESET}")
    print(f"  {_THEME['info']}failed         {_THEME['error']}{s['failed']}{RESET}")
    print(f"\n  {_THEME['warning']}top actions:{RESET}")
    for name, count in s["top"]:
        bar = "█" * min(count, 25)
        print(f"  {_THEME['info']}  {name:<35}{_THEME['primary']}{bar}{RESET} {count}")
    print_separator()


# ── aliases ───────────────────────────────────────────────────────────────────

def cmd_aliases() -> None:
    aliases = load_aliases()
    if not aliases:
        print_venty("no aliases defined")
        print_info("use: alias <name> = <expansion>")
        return
    print(f"\n{_THEME['warning']}{BOLD}  aliases{RESET}")
    print_separator()
    for name, exp in aliases.items():
        print(f"  {BOLD}{name:<20}{RESET}{_THEME['info']}{exp}{RESET}")
    print_separator()


def cmd_alias_set(args_str: str) -> None:
    if "=" not in args_str:
        print_error("usage: alias <name> = <expansion>")
        return
    name, expansion = args_str.split("=", 1)
    name      = name.strip()
    expansion = expansion.strip()
    if not name or not expansion:
        print_error("name and expansion cannot be empty")
        return
    set_alias(name, expansion)
    print_success(f"alias '{name}' -> '{expansion}'")


def cmd_alias_remove(name: str) -> None:
    if remove_alias(name.strip()):
        print_success(f"removed alias '{name.strip()}'")
    else:
        print_error(f"alias '{name.strip()}' not found")


# ── scheduler ─────────────────────────────────────────────────────────────────

def cmd_jobs() -> None:
    jobs = list_jobs()
    if not jobs:
        print_venty("no scheduled jobs")
        return
    print(f"\n{_THEME['warning']}{BOLD}  scheduled jobs{RESET}")
    print_separator()
    for j in jobs:
        repeat = "repeat" if j.get("repeat") else "once"
        print(f"  {BOLD}{j['id']}{RESET}  {_THEME['info']}{j['label']}  [{repeat}]  run_at={j['run_at']}{RESET}")
    print_separator()


def cmd_cancel_job(job_id: str) -> None:
    if cancel_job(job_id.strip()):
        print_success(f"cancelled job {job_id.strip()}")
    else:
        print_error(f"job '{job_id.strip()}' not found")


# ── keybinds ──────────────────────────────────────────────────────────────────

def cmd_keybinds() -> None:
    kb = load_keybinds()
    print(f"\n{_THEME['warning']}{BOLD}  keybinds{RESET}")
    print_separator()
    for action, key in kb.items():
        print(f"  {BOLD}{action:<20}{RESET}{_THEME['info']}{key}{RESET}")
    print_separator()


# ── clear helpers ─────────────────────────────────────────────────────────────

def cmd_clear_history() -> None:
    clear_history()
    print_success("history cleared")


def cmd_clear_logs() -> None:
    clear_logs()
    print_success("logs cleared")


def cmd_clear_cache() -> None:
    clear_cache()
    print_success("cache cleared")


# ── help ──────────────────────────────────────────────────────────────────────

def cmd_help() -> None:
    print(f"\n{_THEME['warning']}{BOLD}  commands{RESET}")
    print_separator()
    cmds = [
        ("actions",              "list all available actions"),
        ("history",              "show conversation history"),
        ("sessions",             "show session log"),
        ("logs",                 "show recent log entries"),
        ("errors",               "show recent error entries"),
        ("config",               "show current configuration"),
        ("set <k> <v>",          "change a config value"),
        ("reload",               "reload config from settings.json"),
        ("stats",                "show action usage statistics"),
        ("aliases",              "list all aliases"),
        ("alias <name> = <exp>", "create an alias"),
        ("unalias <name>",       "remove an alias"),
        ("jobs",                 "list scheduled jobs"),
        ("cancel <job_id>",      "cancel a scheduled job"),
        ("keybinds",             "show keybinds"),
        ("clear",                "clear screen and reset session memory"),
        ("clear history",        "delete saved history file"),
        ("clear logs",           "clear log files"),
        ("clear cache",          "clear action cache"),
        ("help",                 "show this message"),
        ("exit",                 "quit Venty"),
    ]
    for cmd, desc in cmds:
        print(f"  {_THEME['primary']}{BOLD}{cmd:<28}{RESET}{_THEME['info']}{desc}{RESET}")
    print_separator()
