#!/usr/bin/env python3
"""Gmail OAuth generando URL manual + intercambio de codigo"""
import os, json, urllib.parse, sys
from google_auth_oauthlib.flow import InstalledAppFlow
from urllib.parse import urlparse, parse_qs

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

token_path = os.path.expanduser("~/.hermes/google_token.json")
secret_path = os.path.expanduser("~/.hermes/google_client_secret.json")

# Cargar client secret
with open(secret_path) as f:
    client_config = json.load(f)["installed"]

CLIENT_ID = client_config["client_id"]
REDIRECT_URI = "http://localhost"

# Construir URL manualmente (evita PKCE que omite redirect_uri)
params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": " ".join(SCOPES),
    "access_type": "offline",
    "include_granted_scopes": "true",
    "prompt": "consent",
}
auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)

print("=== MANUAL OAUTH FLOW ===")
print()
print("1. ABRE este enlace en tu navegador (pulsalo):")
print(auth_url)
print()
print("2. SI TE APARECE 'Acceso bloqueado':")
print("   - Pulsa el boton 'Advanced' o 'Mas informacion'")
print("   - Luego pulsa 'Go to ... (unsafe)' o 'Acceder a ... (poco seguro)'")
print("   - Autoriza la aplicacion con tu cuenta formulasia76@gmail.com")
print()
print("3. Google te redirigira a http://localhost/?code=...")
print("   (dara error de pagina no encontrada, NORMAL)")
print("   COPIA LA URL COMPLETA de la barra de direcciones")
print("   (empieza por http://localhost/?code=4/...)")
print()
print("4. PEGA AQUI la URL completa y pulsa Enter:")
redirect_url = sys.stdin.readline().strip()

# Extraer el code
qs = parse_qs(urlparse(redirect_url).query)
code = qs['code'][0]

# Intercambiar por token
flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
flow.fetch_token(code=code)
creds = flow.credentials

with open(token_path, 'w') as f:
    f.write(creds.to_json())

print()
print("=== TOKEN GUARDADO CORRECTAMENTE ===")
print("Scopes:", creds.scopes)
print("Expira:", creds.expiry)
print("Refresh token:", "SI" if creds.refresh_token else "NO")
