"""
Web Addons — browser control & quick web shortcuts for Venty.
"""
import urllib.parse

from core.plugin_sdk import Plugin, ok, fail
from actions.browser import open_url
from actions.web import _web_search, _web_fetch

plugin = Plugin(
    id="webaddons",
    name="Web Addons",
    version="1.2.0",
    description="Open sites in Chrome/Edge/Firefox, search the web, fetch pages",
    author="Venty",
)


def _url_from_args(args: list, index: int = 0) -> str:
    if not args:
        raise ValueError("URL required")
    return args[index].strip()


@plugin.action("web_open_url", "Open URL in default browser, args = [url]")
def web_open_url(args):
    return open_url(_url_from_args(args), "default")


@plugin.action("web_open_chrome", "Open URL in Google Chrome, args = [url]")
def web_open_chrome(args):
    return open_url(_url_from_args(args), "chrome")


@plugin.action("web_open_edge", "Open URL in Microsoft Edge, args = [url]")
def web_open_edge(args):
    return open_url(_url_from_args(args), "edge")


@plugin.action("web_open_firefox", "Open URL in Firefox, args = [url]")
def web_open_firefox(args):
    return open_url(_url_from_args(args), "firefox")


@plugin.action("web_open", "Open URL in chosen browser, args = [url, chrome|edge|firefox|default]")
def web_open(args):
    url = _url_from_args(args)
    browser = args[1] if len(args) > 1 else "default"
    return open_url(url, browser)


@plugin.action("web_search_google", "Google search in browser, args = [query]")
def web_search_google(args):
    q = urllib.parse.quote(_url_from_args(args))
    return open_url(f"https://www.google.com/search?q={q}", "default")


@plugin.action("web_search", "Same as web_search_google — search the web, args = [query]")
def web_search(args):
    return web_search_google(args)


@plugin.action("web_youtube", "Open YouTube search in browser, args = [query]")
def web_youtube(args):
    q = urllib.parse.quote(_url_from_args(args))
    return open_url(f"https://www.youtube.com/results?search_query={q}", "default")


@plugin.action("web_github", "Open GitHub user or repo in browser, args = [user or user/repo]")
def web_github(args):
    path = _url_from_args(args).strip("/").replace("https://github.com/", "")
    return open_url(f"https://github.com/{path}", "default")


@plugin.action("web_reddit", "Open Reddit search in browser, args = [query]")
def web_reddit(args):
    q = urllib.parse.quote(_url_from_args(args))
    return open_url(f"https://www.reddit.com/search/?q={q}", "default")


@plugin.action("web_maps", "Open Google Maps search, args = [place or address]")
def web_maps(args):
    q = urllib.parse.quote(_url_from_args(args))
    return open_url(f"https://www.google.com/maps/search/{q}", "default")


@plugin.action("web_wikipedia", "Open Wikipedia article search, args = [topic]")
def web_wikipedia(args):
    q = _url_from_args(args).replace(" ", "_")
    return open_url(f"https://en.wikipedia.org/wiki/{urllib.parse.quote(q)}", "default")


@plugin.action("web_fetch_text", "Fetch page text (no browser), args = [url]")
def web_fetch_text(args):
    text = _web_fetch(_url_from_args(args))
    return ok(text)


@plugin.action("web_instant_answer", "DuckDuckGo instant answer (no browser), args = [query]")
def web_instant_answer(args):
    text = _web_search(_url_from_args(args))
    return ok(text)


# Popular shortcuts
_SITES = {
    "google": "https://google.com",
    "youtube": "https://youtube.com",
    "github": "https://github.com",
    "reddit": "https://reddit.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "discord": "https://discord.com/app",
    "chatgpt": "https://chat.openai.com",
    "stackoverflow": "https://stackoverflow.com",
}


@plugin.action("web_go", "Open known site by name, args = [google|youtube|github|reddit|...]")
def web_go(args):
    name = _url_from_args(args).lower().strip()
    if name.startswith("http"):
        return open_url(name, "default")
    url = _SITES.get(name)
    if not url:
        return fail(f"unknown site '{name}'. Known: {', '.join(sorted(_SITES))}")
    return open_url(url, "default")


ACTIONS = plugin.actions
PLUGIN_META = plugin.meta
