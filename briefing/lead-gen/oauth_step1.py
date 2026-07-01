#!/usr/bin/env python3
"""Step 1: Generar URL de autorizacion"""
import os, json, urllib.parse
with open(os.path.expanduser("~/.hermes/google_client_secret.json")) as f:
    client_config = json.load(f)["installed"]
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
params = {
    "client_id": client_config["client_id"],
    "redirect_uri": "http://localhost",
    "response_type": "code",
    "scope": " ".join(SCOPES),
    "access_type": "offline",
    "include_granted_scopes": "true",
    "prompt": "consent",
}
url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
# Store params for step 2
import pickle
with open("/tmp/oauth_params.pkl", "wb") as f:
    pickle.dump({"client_config": client_config, "scopes": SCOPES}, f)
print(url)
