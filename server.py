import os
import http.server
import socketserver

PORT = int(os.environ.get("PORT", 8080))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

def run():
    handler = DashboardHandler
    with socketserver.ThreadingTCPServer(("", PORT), handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"Server started on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
