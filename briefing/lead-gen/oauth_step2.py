#!/usr/bin/env python3
"""Step 2: Canjear codigo OAuth por token"""
import os, json, sys, pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from urllib.parse import urlparse, parse_qs

redirect_url = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.readline().strip()

with open("/tmp/oauth_params.pkl", "rb") as f:
    params = pickle.load(f)

secret_path = os.path.expanduser("~/.hermes/google_client_secret.json")
token_path = os.path.expanduser("~/.hermes/google_token.json")

qs = parse_qs(urlparse(redirect_url).query)
code = qs.get('code', [None])[0]

if not code:
    print("ERROR: No se encontro 'code' en la URL")
    print("URL recibida:", redirect_url[:200])
    sys.exit(1)

flow = InstalledAppFlow.from_client_secrets_file(secret_path, params["scopes"])
flow.fetch_token(code=code)
creds = flow.credentials

with open(token_path, 'w') as f:
    f.write(creds.to_json())

print("=== TOKEN GUARDADO ===")
print("Scopes:", creds.scopes)
print("Expira:", creds.expiry)
print("Refresh:", "SI" if creds.refresh_token else "NO")
