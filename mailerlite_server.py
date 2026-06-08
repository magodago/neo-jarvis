#!/usr/bin/env python3
"""NEO MailerLite HTTP Bridge — tiny server for newsletter form submissions."""
import json, urllib.request, http.server, os, base64, sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def get_key():
    raw = os.environ.get("ML_KEY_B64", "")
    if raw:
        return base64.b64decode(raw.strip().strip("'\"")).decode()
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ML_KEY_B64="):
                return base64.b64decode(line.split("=",1)[1].strip().strip("'\"")).decode()
    return ""

KEY = get_key()
ML_URL = "https://connect.mailerlite.com/api/subscribers"

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/subscribe":
            self.send_response(404)
            self.end_headers()
            return
        
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        
        try:
            # Support both JSON and form-urlencoded
            ct = self.headers.get("Content-Type", "")
            if "json" in ct:
                data = json.loads(body)
            else:
                params = parse_qs(body.decode())
                data = {k: v[0] for k, v in params.items()}
            
            email = data.get("email", "")
            name = data.get("name", "")
            
            if not email or "@" not in email:
                self._respond(400, {"error": "email required"})
                return
            
            # Forward to MailerLite
            ml_data = {"email": email}
            if name: ml_data["fields"] = {"name": name}
            
            req = urllib.request.Request(ML_URL, json.dumps(ml_data).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
            
            try:
                urllib.request.urlopen(req)
                self._respond(200, {"status": "ok", "email": email})
                print(f"✅ Subscriptor: {email}")
            except urllib.error.HTTPError as e:
                err = e.read().decode()
                if "already" in err.lower():
                    self._respond(200, {"status": "exists", "email": email})
                    print(f"ℹ️  Ya existe: {email}")
                else:
                    self._respond(500, {"error": str(e.code)})
                    print(f"❌ Error {e.code}: {err[:100]}")
                    
        except Exception as e:
            self._respond(500, {"error": str(e)})
    
    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[MailerLiteBridge] {args[0]} {args[1]}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8645
    if not KEY:
        print("❌ No MailerLite API key configured")
        print("   Set ML_KEY_B64 in ~/.hermes/.env")
        sys.exit(1)
    
    server = http.server.HTTPServer(("0.0.0.0", port), Handler)
    print(f"🚀 MailerLite Bridge running on port {port}")
    print(f"   POST /subscribe with JSON: email, name (opcional)")
    server.serve_forever()
