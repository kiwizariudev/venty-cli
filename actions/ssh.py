import subprocess
import os

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def _ok(text):
    return type("R", (), {"stdout": str(text)})()

ACTIONS = {
    "ssh_run":          {"description": "Run command on remote host via SSH, args = [user@host, command]",           "execute": lambda a: _run(f'ssh {a[0]} "{a[1]}"')},
    "ssh_run_key":      {"description": "SSH with key file, args = [user@host, command, key_path]",                  "execute": lambda a: _run(f'ssh -i "{a[2]}" {a[0]} "{a[1]}"')},
    "ssh_copy_to":      {"description": "Copy file to remote host via SCP, args = [local_path, user@host:remote_path]", "execute": lambda a: _run(f'scp "{a[0]}" {a[1]}')},
    "ssh_copy_from":    {"description": "Copy file from remote host, args = [user@host:remote_path, local_path]",    "execute": lambda a: _run(f'scp {a[0]} "{a[1]}"')},
    "ssh_copy_dir":     {"description": "Copy directory to remote host, args = [local_dir, user@host:remote_path]",  "execute": lambda a: _run(f'scp -r "{a[0]}" {a[1]}')},
    "ssh_keygen":       {"description": "Generate SSH key pair, args = [output_path]",                               "execute": lambda a: _run(f'ssh-keygen -t ed25519 -f "{a[0]}" -N ""')},
    "ssh_add_key":      {"description": "Add SSH key to agent, args = [key_path]",                                   "execute": lambda a: _run(f'ssh-add "{a[0]}"')},
    "ssh_test":         {"description": "Test SSH connection, args = [user@host]",                                   "execute": lambda a: _run(f"ssh -o ConnectTimeout=5 -o BatchMode=yes {a[0]} echo ok")},
    "ssh_tunnel":       {"description": "Create SSH tunnel, args = [local_port, user@host, remote_port]",            "execute": lambda a: _run(f"ssh -N -L {a[0]}:localhost:{a[2]} {a[1]}")},
    "rsync_push":       {"description": "Sync local folder to remote, args = [local_path, user@host:remote_path]",   "execute": lambda a: _run(f'rsync -avz "{a[0]}" {a[1]}')},
    "rsync_pull":       {"description": "Sync remote folder to local, args = [user@host:remote_path, local_path]",   "execute": lambda a: _run(f'rsync -avz {a[0]} "{a[1]}"')},
}
