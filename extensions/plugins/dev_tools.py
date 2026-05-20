import subprocess
import os

PLUGIN_NAME    = "Dev Tools"
PLUGIN_VERSION = "1.0.0"

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def _ok(text):
    return type("R", (), {"stdout": str(text)})()

def _project_size(path="."):
    total = 0
    count = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules", "env", ".venv")]
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
                count += 1
            except Exception:
                pass
    return _ok(f"{count} files  •  {total / 1024:.1f} KB  •  {total / (1024*1024):.2f} MB")

ACTIONS = {
    "dev_run_tests": {
        "description": "Run pytest in a folder, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && python -m pytest -v'),
    },
    "dev_check_types": {
        "description": "Run mypy type check, args = [file_or_folder]",
        "execute": lambda a: _run(f"mypy {a[0]}"),
    },
    "dev_project_size": {
        "description": "Get project file count and size, args = [path] or []",
        "execute": lambda a: _project_size(a[0] if a else "."),
    },
    "dev_lint": {
        "description": "Run flake8 linter, args = [file_or_folder]",
        "execute": lambda a: _run(f"flake8 {a[0] if a else '.'}"),
    },
    "dev_format": {
        "description": "Format Python code with black, args = [file_or_folder]",
        "execute": lambda a: _run(f"black {a[0] if a else '.'}"),
    },
    "dev_requirements": {
        "description": "Generate requirements.txt from current env, args = [output_path]",
        "execute": lambda a: _run(f'pip freeze > "{a[0] if a else "requirements.txt"}"'),
    },
    "dev_venv_create": {
        "description": "Create a virtual environment, args = [path]",
        "execute": lambda a: _run(f'python -m venv "{a[0] if a else "env"}"'),
    },
    "dev_venv_activate": {
        "description": "Show venv activate command, args = [path]",
        "execute": lambda a: _ok(f'Run: {a[0] if a else "env"}\\Scripts\\activate'),
    },
    "dev_git_summary": {
        "description": "Show git log + status summary, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git log --oneline -5 && git status --short'),
    },
    "dev_count_lines": {
        "description": "Count lines of code in a folder, args = [folder] [extension]",
        "execute": lambda a: _ok(str(sum(
            sum(1 for _ in open(os.path.join(r, f), encoding="utf-8", errors="ignore"))
            for r, _, files in os.walk(a[0] if a else ".")
            for f in files if f.endswith(a[1] if len(a) > 1 else ".py")
        )) + " lines"),
    },
}
