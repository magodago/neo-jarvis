#!/usr/bin/env python3
"""NEO MailerLite Bridge."""
import json, urllib.request, sys, os, base64
from pathlib import Path

def get_key():
    """Read MailerLite API key from env or .env (base64 encoded)."""
    raw = os.environ.get("ML_KEY_B64", "")
    if raw:
        return base64.b64decode(raw.strip().strip("'\"")).decode()
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ML_KEY_B64="):
                b64 = line.split("=", 1)[1].strip().strip("'\"")
                return base64.b64decode(b64).decode()
    return ""

KEY = get_key()
URL = "https://connect.mailerlite.com/api/subscribers"

def add(email, name=""):
    if not KEY: return print("❌ No KEY")
    d = {"email": email}
    if name: d["fields"] = {"name": name}
    req = urllib.request.Request(URL, json.dumps(d).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req)
        print(f"✅ {email}")
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        if "already" in b.lower(): print(f"ℹ️  {email} ya existe")
        else: print(f"❌ {e.code}: {b[:80]}")

def ls(limit=5):
    if not KEY: return print("❌ No KEY")
    req = urllib.request.Request(f"{URL}?limit={limit}",
        headers={"Authorization": f"Bearer {KEY}"})
    try:
        for s in json.loads(urllib.request.urlopen(req).read()).get("data", []):
            print(f"  {s['email']} — {s['status']}")
    except Exception as e: print(f"❌ {e}")

if __name__ == "__main__":
    if "list" in sys.argv[1:2]: ls()
    elif sys.argv[1:2] == ["add"] and len(sys.argv)>2: add(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "")
    else: ls()
