#!/usr/bin/env python3
"""Envía test a formulasia con el email v3 (con packs)"""
import os, sys, base64, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enviar_v3 import TOKEN_FILE, SCOPES, LANDING, EMAIL_TEXTO, HTML_TEMPLATE

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if not creds.valid and creds.expired and creds.refresh_token:
    creds.refresh(Request())
service = build("gmail", "v1", credentials=creds)

# Email con packs para un restaurante en Madrid (ejemplo)
ciudad = "Madrid"
sector = "restaurante"
nombre = "Restaurante Ejemplo"

body = EMAIL_TEXTO.replace("[CIUDAD]", ciudad).replace("[SECTOR]", sector)
body_html = body.replace("\n", "<br>")
html = HTML_TEMPLATE.replace("[CUERPO_HTML]", body_html).replace("[LANDING]", LANDING)
subj = f"{nombre}, una idea para tu {sector} en {ciudad}"

print("=" * 55)
print("EMAIL CON PACKS - VERSIÓN DEFINITIVA")
print("=" * 55)
print(f"ASUNTO: {subj}")
print(f"CUERPO:")
print(body)
print()

msg = MIMEMultipart("alternative")
msg["Subject"] = subj
msg["From"] = "dortizs76@gmail.com"
msg["To"] = "formulasia76@gmail.com"
msg["Reply-To"] = "dortizs76@gmail.com"
msg.attach(MIMEText(body, "plain", "utf-8"))
msg.attach(MIMEText(html, "html", "utf-8"))

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
print(f"✅ ENVIADO a formulasia76@gmail.com")
print(f"📬 Revisa tu bandeja de entrada")
