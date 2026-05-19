"""
ui/colors.py — ANSI color codes, theme support, and all print helpers
"""
import random

# ── Raw ANSI codes ────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# theme-aware codes are set by apply_theme()
_THEME = {
    "primary":   "\033[96m",
    "secondary": "\033[95m",
    "success":   "\033[92m",
    "error":     "\033[91m",
    "warning":   "\033[93m",
    "info":      "\033[90m",
    "user":      "\033[94m",
}

VENTY_POOL = ["\033[96m", "\033[95m", "\033[94m", "\033[92m", "\033[93m"]


def apply_theme(theme_data: dict) -> None:
    """Load a theme dict (from config/themes.json) into the active palette."""
    for key, code in theme_data.items():
        if key in _THEME:
            _THEME[key] = f"\033[{code}m"


def vc() -> str:
    return random.choice(VENTY_POOL)


# ── Print helpers ─────────────────────────────────────────────────────────────

def print_venty(message: str) -> None:
    c = vc()
    print(f"\n{c}{BOLD}Venty >{RESET} {c}{message}{RESET}")


def print_success(msg: str) -> None:
    print(f"{_THEME['success']}  + {msg}{RESET}")


def print_error(msg: str) -> None:
    print(f"{_THEME['error']}  x {msg}{RESET}")


def print_warning(msg: str) -> None:
    print(f"{_THEME['warning']}  ! {msg}{RESET}")


def print_info(msg: str) -> None:
    print(f"{_THEME['info']}  > {msg}{RESET}")


def print_output(text: str) -> None:
    print(f"\n{_THEME['info']}{text}{RESET}")


def print_action(action: str, args: list) -> None:
    args_str = ", ".join(str(a) for a in args) if args else "no args"
    print(f"{_THEME['warning']}  * action: {BOLD}{action}{RESET}{_THEME['warning']} -> [{args_str}]{RESET}")


def print_loop_step(i: int, total: int, action: str, args: list) -> None:
    args_str = ", ".join(str(a) for a in args) if args else "no args"
    print(f"{_THEME['secondary']}  loop [{i}/{total}] {BOLD}{action}{RESET}{_THEME['secondary']} -> [{args_str}]{RESET}")


def print_separator() -> None:
    print(f"{_THEME['info']}  {'—' * 52}{RESET}")


def print_banner(provider: str = "", model: str = "not configured") -> None:
    c = vc()
    print(f"""
{c}{BOLD}
  ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗
  ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝
  ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝
  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝
   ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║
    ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝
{RESET}{_THEME['info']}  AI Desktop Assistant  •  {provider if provider else "Venty"}  •  {model}
{RESET}""")
