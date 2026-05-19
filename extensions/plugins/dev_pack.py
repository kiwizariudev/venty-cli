"""
Dev Pack — quick developer utilities.
"""
import os
import subprocess

from core.plugin_sdk import Plugin, ok, fail
from core.paths import SANDBOX_DIR, BASE_DIR

plugin = Plugin(
    id="dev_pack",
    name="Dev Pack",
    version="1.0.0",
    description="Project info, git quick status, file stats",
    author="Venty",
)


def _cwd(args: list) -> str:
    if args and args[0]:
        p = args[0]
        return p if os.path.isabs(p) else os.path.join(BASE_DIR, p)
    return SANDBOX_DIR


@plugin.action("dev_tree", "Show folder tree (depth 2), args = [path] or []")
def dev_tree(args):
    path = _cwd(args)
    r = subprocess.run(
        f'tree "{path}" /A /F',
        shell=True, capture_output=True, text=True, timeout=30,
    )
    out = (r.stdout or r.stderr or "")[:3000]
    return ok(out or "tree failed")


@plugin.action("dev_git_status", "Git status in folder, args = [path] or []")
def dev_git_status(args):
    path = _cwd(args)
    r = subprocess.run(
        f'git -C "{path}" status -sb',
        shell=True, capture_output=True, text=True, timeout=15,
    )
    if r.returncode != 0:
        return fail(r.stderr.strip() or "not a git repo")
    return ok(r.stdout.strip())


@plugin.action("dev_count_py", "Count .py files and lines, args = [path] or []")
def dev_count_py(args):
    path = _cwd(args)
    files = 0
    lines = 0
    for root, _, names in os.walk(path):
        if "env" in root.split(os.sep) or "__pycache__" in root:
            continue
        for n in names:
            if n.endswith(".py"):
                files += 1
                try:
                    with open(os.path.join(root, n), encoding="utf-8", errors="ignore") as f:
                        lines += sum(1 for _ in f)
                except OSError:
                    pass
    return ok(f"{files} Python files, ~{lines} lines under {path}")


@plugin.action("dev_pip_list", "List pip packages (top 30), args = []")
def dev_pip_list(args):
    r = subprocess.run(
        [os.environ.get("PYTHON", "python"), "-m", "pip", "list"],
        capture_output=True, text=True, timeout=60,
    )
    lines = (r.stdout or "").strip().splitlines()[:32]
    return ok("\n".join(lines))


ACTIONS = plugin.actions
PLUGIN_META = plugin.meta
