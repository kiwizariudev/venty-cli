"""
extensions/plugins/dev_tools.py — Developer helper actions
"""
import os
import sys
import subprocess

def dev_run_tests(args):
    """Run pytest in the project root. args = []"""
    try:
        res = subprocess.run([sys.executable, "-m", "pytest", "tests/"], capture_output=True, text=True)
        return type('R', (), {'stdout': res.stdout + "\n" + res.stderr})()
    except Exception as e:
        return type('R', (), {'stdout': f"Failed to run tests: {e}"})()

def dev_check_types(args):
    """Run mypy if installed. args = []"""
    try:
        res = subprocess.run([sys.executable, "-m", "mypy", "."], capture_output=True, text=True)
        return type('R', (), {'stdout': res.stdout + "\n" + res.stderr})()
    except Exception as e:
        return type('R', (), {'stdout': f"Mypy not found or failed: {e}"})()

def dev_project_size(args):
    """Calculate total lines of code in the project."""
    total_lines = 0
    for root, dirs, files in os.walk("."):
        if "env" in dirs: dirs.remove("env")
        if ".git" in dirs: dirs.remove(".git")
        for f in files:
            if f.endswith(".py"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as f_obj:
                    total_lines += len(f_obj.readlines())
    return type('R', (), {'stdout': f"Total Python LOC: {total_lines}"})()

ACTIONS = {
    "dev_run_tests": {
        "description": "Run the project test suite using pytest",
        "execute": dev_run_tests
    },
    "dev_check_types": {
        "description": "Run static type checking using mypy",
        "execute": dev_check_types
    },
    "dev_project_size": {
        "description": "Count total lines of Python code in the project",
        "execute": dev_project_size
    }
}
