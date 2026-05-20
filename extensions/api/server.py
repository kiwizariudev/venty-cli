"""
extensions/api/server.py — Multi-language Bridge API
Allows other languages (Java, JS, Rust, etc.) to interact with Venty.
"""
import json
import http.server
import socketserver
import threading
from core.agent import ask, parse_response
from core.executor import execute_action
from core.logger import get_logger

logger = get_logger()

class VentyAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Endpoint: /command
        if self.path == "/command":
            user_input = data.get("command", "")
            # This is a simplified version for the bridge
            # In a real scenario, it would hook into the main loop's agent
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "received", "message": f"Venty bridge received: {user_input}"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_api(port=8888):
    def serve():
        with socketserver.TCPServer(("", port), VentyAPIHandler) as httpd:
            logger.info(f"Venty Multi-lang Bridge started on port {port}")
            httpd.serve_forever()
            
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return port
