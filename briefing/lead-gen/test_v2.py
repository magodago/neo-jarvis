#!/usr/bin/env python3
import sys, re, os, base64
sys.path.insert(0, "/home/dorti/neo-jarvis/briefing/lead-gen")
from personalizer import generar_email
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

tok = os.path.expanduser("~/.hermes/google_token.json")
scopes = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify"]
creds = Credentials.from_authorized_user_file(tok, scopes)
service = build("gmail", "v1", credentials=creds)

s, b = generar_email({"nombre": "Restaurante Los Bravos",
                       "ciudad": "Barcelona", "sector": "restaurantes"})
s = re.sub(r"[*#_~`]", "", s).strip()
b = re.sub(r"[*#_~`]", "", b).strip()
if len(s) < 5 or len(s) > 100:
    s = "Restaurante Los Bravos, tu web profesional desde 299 EUR"

body = b.replace("\n\n", " ").replace("\n", " ")

html = (
    "<div style='background:#0a0a0a;padding:30px;font-family:sans-serif'>"
    "<div style='max-width:560px;margin:auto;background:#111;border-radius:12px;overflow:hidden'>"
    "<div style='background:linear-gradient(135deg,#0a0a0a,#1a0033);padding:25px;text-align:center'>"
    "<h1 style='margin:0;color:#ff00ff'>NEO <span style='color:#fff'>LABS</span></h1>"
    "<p style='margin:4px 0 0;color:#666;font-size:10px;letter-spacing:2px'>SOLUCIONES DIGITALES</p>"
    "</div>"
    "<div style='padding:25px;color:#ddd;font-size:14px;line-height:1.7'>"
    + body +
    "</div>"
    "<div style='padding:0 25px 15px'>"
    "<div style='background:#1a1a2e;border-radius:6px;padding:10px 14px;margin:3px 0;border-left:3px solid #ff00ff'>"
    "<b style='color:#ff00ff'>BASICA 299 EUR</b>"
    " <span style='color:#999;font-size:12px'>- Web responsive, SEO, formulario, hosting</span></div>"
    "<div style='background:#1a1a2e;border-radius:6px;padding:10px 14px;margin:3px 0;border-left:3px solid #00ffff'>"
    "<b style='color:#00ffff'>PREMIUM 599 EUR (MAS POPULAR)</b>"
    " <span style='color:#999;font-size:12px'>- Diseno premium, SEO, blog, panel admin</span></div>"
    "<div style='background:#1a1a2e;border-radius:6px;padding:10px 14px;margin:3px 0;border-left:3px solid #ff8800'>"
    "<b style='color:#ff8800'>PREMIUM+CURSO 699 EUR</b>"
    " <span style='color:#999;font-size:12px'>- Todo + curso IA Operativa (valor 297 EUR)</span></div>"
    "</div>"
    "<div style='text-align:center;padding:10px 25px 25px'>"
    "<a href='https://magodago.github.io/neo-jarvis/landing/' style='display:inline-block;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;padding:12px 30px;border-radius:6px;font-weight:bold;font-size:14px'>VER EJEMPLOS</a>"
    "</div>"
    "<div style='background:#080808;padding:15px;text-align:center;color:#555;font-size:11px'>"
    "neolabs.es | Responde BAJA si no quieres mas emails</div>"
    "</div></div>"
)

msg = MIMEMultipart("alternative")
msg["Subject"] = s
msg["From"] = "dortizs76@gmail.com"
msg["To"] = "dortizs76@gmail.com"
msg.attach(MIMEText(b, "plain", "utf-8"))
msg.attach(MIMEText(html, "html", "utf-8"))

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
r = service.users().messages().send(userId="me", body={"raw": raw}).execute()
print("ENVIADO ID:", r["id"])
print("ASUNTO:", s)
