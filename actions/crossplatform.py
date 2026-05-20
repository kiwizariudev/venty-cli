import os
import platform
import subprocess
import shutil
import datetime
import time

_OS = platform.system()


def _run(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


def _open_file_manager(path="."):
    if _OS == "Windows":
        return subprocess.Popen(f'explorer "{path}"', shell=True)
    elif _OS == "Darwin":
        return subprocess.Popen(["open", path])
    else:
        for fm in ("xdg-open", "nautilus", "thunar", "dolphin"):
            if shutil.which(fm):
                return subprocess.Popen([fm, path])


def _open_url(url):
    if _OS == "Windows":
        return subprocess.Popen(f"start {url}", shell=True)
    elif _OS == "Darwin":
        return subprocess.Popen(["open", url])
    else:
        return subprocess.Popen(["xdg-open", url])


def _open_app(app):
    if _OS == "Windows":
        return subprocess.Popen(app, shell=True)
    elif _OS == "Darwin":
        return subprocess.Popen(["open", "-a", app])
    else:
        return subprocess.Popen([app])


def _lock_screen():
    if _OS == "Windows":
        return subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], capture_output=True)
    elif _OS == "Darwin":
        return _run("pmset displaysleepnow")
    else:
        for cmd in ("gnome-screensaver-command -l", "xdg-screensaver lock", "loginctl lock-session"):
            if shutil.which(cmd.split()[0]):
                return _run(cmd)


def _get_cpu_usage():
    if _OS == "Windows":
        return _run("powershell (Get-WmiObject Win32_Processor).LoadPercentage")
    elif _OS == "Darwin":
        return _run("top -l 1 | grep 'CPU usage'")
    else:
        return _run("top -bn1 | grep 'Cpu(s)'")


def _get_ram_info():
    if _OS == "Windows":
        return _run("powershell (Get-WmiObject Win32_OperatingSystem | Select-Object FreePhysicalMemory,TotalVisibleMemorySize | Format-List)")
    elif _OS == "Darwin":
        return _run("vm_stat")
    else:
        return _run("free -h")


def _get_disk_info():
    if _OS == "Windows":
        return subprocess.run(["wmic", "logicaldisk", "get", "size,freespace,caption"], capture_output=True, text=True)
    else:
        return _run("df -h")


def _get_os_info():
    return _stdout(f"{platform.system()} {platform.release()} {platform.version()} {platform.machine()}")


def _get_uptime():
    if _OS == "Windows":
        return _run("powershell (Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime")
    elif _OS == "Darwin":
        return _run("uptime")
    else:
        return _run("uptime -p")


def _screenshot():
    if _OS == "Windows":
        return subprocess.Popen("snippingtool", shell=True)
    elif _OS == "Darwin":
        return subprocess.Popen(["screencapture", "-i", f"screenshot_{int(time.time())}.png"])
    else:
        for tool in ("gnome-screenshot", "scrot", "import"):
            if shutil.which(tool):
                return subprocess.Popen([tool])


def _clipboard_copy(text):
    if _OS == "Windows":
        return subprocess.run(["clip"], input=text.encode(), capture_output=True)
    elif _OS == "Darwin":
        return subprocess.run(["pbcopy"], input=text.encode(), capture_output=True)
    else:
        for tool in ("xclip -selection clipboard", "xsel --clipboard --input"):
            if shutil.which(tool.split()[0]):
                return subprocess.run(tool.split(), input=text.encode(), capture_output=True)


def _clipboard_get():
    if _OS == "Windows":
        return _run("powershell Get-Clipboard")
    elif _OS == "Darwin":
        return _run("pbpaste")
    else:
        for tool in ("xclip -selection clipboard -o", "xsel --clipboard --output"):
            if shutil.which(tool.split()[0]):
                return _run(tool)


def _notify(title, message):
    """Send a desktop notification."""
    if _OS == "Windows":
        ps = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
        return subprocess.Popen(f'powershell -Command "{ps}"', shell=True)
    elif _OS == "Darwin":
        return _run(f'osascript -e \'display notification "{message}" with title "{title}"\'')
    else:
        if shutil.which("notify-send"):
            return subprocess.Popen(["notify-send", title, message])


def _list_processes():
    if _OS == "Windows":
        return subprocess.run(["tasklist"], capture_output=True, text=True)
    else:
        return _run("ps aux")


def _kill_process(name):
    if _OS == "Windows":
        return subprocess.run(["taskkill", "/F", "/IM", name], capture_output=True, text=True)
    else:
        return _run(f"pkill -f {name}")


def _get_ip():
    if _OS == "Windows":
        return subprocess.run(["ipconfig"], capture_output=True, text=True)
    else:
        return _run("ip addr show" if shutil.which("ip") else "ifconfig")


def _flush_dns():
    if _OS == "Windows":
        return subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
    elif _OS == "Darwin":
        return _run("sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder")
    else:
        return _run("sudo systemd-resolve --flush-caches")


def _open_terminal():
    if _OS == "Windows":
        return subprocess.Popen("start cmd", shell=True)
    elif _OS == "Darwin":
        return subprocess.Popen(["open", "-a", "Terminal"])
    else:
        for term in ("gnome-terminal", "xterm", "konsole", "xfce4-terminal"):
            if shutil.which(term):
                return subprocess.Popen([term])


def _set_volume(level):
    """Set volume 0-100."""
    if _OS == "Windows":
        val = int(int(level) * 655.35)
        return subprocess.run(["nircmd", "setsysvolume", str(val)], capture_output=True, text=True)
    elif _OS == "Darwin":
        return _run(f"osascript -e 'set volume output volume {level}'")
    else:
        return _run(f"amixer -q sset Master {level}%")


def _sleep():
    if _OS == "Windows":
        return subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], capture_output=True, text=True)
    elif _OS == "Darwin":
        return _run("pmset sleepnow")
    else:
        return _run("systemctl suspend")


ACTIONS = {
    # ── Cross-platform system ─────────────────────────────────
    "xp_os_info":        {"description": "Get OS info (cross-platform)",                              "execute": lambda a: _get_os_info()},
    "xp_cpu_usage":      {"description": "Get CPU usage (cross-platform)",                            "execute": lambda a: _get_cpu_usage()},
    "xp_ram_info":       {"description": "Get RAM info (cross-platform)",                             "execute": lambda a: _get_ram_info()},
    "xp_disk_info":      {"description": "Get disk info (cross-platform)",                            "execute": lambda a: _get_disk_info()},
    "xp_uptime":         {"description": "Get system uptime (cross-platform)",                        "execute": lambda a: _get_uptime()},
    "xp_screenshot":     {"description": "Take a screenshot (cross-platform)",                        "execute": lambda a: _screenshot()},
    "xp_list_processes": {"description": "List running processes (cross-platform)",                   "execute": lambda a: _list_processes()},
    "xp_kill_process":   {"description": "Kill a process by name, args = [name] (cross-platform)",   "execute": lambda a: _kill_process(a[0])},
    "xp_lock_screen":    {"description": "Lock the screen (cross-platform)",                          "execute": lambda a: _lock_screen()},
    "xp_sleep":          {"description": "Sleep the computer (cross-platform)",                       "execute": lambda a: _sleep()},

    # ── Cross-platform network ────────────────────────────────
    "xp_ip_info":        {"description": "Get IP info (cross-platform)",                              "execute": lambda a: _get_ip()},
    "xp_flush_dns":      {"description": "Flush DNS cache (cross-platform)",                          "execute": lambda a: _flush_dns()},
    "xp_ping":           {"description": "Ping a host, args = [host] (cross-platform)",               "execute": lambda a: _run(f"ping {'- c 4' if _OS != 'Windows' else '-n 4'} {a[0]}")},

    # ── Cross-platform UI ─────────────────────────────────────
    "xp_open_url":       {"description": "Open URL in default browser, args = [url] (cross-platform)","execute": lambda a: _open_url(a[0])},
    "xp_open_app":       {"description": "Open an application, args = [app] (cross-platform)",        "execute": lambda a: _open_app(a[0])},
    "xp_open_folder":    {"description": "Open folder in file manager, args = [path] (cross-platform)","execute": lambda a: _open_file_manager(a[0] if a else ".")},
    "xp_open_terminal":  {"description": "Open a terminal window (cross-platform)",                   "execute": lambda a: _open_terminal()},
    "xp_notify":         {"description": "Send desktop notification, args = [title, message]",        "execute": lambda a: _notify(a[0], a[1] if len(a) > 1 else "")},
    "xp_set_volume":     {"description": "Set volume 0-100, args = [level] (cross-platform)",         "execute": lambda a: _set_volume(a[0])},

    # ── Cross-platform clipboard ──────────────────────────────
    "xp_clipboard_copy": {"description": "Copy text to clipboard, args = [text] (cross-platform)",   "execute": lambda a: _clipboard_copy(a[0])},
    "xp_clipboard_get":  {"description": "Get clipboard content (cross-platform)",                    "execute": lambda a: _clipboard_get()},

    # ── Cross-platform file utils ─────────────────────────────
    "xp_which":          {"description": "Check if a command exists, args = [command]",               "execute": lambda a: _stdout(shutil.which(a[0]) or f"{a[0]} not found")},
    "xp_env_var":        {"description": "Get environment variable, args = [VAR_NAME]",               "execute": lambda a: _stdout(f"{a[0]} = {os.environ.get(a[0], 'NOT SET')}")},
    "xp_set_env_var":    {"description": "Set env variable (session), args = [VAR_NAME, value]",      "execute": lambda a: [os.environ.update({a[0]: a[1]}), _stdout(f"Set {a[0]}={a[1]}")][-1]},
    "xp_get_cwd":        {"description": "Get current working directory",                             "execute": lambda a: _stdout(os.getcwd())},
    "xp_hostname":       {"description": "Get hostname",                                              "execute": lambda a: _stdout(platform.node())},
    "xp_python_version": {"description": "Get Python version",                                        "execute": lambda a: _stdout(platform.python_version())},
    "xp_get_time":       {"description": "Get current date and time",                                 "execute": lambda a: _stdout(datetime.datetime.now().strftime("%A %d %B %Y  %H:%M:%S"))},
}
