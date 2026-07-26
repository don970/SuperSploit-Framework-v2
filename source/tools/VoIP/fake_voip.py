import http.server
import socketserver
import json
import time

# Configuration
PORT = 8001
VALID_USER = "admin"
VALID_PASS = "secret"

class FakeVoipHandler(http.server.BaseHTTPRequestHandler):
    def _send_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        print(f"\n[+] Incoming Request from {self.client_address}")
        
        try:
            # Handle both form-urlencoded (Twilio style) and JSON
            if self.headers['Content-Type'] == 'application/json':
                data = json.loads(post_data)
            else:
                # Basic mock parsing for form data
                import urllib.parse
                data = urllib.parse.parse_qs(post_data)
                # Convert list values to single values
                data = {k: v[0] for k, v in data.items()}

            # Mock Authentication Check
            auth = self.headers.get('Authorization')
            if auth:
                print(f"[*] Auth Provided: {auth}")

            print("================== SPOOFED SMS RECEIVED ==================")
            print(f"SENDER ID (From) : {data.get('From', 'UNKNOWN')}")
            print(f"RECIPIENT (To)   : {data.get('To', 'UNKNOWN')}")
            print(f"MESSAGE BODY     : {data.get('Body', 'EMPTY')}")
            print("==========================================================")

            # Mock successful delivery
            response = {
                "sid": f"SM{int(time.time())}",
                "status": "queued",
                "date_created": time.ctime(),
                "direction": "outbound-api"
            }
            self._send_response(201, response)

        except Exception as e:
            print(f"[-] Error: {e}")
            self._send_response(400, {"error": str(e)})

    def log_message(self, format, *args):
        # Silence standard HTTP logs for cleaner output
        return

def start_server():
    with socketserver.TCPServer(("", PORT), FakeVoipHandler) as httpd:
        print(f"[*] Fake VoIP SMS Gateway listening on 0.0.0.0:{PORT}")
        print(f"[*] Mock Endpoint: http://127.0.0.1:{PORT}/2010-04-01/Accounts/AC.../Messages")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Shutting down server...")

if __name__ == "__main__":
    start_server()
