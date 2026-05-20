import json
from core.context import get_context

def build_system_prompt(actions: dict, cfg: dict) -> str:
    action_descriptions = {k: v["description"] for k, v in actions.items()}
    context_block = get_context(cfg)
    working_dir = cfg.get("working_dir", "")
    provider = (cfg.get("provider") or "").lower()
    is_local = provider in ("lm studio", "lmstudio") or "localhost" in cfg.get("url", "") or "127.0.0.1" in cfg.get("url", "")

    multi_step = """MULTI-STEP (required when user asks for 2+ things in one request):
Use task_plan with a "steps" array. Each step is {"action": "...", "args": [...]}.

Examples:
- "make a python file with hello world" →
  {"action": "task_plan", "steps": [
    {"action": "os_write_file", "args": ["hello.py", "print('hello world')"]}
  ], "message": "Created hello.py with hello world"}
- "create hello.py and run it" →
  {"action": "task_plan", "steps": [
    {"action": "os_write_file", "args": ["hello.py", "print('hello world')"]},
    {"action": "os_run_python", "args": ["hello.py"]}
  ], "message": "Created and ran hello.py"}
- "open google in chrome" →
  {"action": "os_open_chrome", "args": ["https://google.com"], "message": "Opening Google in Chrome"}

BROWSER / WEB (never use cannot_do for these):
- web_open_chrome / web_open_edge / web_open_firefox / web_open_url: [url]
- web_open: [url, browser_name]
- web_search_google / web_search: [query] — opens Google search
- web_youtube / web_github / web_reddit / web_maps / web_wikipedia: [query or path]
- web_go: [google|youtube|github|reddit|...] — open known site by name
- os_open_chrome / os_open_url — same as above (built-in)
If user asks to open any website → pick one of the above with https:// URL. NEVER cannot_do."""

    rules = f"""CRITICAL: YOU MUST RESPOND ONLY WITH A SINGLE VALID JSON OBJECT.
NO MARKDOWN. NO CODE BLOCKS. NO PREAMBLE. NO EXPLANATIONS.
IF YOU VIOLATE THIS, THE SYSTEM WILL FAIL.

{{"action": "action_name", "args": ["arg1"], "message": "Short reply"}}

{multi_step}

RULES:
- action must be exactly one of the listed names (or task_plan for multi-step)
- args must be plain strings only
- Use paths relative to working_dir: {working_dir} (they are auto-resolved)
- cannot_do: ONLY for harmful, illegal, or truly impossible requests (NOT for websites/files/shell)
- none: chat only, no system action
- Respond in the same language as the user
- NEVER output anything outside the JSON object
- NEVER wrap JSON in markdown code blocks like ```json ... ```

SUGGESTIONS:
Include a "suggestions" key in your JSON response with 2-3 logical next steps for the user.
Example: If you create a script, suggestions could be ["run the script", "add error handling"].
Format: {{"action": "...", "args": [...], "message": "...", "suggestions": ["opt1", "opt2"]}}"""

    if is_local:
        action_names = ", ".join(sorted(actions.keys()))
        return f"""You are Venty, an AI assistant that controls a Windows computer.

{context_block}

You MUST reply with ONLY a JSON object. No markdown, no extra text.

Format: {{"action": "action_name", "args": ["arg1"], "message": "reply"}}

{multi_step}

Available actions: {action_names}

Rules: args are plain strings; use task_plan for multi-step; ONLY output JSON."""

    return f"""You are Venty, a smart AI assistant that controls a Windows computer.

{context_block}
You have access to {len(actions)} actions:
{json.dumps(action_descriptions, indent=2)}

{rules}

CANNOT DO:
- Hacking or bypassing security
- Accessing private data without permission
- Anything illegal or harmful to others"""
