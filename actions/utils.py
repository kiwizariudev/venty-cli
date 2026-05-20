import os
import json
import zipfile
import http.server
import socketserver
import threading
import socket
import time

def _stdout(text):
    return type("R", (), {"stdout": str(text)})()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_server(args):
    path = args[0]
    port = int(args[1]) if len(args) > 1 else 8000
    os.chdir(path)
    handler = http.server.SimpleHTTPRequestHandler
    def serve():
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return _stdout(f"Server started at http://{get_ip()}:{port} serving {path}")

def format_json(args):
    path = args[0]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return _stdout(f"Formatted {path}")

def zip_folder(args):
    path = args[0]
    output = args[1]
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    return _stdout(f"Zipped {path} to {output}")

def unzip_file(args):
    path = args[0]
    dest = args[1]
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(dest)
    return _stdout(f"Unzipped {path} to {dest}")

ACTIONS = {
    "tool_http_server": {
        "description": "Start a mini HTTP server, args = [folder, port]",
        "execute": start_server,
    },
    "tool_format_json": {
        "description": "Format a JSON file, args = [filepath]",
        "execute": format_json,
    },
    "tool_zip": {
        "description": "Zip a folder, args = [folder_path, output_zip]",
        "execute": zip_folder,
    },
    "tool_unzip": {
        "description": "Unzip a file, args = [zip_path, extract_to]",
        "execute": unzip_file,
    },
}
