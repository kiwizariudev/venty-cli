"""
actions/web.py — web search, fetch, and HTTP requests (new module)
Uses only stdlib + requests (already a dependency).
"""
import json
import urllib.parse

try:
    import requests as _req
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


def _stdout(text):
    return type("R", (), {"stdout": str(text)})()


def _web_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo instant answer API — no key required."""
    if not _HAS_REQUESTS:
        return "requests package not installed"
    try:
        encoded = urllib.parse.quote(query)
        r = _req.get(
            f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1",
            timeout=10,
            headers={"User-Agent": "Venty/1.0"},
        )
        data = r.json()
        lines = []
        if data.get("AbstractText"):
            lines.append(f"Summary: {data['AbstractText']}")
            if data.get("AbstractURL"):
                lines.append(f"Source : {data['AbstractURL']}")
        for item in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(item, dict) and item.get("Text"):
                lines.append(f"• {item['Text']}")
        return "\n".join(lines) if lines else "No results found"
    except Exception as e:
        return f"Search error: {e}"


def _web_fetch(url: str, max_chars: int = 2000) -> str:
    """Fetch a URL and return plain text content (stripped HTML)."""
    if not _HAS_REQUESTS:
        return "requests package not installed"
    try:
        r = _req.get(url, timeout=15, headers={"User-Agent": "Venty/1.0"})
        r.raise_for_status()
        # very basic HTML strip
        import re
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars] + ("..." if len(text) > max_chars else "")
    except Exception as e:
        return f"Fetch error: {e}"


def _web_post(url: str, body: str) -> str:
    """Send a POST request with a JSON body, args = [url, json_string]."""
    if not _HAS_REQUESTS:
        return "requests package not installed"
    try:
        payload = json.loads(body)
        r = _req.post(url, json=payload, timeout=15, headers={"User-Agent": "Venty/1.0"})
        return f"Status: {r.status_code}\n{r.text[:1000]}"
    except Exception as e:
        return f"POST error: {e}"


ACTIONS = {
    "web_search": {
        "description": "Search the web (DuckDuckGo), args = [query]",
        "execute": lambda a: _stdout(_web_search(a[0])),
    },
    "web_fetch": {
        "description": "Fetch and read a URL, args = [url]",
        "execute": lambda a: _stdout(_web_fetch(a[0])),
    },
    "web_post": {
        "description": "Send HTTP POST with JSON body, args = [url, json_string]",
        "execute": lambda a: _stdout(_web_post(a[0], a[1] if len(a) > 1 else "{}")),
    },
    "web_get_json": {
        "description": "GET a URL and return JSON, args = [url]",
        "execute": lambda a: _stdout(
            json.dumps(_req.get(a[0], timeout=10).json(), indent=2)[:2000]
            if _HAS_REQUESTS else "requests not installed"
        ),
    },
}
