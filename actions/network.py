"""
actions/network.py — network diagnostics and connectivity
"""
import subprocess
import socket


def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def _runl(args):
    return subprocess.run(args, capture_output=True, text=True)


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


ACTIONS = {
    "os_ip_info": {
        "description": "Get IP info",
        "execute": lambda a: _runl(["ipconfig"]),
    },
    "os_ip_info_all": {
        "description": "Get full IP info",
        "execute": lambda a: _runl(["ipconfig", "/all"]),
    },
    "os_ping": {
        "description": "Ping a host, args = [host]",
        "execute": lambda a: _runl(["ping", "-n", "4", a[0]]),
    },
    "os_ping_continuous": {
        "description": "Ping N times, args = [host, count]",
        "execute": lambda a: _runl(["ping", "-n", a[1] if len(a) > 1 else "10", a[0]]),
    },
    "os_flush_dns": {
        "description": "Flush DNS cache",
        "execute": lambda a: _runl(["ipconfig", "/flushdns"]),
    },
    "os_trace_route": {
        "description": "Trace route to host, args = [host]",
        "execute": lambda a: _runl(["tracert", a[0]]),
    },
    "os_netstat": {
        "description": "Show network connections",
        "execute": lambda a: _runl(["netstat", "-an"]),
    },
    "os_netstat_ports": {
        "description": "Show listening TCP ports",
        "execute": lambda a: _runl(["netstat", "-an", "-p", "TCP"]),
    },
    "os_wifi_list": {
        "description": "List wifi networks",
        "execute": lambda a: _runl(["netsh", "wlan", "show", "networks"]),
    },
    "os_wifi_profile": {
        "description": "Show wifi password, args = [wifi_name]",
        "execute": lambda a: _runl(["netsh", "wlan", "show", "profile", a[0], "key=clear"]),
    },
    "os_wifi_connect": {
        "description": "Connect to wifi, args = [wifi_name]",
        "execute": lambda a: _runl(["netsh", "wlan", "connect", f"name={a[0]}"]),
    },
    "os_wifi_disconnect": {
        "description": "Disconnect from wifi",
        "execute": lambda a: _runl(["netsh", "wlan", "disconnect"]),
    },
    "os_open_port_check": {
        "description": "Check if port is open, args = [host, port]",
        "execute": lambda a: _run(f"powershell Test-NetConnection -ComputerName {a[0]} -Port {a[1]}"),
    },
    "os_dns_lookup": {
        "description": "DNS lookup for a domain, args = [domain]",
        "execute": lambda a: _run(f"nslookup {a[0]}"),
    },
    "os_my_ip": {
        "description": "Get your public IP",
        "execute": lambda a: _run("powershell (Invoke-WebRequest -Uri 'https://api.ipify.org').Content"),
    },
    "os_local_ip": {
        "description": "Get local IP address",
        "execute": lambda a: _stdout(socket.gethostbyname(socket.gethostname())),
    },
    "os_hostname": {
        "description": "Get computer hostname",
        "execute": lambda a: _stdout(socket.gethostname()),
    },
    "os_arp_table": {
        "description": "Show ARP table",
        "execute": lambda a: _runl(["arp", "-a"]),
    },
    "os_ipconfig_release": {
        "description": "Release IP address",
        "execute": lambda a: _runl(["ipconfig", "/release"]),
    },
    "os_ipconfig_renew": {
        "description": "Renew IP address",
        "execute": lambda a: _runl(["ipconfig", "/renew"]),
    },
    "os_download_file": {
        "description": "Download a file from URL, args = [url, output_path]",
        "execute": lambda a: _run(f'powershell Invoke-WebRequest -Uri "{a[0]}" -OutFile "{a[1]}"'),
    },
}
