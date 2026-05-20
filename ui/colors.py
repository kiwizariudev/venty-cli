"""
ui/colors.py — ANSI color codes, theme support, and all print helpers
"""
import random

try:
    from rich.console import Console
    from rich.panel   import Panel
    from rich.progress import Progress, BarColumn, TextColumn
    _HAS_RICH = True
    _console = Console()
except ImportError:
    _HAS_RICH = False

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

class Colors:
    PRIMARY   = _THEME["primary"]
    SECONDARY = _THEME["secondary"]
    SUCCESS   = _THEME["success"]
    ERROR     = _THEME["error"]
    WARNING   = _THEME["warning"]
    INFO      = _THEME["info"]
    USER      = _THEME["user"]
    YELLOW    = "\033[93m"
    RESET     = "\033[0m"
    BOLD      = "\033[1m"

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
    if _HAS_RICH:
        _console.print(Panel(message, title="[bold cyan]Venty[/bold cyan]", border_style="cyan"))
    else:
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


def print_step(current: int, total: int, title: str) -> None:
    """Print a progress step for multi-step plans."""
    if _HAS_RICH:
        _console.print(f"[bold cyan][{current}/{total}][/bold cyan] [white]{title}[/white]")
    else:
        bar_width = 20
        filled = int(bar_width * current / total)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"{_THEME['info']}  [{bar}] {current}/{total} : {BOLD}{title}{RESET}")


def print_loop_step(i: int, total: int, action: str, args: list) -> None:
    args_str = ", ".join(str(a) for a in args) if args else "no args"
    print(f"{_THEME['secondary']}  loop [{i}/{total}] {BOLD}{action}{RESET}{_THEME['secondary']} -> [{args_str}]{RESET}")


def print_separator() -> None:
    print(f"{_THEME['info']}  {'—' * 52}{RESET}")


def print_banner(provider: str = "", model: str = "not configured") -> None:
    c = vc()
    # Integrated Side-by-Side Banner with Mascot
    banner_lines = [
        f"  {c} .~~~.     {c}{BOLD} ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗",
        f"  {c}(o . o)    {c}{BOLD} ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝",
        f"  {c} ) v (     {c}{BOLD} ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝",
        f"  {c}~~ ~ ~~    {c}{BOLD} ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝ ",
        f"  {c}~ ~ ~ ~ ~  {c}{BOLD}  ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║  ",
        f"  {c}           {c}{BOLD}   ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝  "
    ]
    
    print("\n" + "\n".join(banner_lines))
    print(f"{RESET}{_THEME['info']}                        Welcome to the new Venty CLI UX! /help to learn more.")
    print(f"{RESET}{_THEME['info']}                             AI Desktop Assistant  •  {provider if provider else 'Venty'}  •  {model}")
    print_separator()
