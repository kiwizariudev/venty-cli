"""
actions/compile.py — compile and run code (gcc, g++, python, node, java, etc.)
"""
import subprocess


def _run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)


def _popen(cmd):
    return subprocess.Popen(cmd, shell=True)


ACTIONS = {
    "os_run_command": {
        "description": "Run any shell command, args = [command string]",
        "execute": lambda a: _run(a[0]),
    },
    "os_compile_gcc": {
        "description": "Compile C with gcc, args = [source.c, output]",
        "execute": lambda a: _run(f'gcc "{a[0]}" -o "{a[1]}"'),
    },
    "os_compile_gcc_flags": {
        "description": "Compile C with flags, args = [source.c, output, flags]",
        "execute": lambda a: _run(f'gcc {a[2]} "{a[0]}" -o "{a[1]}"'),
    },
    "os_compile_gpp": {
        "description": "Compile C++ with g++, args = [source.cpp, output]",
        "execute": lambda a: _run(f'g++ "{a[0]}" -o "{a[1]}"'),
    },
    "os_compile_gpp_flags": {
        "description": "Compile C++ with flags, args = [source.cpp, output, flags]",
        "execute": lambda a: _run(f'g++ {a[2]} "{a[0]}" -o "{a[1]}"'),
    },
    "os_compile_cs": {
        "description": "Compile C# with csc, args = [source.cs, output.exe]",
        "execute": lambda a: _run(f'csc /out:"{a[1]}" "{a[0]}"'),
    },
    "os_compile_java": {
        "description": "Compile Java file, args = [source.java]",
        "execute": lambda a: _run(f'javac "{a[0]}"'),
    },
    "os_run_java": {
        "description": "Run Java class, args = [classname]",
        "execute": lambda a: _run(f"java {a[0]}"),
    },
    "os_run_exe": {
        "description": "Run an exe file (no wait), args = [path.exe]",
        "execute": lambda a: _popen(f'"{a[0]}"'),
    },
    "os_run_exe_wait": {
        "description": "Run exe and wait for output, args = [path.exe]",
        "execute": lambda a: _run(f'"{a[0]}"'),
    },
    "os_run_python": {
        "description": "Run a python script, args = [script.py]",
        "execute": lambda a: _run(f'python "{a[0]}"'),
    },
    "os_run_python_args": {
        "description": "Run python script with args, args = [script.py, arg1, arg2...]",
        "execute": lambda a: _run("python " + " ".join(f'"{x}"' for x in a)),
    },
    "os_run_python3": {
        "description": "Run with python3, args = [script.py]",
        "execute": lambda a: _run(f'python3 "{a[0]}"'),
    },
    "os_run_node": {
        "description": "Run a node.js script, args = [script.js]",
        "execute": lambda a: _run(f'node "{a[0]}"'),
    },
    "os_run_batch": {
        "description": "Run a .bat file, args = [file.bat]",
        "execute": lambda a: _popen(f'"{a[0]}"'),
    },
    "os_run_powershell_script": {
        "description": "Run a .ps1 script, args = [script.ps1]",
        "execute": lambda a: _run(f'powershell -ExecutionPolicy Bypass -File "{a[0]}"'),
    },
    "os_run_powershell_cmd": {
        "description": "Run a PowerShell command, args = [command]",
        "execute": lambda a: _run(f'powershell -Command "{a[0]}"'),
    },
    "os_pip_install": {
        "description": "Install a python package, args = [package_name]",
        "execute": lambda a: _run(f"pip install {a[0]}"),
    },
    "os_pip_install_req": {
        "description": "Install from requirements.txt, args = [path]",
        "execute": lambda a: _run(f'pip install -r "{a[0]}"'),
    },
    "os_pip_uninstall": {
        "description": "Uninstall a python package, args = [package_name]",
        "execute": lambda a: _run(f"pip uninstall -y {a[0]}"),
    },
    "os_pip_upgrade": {
        "description": "Upgrade a python package, args = [package_name]",
        "execute": lambda a: _run(f"pip install --upgrade {a[0]}"),
    },
    "os_pip_list": {
        "description": "List installed python packages",
        "execute": lambda a: _run("pip list"),
    },
    "os_pip_freeze": {
        "description": "Export pip freeze to file, args = [output_file]",
        "execute": lambda a: _run(f'pip freeze > "{a[0]}"'),
    },
    "os_npm_install": {
        "description": "npm install in a folder, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && npm install'),
    },
    "os_npm_install_pkg": {
        "description": "npm install a package, args = [folder_path, package]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && npm install {a[1]}'),
    },
    "os_npm_run": {
        "description": "Run npm script, args = [folder_path, script_name]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && npm run {a[1]}'),
    },
    "os_npm_build": {
        "description": "npm build, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && npm run build'),
    },
    "os_npm_list": {
        "description": "List npm packages, args = [folder_path]",
        "execute": lambda a: _run(f'cd /d "{a[0]}" && npm list'),
    },
}
