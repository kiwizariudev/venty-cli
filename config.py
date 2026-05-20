import json
import os
import sys
import subprocess
import random
import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
    from rich import print as rprint
    _HAS_RICH = True
    console = Console()
except ImportError:
    _HAS_RICH = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "data", "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.json")
THEMES_PATH = os.path.join(CONFIG_DIR, "themes.json")
PLUGINS_DIR = os.path.join(BASE_DIR, "extensions", "plugins")

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_color():
    return random.choice(["cyan", "magenta", "blue", "green", "yellow"])

def print_header():
    c = get_color()
    logo = f"""
[{c}]           ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗
           ██║   ██║██╔════╝████╗  ██║╚══██╔══╝╚██╗ ██╔╝
           ██║   ██║█████╗  ██╔██╗ ██║   ██║    ╚████╔╝
           ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║     ╚██╔╝
            ╚████╔╝ ███████╗██║ ╚████║   ██║      ██║
             ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ╚═╝[/{c}]
"""
    if _HAS_RICH:
        console.print(logo)
        console.print(f"[dim]             Config Lab • Management & Build Tool[/dim]", justify="center")
        console.print("[dim]  " + "—" * 80 + "[/dim]")
    else:
        print(logo)
        print("             Config Lab • Management & Build Tool")

def main_menu():
    while True:
        clear()
        print_header()
        table = Table(box=None, show_header=False, padding=(0, 2))
        table.add_row("[cyan]1[/cyan]", "Themes", "[dim]Change CLI appearance[/dim]")
        table.add_row("[cyan]2[/cyan]", "Plugins", "[dim]Enable/Disable extensions[/dim]")
        table.add_row("[cyan]3[/cyan]", "Agent", "[dim]Temperature, Max Tokens, Instructions[/dim]")
        table.add_row("[cyan]4[/cyan]", "API", "[dim]Keys, Models, Endpoints[/dim]")
        table.add_row("[cyan]5[/cyan]", "Build", "[dim]Install deps & Setup project[/dim]")
        table.add_row("[cyan]0[/cyan]", "Exit", "")
        if _HAS_RICH:
            console.print(Panel(table, title="[bold]Main Menu[/bold]", border_style="blue", expand=False))
            choice = Prompt.ask("\n[bold blue]Choice[/bold blue]", choices=["1", "2", "3", "4", "5", "0"], default="0")
        else:
            print("\n1. Themes\n2. Plugins\n3. Agent\n4. API\n5. Build\n0. Exit")
            choice = input("\nChoice > ")
        if choice == "1": theme_menu()
        elif choice == "2": plugin_menu()
        elif choice == "3": agent_menu()
        elif choice == "4": api_menu()
        elif choice == "5": build_menu()
        elif choice == "0": break

def theme_menu():
    themes = load_json(THEMES_PATH)
    cfg = load_json(CONFIG_PATH)
    active_theme = cfg.get("theme", "default")
    clear()
    print_header()
    table = Table(title="[bold blue]Theme Selection[/bold blue]", box=None)
    table.add_column("#", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    theme_names = list(themes.keys())
    for i, t in enumerate(theme_names, 1):
        status = "● ACTIVE" if t == active_theme else ""
        table.add_row(str(i), t, status)
    if _HAS_RICH:
        console.print(table)
        choice = Prompt.ask("\nSelect theme # or name (0 to back)", default="0")
    else:
        choice = input("\nSelect theme # (0 to back) > ")
    if choice == "0" or not choice: return
    selected = None
    if choice.isdigit() and 1 <= int(choice) <= len(theme_names):
        selected = theme_names[int(choice)-1]
    elif choice in themes:
        selected = choice
    if selected:
        cfg['theme'] = selected
        save_json(CONFIG_PATH, cfg)
        if _HAS_RICH: rprint(f"[green]✔[/green] Theme set to [bold]{selected}[/bold]")
    if _HAS_RICH: console.input("\n[dim]Press Enter...[/dim]")
    else: input("\nPress Enter...")

def plugin_menu():
    cfg = load_json(CONFIG_PATH)
    disabled = cfg.get("disabled_plugins", [])
    while True:
        clear()
        print_header()
        plugins = [f for f in os.listdir(PLUGINS_DIR) if f.endswith(".py") and not f.startswith("_")]
        table = Table(title="[bold blue]Plugin Manager[/bold blue]", box=None)
        table.add_column("#", style="cyan")
        table.add_column("Plugin", style="white")
        table.add_column("Status", style="green")
        for i, p in enumerate(plugins, 1):
            is_off = p in disabled
            status = "[red]DISABLED[/red]" if is_off else "[green]ENABLED[/green]"
            table.add_row(str(i), p, status)
        if _HAS_RICH:
            console.print(table)
            choice = Prompt.ask("\nEnter # to toggle status (0 to back)", default="0")
        else:
            choice = input("\nEnter # to toggle (0 to back) > ")
        if choice == "0" or not choice: break
        if choice.isdigit() and 1 <= int(choice) <= len(plugins):
            p_name = plugins[int(choice)-1]
            if p_name in disabled: disabled.remove(p_name)
            else: disabled.append(p_name)
            cfg["disabled_plugins"] = disabled
            save_json(CONFIG_PATH, cfg)

def agent_menu():
    cfg = load_json(CONFIG_PATH)
    clear()
    print_header()
    table = Table(box=None, show_header=False)
    table.add_row("[cyan]1[/cyan]", "Temperature", f"[bold]{cfg.get('temperature', 0.2)}[/bold]")
    table.add_row("[cyan]2[/cyan]", "Max Tokens", f"[bold]{cfg.get('max_tokens', 700)}[/bold]")
    table.add_row("[cyan]3[/cyan]", "Streaming", f"[bold]{'ON' if cfg.get('stream', True) else 'OFF'}[/bold]")
    if _HAS_RICH:
        console.print(Panel(table, title="[bold blue]Agent Settings[/bold blue]", border_style="blue"))
        choice = Prompt.ask("\nChoice (0 to back)", choices=["1", "2", "3", "0"], default="0")
        if choice == "1":
            cfg['temperature'] = FloatPrompt.ask("New temperature (0.0 - 1.0)", default=cfg.get('temperature', 0.2))
        elif choice == "2":
            cfg['max_tokens'] = IntPrompt.ask("New max tokens", default=cfg.get('max_tokens', 700))
        elif choice == "3":
            cfg['stream'] = not cfg.get('stream', True)
    if choice in ["1", "2", "3"]:
        save_json(CONFIG_PATH, cfg)
        rprint("[green]✔[/green] Settings updated")
    if _HAS_RICH: console.input("\n[dim]Press Enter...[/dim]")

def api_menu():
    cfg = load_json(CONFIG_PATH)
    clear()
    print_header()
    table = Table(box=None, show_header=False)
    table.add_row("[cyan]1[/cyan]", "Provider", f"[bold]{cfg.get('provider', 'Not set')}[/bold]")
    table.add_row("[cyan]2[/cyan]", "Model", f"[bold]{cfg.get('model', 'Not set')}[/bold]")
    table.add_row("[cyan]3[/cyan]", "URL", f"[bold]{cfg.get('url', 'Not set')}[/bold]")
    table.add_row("[cyan]4[/cyan]", "API Key", f"[bold]{'********' if cfg.get('api_key') else 'Empty'}[/bold]")
    if _HAS_RICH:
        console.print(Panel(table, title="[bold blue]API Configuration[/bold blue]", border_style="blue"))
        choice = Prompt.ask("\nChoice (0 to back)", choices=["1", "2", "3", "4", "0"], default="0")
        if choice == "1": cfg['provider'] = Prompt.ask("Provider Name", default=cfg.get('provider'))
        elif choice == "2": cfg['model'] = Prompt.ask("Model ID", default=cfg.get('model'))
        elif choice == "3": cfg['url'] = Prompt.ask("Endpoint URL", default=cfg.get('url'))
        elif choice == "4": cfg['api_key'] = Prompt.ask("API Key", password=True)
    if choice in ["1", "2", "3", "4"]:
        save_json(CONFIG_PATH, cfg)
        rprint("[green]✔[/green] API updated")
    if _HAS_RICH: console.input("\n[dim]Press Enter...[/dim]")

def build_menu():
    clear()
    print_header()
    rprint("[bold blue]Build System[/bold blue]")
    if _HAS_RICH:
        if not Confirm.ask("Start build process?"): return
    rprint("[yellow]>[/yellow] Checking directories...")
    from core.paths import ensure_dirs
    ensure_dirs()
    rprint("[green]✔[/green] Directories OK")
    rprint("[yellow]>[/yellow] Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        rprint("[green]✔[/green] Dependencies installed")
    except Exception as e:
        rprint(f"[red]x[/red] Installation failed: {e}")
    rprint("\n[bold green]Build Complete![/bold green]")
    if _HAS_RICH: console.input("\n[dim]Press Enter...[/dim]")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        rprint("\n[dim]Exited.[/dim]")
