"""
actions/git.py — git operations
"""
import subprocess


def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


ACTIONS = {
    "os_git_clone": {
        "description": "Clone a git repo, args = [url, destination_folder]",
        "execute": lambda a: _run(f'git clone {a[0]} "{a[1] if len(a) > 1 else ""}"'),
    },
    "os_git_pull": {
        "description": "Git pull, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git pull'),
    },
    "os_git_push": {
        "description": "Git push, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git push'),
    },
    "os_git_status": {
        "description": "Git status, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git status'),
    },
    "os_git_commit": {
        "description": "Git add all and commit, args = [folder_path, message]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git add . && git commit -m "{a[1]}"'),
    },
    "os_git_log": {
        "description": "Git log, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git log --oneline -20'),
    },
    "os_git_branch": {
        "description": "List git branches, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git branch -a'),
    },
    "os_git_checkout": {
        "description": "Git checkout branch, args = [folder_path, branch]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git checkout {a[1]}'),
    },
    "os_git_diff": {
        "description": "Git diff, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git diff'),
    },
    "os_git_stash": {
        "description": "Git stash, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git stash'),
    },
    "os_git_reset": {
        "description": "Git reset hard to HEAD, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git reset --hard HEAD'),
    },
    "os_git_init": {
        "description": "Git init in a folder, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && git init'),
    },
}
