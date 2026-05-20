import subprocess

def _run(*args, **kwargs):
    return subprocess.run(list(args[0]), capture_output=True, text=True, **kwargs)

def _popen(cmd, **kwargs):
    return subprocess.Popen(cmd, shell=True, **kwargs)

def _stdout(text):
    return type("R", (), {"stdout": str(text)})()

ACTIONS = {
    "os_close": {
        "description": "Close a process by name, args = [process.exe]",
        "execute": lambda a: _run(["taskkill", "/F", "/IM", a[0]]),
    },
    "os_open": {
        "description": "Open an app or file, args = [app or path]",
        "execute": lambda a: _popen(a[0]),
    },
    "os_list_processes": {
        "description": "List running processes",
        "execute": lambda a: _run(["tasklist"]),
    },
    "os_kill_pid": {
        "description": "Kill process by PID, args = [pid]",
        "execute": lambda a: _run(["taskkill", "/F", "/PID", str(a[0])]),
    },
    "os_process_priority": {
        "description": "Set process priority, args = [process.exe, low|normal|high|realtime]",
        "execute": lambda a: _run(["wmic", "process", "where", f"name='{a[0]}'", "call", "setpriority", a[1]]),
    },
    "os_process_info": {
        "description": "Get info about a process, args = [process.exe]",
        "execute": lambda a: _run(["wmic", "process", "where", f"name='{a[0]}'", "get", "processid,workingsetsize,commandline"]),
    },
    "os_start_service": {
        "description": "Start a Windows service, args = [service_name]",
        "execute": lambda a: _run(["net", "start", a[0]]),
    },
    "os_stop_service": {
        "description": "Stop a Windows service, args = [service_name]",
        "execute": lambda a: _run(["net", "stop", a[0]]),
    },
    "os_list_services": {
        "description": "List all Windows services",
        "execute": lambda a: _run(["sc", "query", "type=", "all"]),
    },
    "os_service_status": {
        "description": "Get status of a service, args = [service_name]",
        "execute": lambda a: _run(["sc", "query", a[0]]),
    },
    "os_suspend_process": {
        "description": "Suspend a process (needs pssuspend), args = [process.exe]",
        "execute": lambda a: subprocess.run(f"pssuspend {a[0]}", shell=True, capture_output=True, text=True),
    },
    "os_resume_process": {
        "description": "Resume a suspended process, args = [process.exe]",
        "execute": lambda a: subprocess.run(f"pssuspend -r {a[0]}", shell=True, capture_output=True, text=True),
    },
}
