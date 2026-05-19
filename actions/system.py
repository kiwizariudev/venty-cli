"""
actions/system.py — system information (CPU, RAM, GPU, disk, env vars, etc.)
"""
import os
import platform
import subprocess
import datetime
import time


def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def _runl(args):
    return subprocess.run(args, capture_output=True, text=True)


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


ACTIONS = {
    "os_disk_info": {
        "description": "Get disk info",
        "execute": lambda a: _runl(["wmic", "logicaldisk", "get", "size,freespace,caption"]),
    },
    "os_disk_usage": {
        "description": "Get disk usage of a folder, args = [path]",
        "execute": lambda a: _run(f"powershell (Get-ChildItem -Recurse '{a[0]}' | Measure-Object -Property Length -Sum).Sum / 1MB"),
    },
    "os_cpu_info": {
        "description": "Get CPU info",
        "execute": lambda a: _runl(["wmic", "cpu", "get", "name,currentclockspeed,numberofcores,loadpercentage"]),
    },
    "os_cpu_usage": {
        "description": "Get CPU usage percentage",
        "execute": lambda a: _run("powershell (Get-WmiObject Win32_Processor).LoadPercentage"),
    },
    "os_ram_info": {
        "description": "Get RAM info",
        "execute": lambda a: _runl(["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory"]),
    },
    "os_ram_usage": {
        "description": "Get RAM usage",
        "execute": lambda a: _run("powershell (Get-WmiObject Win32_OperatingSystem | Select-Object FreePhysicalMemory,TotalVisibleMemorySize | Format-List)"),
    },
    "os_gpu_info": {
        "description": "Get GPU info",
        "execute": lambda a: _runl(["wmic", "path", "win32_videocontroller", "get", "name,adapterram,driverversion"]),
    },
    "os_os_info": {
        "description": "Get OS info",
        "execute": lambda a: _stdout(f"{platform.system()} {platform.release()} {platform.version()} {platform.machine()}"),
    },
    "os_uptime": {
        "description": "Get system uptime",
        "execute": lambda a: _run("powershell (Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime"),
    },
    "os_screenshot": {
        "description": "Open snipping tool for screenshot",
        "execute": lambda a: subprocess.Popen("snippingtool", shell=True),
    },
    "os_env_var": {
        "description": "Get env variable, args = [VAR_NAME]",
        "execute": lambda a: _stdout(f"{a[0]} = {os.environ.get(a[0], 'NOT SET')}"),
    },
    "os_set_env_var": {
        "description": "Set env variable (session only), args = [VAR_NAME, value]",
        "execute": lambda a: [os.environ.update({a[0]: a[1]}), _stdout(f"Set {a[0]}={a[1]}")][-1],
    },
    "os_list_env_vars": {
        "description": "List all environment variables",
        "execute": lambda a: _stdout("\n".join(f"{k}={v}" for k, v in os.environ.items())),
    },
    "os_installed_programs": {
        "description": "List installed programs",
        "execute": lambda a: _runl(["wmic", "product", "get", "name,version"]),
    },
    "os_drivers_list": {
        "description": "List installed drivers",
        "execute": lambda a: _runl(["driverquery"]),
    },
    "os_battery_info": {
        "description": "Get battery status",
        "execute": lambda a: _run("powershell Get-WmiObject Win32_Battery | Select-Object EstimatedChargeRemaining,BatteryStatus,TimeToFullCharge"),
    },
    "os_hotfix_list": {
        "description": "List installed Windows updates",
        "execute": lambda a: _runl(["wmic", "qfe", "list"]),
    },
    "os_startup_items": {
        "description": "List startup programs",
        "execute": lambda a: _run("wmic startup list full"),
    },
    "os_system_info": {
        "description": "Full system info",
        "execute": lambda a: _runl(["systeminfo"]),
    },
    "os_motherboard_info": {
        "description": "Get motherboard info",
        "execute": lambda a: _runl(["wmic", "baseboard", "get", "product,manufacturer,version"]),
    },
    "os_bios_info": {
        "description": "Get BIOS info",
        "execute": lambda a: _runl(["wmic", "bios", "get", "smbiosbiosversion,manufacturer,releasedate"]),
    },
    "os_get_time": {
        "description": "Get current date and time",
        "execute": lambda a: _stdout(datetime.datetime.now().strftime("%A %d %B %Y  %H:%M:%S")),
    },
    "os_get_timestamp": {
        "description": "Get Unix timestamp",
        "execute": lambda a: _stdout(str(int(time.time()))),
    },
    "os_set_timer": {
        "description": "Wait N seconds, args = [seconds]",
        "execute": lambda a: [time.sleep(int(a[0])), _stdout(f"Timer done after {a[0]}s")][-1],
    },
    "os_sync_time": {
        "description": "Sync system time with NTP",
        "execute": lambda a: _runl(["w32tm", "/resync"]),
    },
}
