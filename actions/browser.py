"""
actions/browser.py — open URLs in default or named browsers (Windows).
"""
import os
import subprocess
import webbrowser


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


def _normalize_url(url: str) -> str:
    url = (url or "").strip().strip('"').strip("'")
    if not url:
        raise ValueError("URL is empty")
    if not url.startswith(("http://", "https://", "file:", "about:")):
        url = "https://" + url
    return url


def _chrome_paths():
    local = os.environ.get("LOCALAPPDATA", "")
    return [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
    ]


def _edge_paths():
    return [
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    ]


def _firefox_paths():
    return [
        os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
    ]


def _launch_exe(paths: list, url: str) -> bool:
    for exe in paths:
        if exe and os.path.isfile(exe):
            subprocess.Popen([exe, url], close_fds=True)
            return True
    return False


def open_url(url: str, browser: str = "default"):
    """Open URL in default or named browser: default, chrome, edge, firefox."""
    url = _normalize_url(url)
    name = (browser or "default").lower().strip()

    if name in ("default", "browser", ""):
        if os.name == "nt":
            os.startfile(url)  # noqa: S606 — Windows default handler
        else:
            webbrowser.open(url)
        return _stdout(f"Opened in default browser: {url}")

    if name == "chrome":
        if _launch_exe(_chrome_paths(), url):
            return _stdout(f"Opened in Chrome: {url}")
        subprocess.Popen(f'cmd /c start chrome "{url}"', shell=True)
        return _stdout(f"Opened in Chrome: {url}")

    if name in ("edge", "msedge"):
        if _launch_exe(_edge_paths(), url):
            return _stdout(f"Opened in Edge: {url}")
        subprocess.Popen(f'cmd /c start msedge "{url}"', shell=True)
        return _stdout(f"Opened in Edge: {url}")

    if name == "firefox":
        if _launch_exe(_firefox_paths(), url):
            return _stdout(f"Opened in Firefox: {url}")
        subprocess.Popen(f'cmd /c start firefox "{url}"', shell=True)
        return _stdout(f"Opened in Firefox: {url}")

    # webbrowser registry name
    try:
        webbrowser.get(name).open(url)
        return _stdout(f"Opened in {name}: {url}")
    except webbrowser.Error:
        if os.name == "nt":
            os.startfile(url)
            return _stdout(f"Browser '{name}' not found — opened with default: {url}")
        raise


ACTIONS = {
    "os_open_url": {
        "description": "Open URL in default browser, args = [url]",
        "execute": lambda a: open_url(a[0]),
    },
    "os_open_browser": {
        "description": "Open URL in a specific browser, args = [url, chrome|edge|firefox|default]",
        "execute": lambda a: open_url(a[0], a[1] if len(a) > 1 else "default"),
    },
    "os_open_chrome": {
        "description": "Open URL in Google Chrome, args = [url]",
        "execute": lambda a: open_url(a[0], "chrome"),
    },
    "os_open_edge": {
        "description": "Open URL in Microsoft Edge, args = [url]",
        "execute": lambda a: open_url(a[0], "edge"),
    },
    "os_open_firefox": {
        "description": "Open URL in Firefox, args = [url]",
        "execute": lambda a: open_url(a[0], "firefox"),
    },
}
