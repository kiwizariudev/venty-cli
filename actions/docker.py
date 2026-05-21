import subprocess

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

ACTIONS = {
    "docker_ps":              {"description": "List running containers",                                          "execute": lambda a: _run("docker ps")},
    "docker_ps_all":          {"description": "List all containers including stopped",                            "execute": lambda a: _run("docker ps -a")},
    "docker_images":          {"description": "List docker images",                                               "execute": lambda a: _run("docker images")},
    "docker_pull":            {"description": "Pull a docker image, args = [image]",                             "execute": lambda a: _run(f"docker pull {a[0]}")},
    "docker_run":             {"description": "Run a container, args = [image] or [image, flags]",               "execute": lambda a: _run(f"docker run {a[1] if len(a)>1 else '-d'} {a[0]}")},
    "docker_run_port":        {"description": "Run container with port mapping, args = [image, host_port, container_port]", "execute": lambda a: _run(f"docker run -d -p {a[1]}:{a[2]} {a[0]}")},
    "docker_stop":            {"description": "Stop a container, args = [container_id_or_name]",                 "execute": lambda a: _run(f"docker stop {a[0]}")},
    "docker_start":           {"description": "Start a stopped container, args = [container_id_or_name]",        "execute": lambda a: _run(f"docker start {a[0]}")},
    "docker_restart":         {"description": "Restart a container, args = [container_id_or_name]",              "execute": lambda a: _run(f"docker restart {a[0]}")},
    "docker_rm":              {"description": "Remove a container, args = [container_id_or_name]",               "execute": lambda a: _run(f"docker rm {a[0]}")},
    "docker_rmi":             {"description": "Remove an image, args = [image]",                                 "execute": lambda a: _run(f"docker rmi {a[0]}")},
    "docker_logs":            {"description": "Get container logs, args = [container_id_or_name]",               "execute": lambda a: _run(f"docker logs {a[0]}")},
    "docker_logs_tail":       {"description": "Get last N lines of container logs, args = [container, lines]",   "execute": lambda a: _run(f"docker logs --tail {a[1] if len(a)>1 else '50'} {a[0]}")},
    "docker_exec":            {"description": "Run command in container, args = [container, command]",           "execute": lambda a: _run(f"docker exec {a[0]} {a[1]}")},
    "docker_build":           {"description": "Build image from Dockerfile, args = [path, tag]",                 "execute": lambda a: _run(f'docker build -t {a[1] if len(a)>1 else "myapp"} "{a[0]}"')},
    "docker_build_no_cache":  {"description": "Build image without cache, args = [path, tag]",                   "execute": lambda a: _run(f'docker build --no-cache -t {a[1] if len(a)>1 else "myapp"} "{a[0]}"')},
    "docker_inspect":         {"description": "Inspect a container or image, args = [name]",                     "execute": lambda a: _run(f"docker inspect {a[0]}")},
    "docker_stats":           {"description": "Show container resource usage (snapshot)",                         "execute": lambda a: _run("docker stats --no-stream")},
    "docker_prune":           {"description": "Remove all stopped containers",                                    "execute": lambda a: _run("docker container prune -f")},
    "docker_prune_images":    {"description": "Remove unused images",                                             "execute": lambda a: _run("docker image prune -f")},
    "docker_prune_all":       {"description": "Remove all unused docker resources",                               "execute": lambda a: _run("docker system prune -f")},
    "docker_network_ls":      {"description": "List docker networks",                                             "execute": lambda a: _run("docker network ls")},
    "docker_volume_ls":       {"description": "List docker volumes",                                              "execute": lambda a: _run("docker volume ls")},
    "docker_compose_up":      {"description": "docker-compose up, args = [folder_path]",                         "execute": lambda a: _run(f'cd /d "{a[0]}" && docker-compose up -d')},
    "docker_compose_down":    {"description": "docker-compose down, args = [folder_path]",                       "execute": lambda a: _run(f'cd /d "{a[0]}" && docker-compose down')},
    "docker_compose_logs":    {"description": "docker-compose logs, args = [folder_path]",                       "execute": lambda a: _run(f'cd /d "{a[0]}" && docker-compose logs --tail=50')},
    "docker_compose_build":   {"description": "docker-compose build, args = [folder_path]",                      "execute": lambda a: _run(f'cd /d "{a[0]}" && docker-compose build')},
    "docker_compose_restart": {"description": "docker-compose restart, args = [folder_path]",                    "execute": lambda a: _run(f'cd /d "{a[0]}" && docker-compose restart')},
    "docker_version":         {"description": "Get docker version",                                               "execute": lambda a: _run("docker --version")},
    "docker_info":            {"description": "Get docker system info",                                           "execute": lambda a: _run("docker info")},
}
