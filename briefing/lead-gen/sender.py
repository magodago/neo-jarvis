#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sender NEO: envia emails HTML con marca NEO via Gmail API"""
import os, csv, base64, json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
TOKEN_PATH = os.path.expanduser("~/.hermes/google_token.json")
BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LANDING = "https://magodago.github.io/neo-jarvis/landing/"

EMAIL_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

<!-- HEADER NEO -->
<tr>
<td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0033 100%);padding:30px 30px 20px;border-radius:12px 12px 0 0;text-align:center">
<div style="font-size:32px;font-weight:bold;color:#ff00ff;letter-spacing:3px">NEO <span style="color:#ffffff">LABS</span></div>
<div style="color:#666;font-size:12px;margin-top:4px">SOLUCIONES DIGITALES PROFESIONALES</div>
</td>
</tr>

<!-- BODY -->
<tr>
<td style="background-color:#111;padding:30px;border-radius:0;color:#e0e0e0;font-size:15px;line-height:1.6">
{BODY_HTML}
</td>
</tr>

<!-- PLANES -->
<tr>
<td style="background-color:#111;padding:0 30px 20px">
<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="background:#1a1a2e;border-radius:8px;padding:15px;margin-bottom:8px;border-left:3px solid #ff00ff">
<div style="color:#ff00ff;font-size:12px;font-weight:bold;text-transform:uppercase">Basica - 299 EUR</div>
<div style="color:#aaa;font-size:12px;margin-top:4px">Web responsive + SEO basico + formulario + hosting 1 ano</div>
</td>
</tr>
<tr><td style="height:6px"></td></tr>
<tr>
<td style="background:#1a1a2e;border-radius:8px;padding:15px;border-left:3px solid #00ffff">
<div style="color:#00ffff;font-size:12px;font-weight:bold;text-transform:uppercase">Premium - 599 EUR (mas popular)</div>
<div style="color:#aaa;font-size:12px;margin-top:4px">Diseno premium + SEO completo + blog + panel de administracion</div>
</td>
</tr>
<tr><td style="height:6px"></td></tr>
<tr>
<td style="background:#1a1a2e;border-radius:8px;padding:15px;border-left:3px solid #ff8800">
<div style="color:#ff8800;font-size:12px;font-weight:bold;text-transform:uppercase">Premium+Curso - 699 EUR</div>
<div style="color:#aaa;font-size:12px;margin-top:4px">Todo lo anterior + curso IA Operativa (valorado en 297 EUR)</div>
</td>
</tr>
</table>
</td>
</tr>

<!-- CTA -->
<tr>
<td style="background-color:#111;padding:20px 30px 30px;text-align:center">
<a href="{LANDING}" style="display:inline-block;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;padding:14px 40px;border-radius:8px;font-weight:bold;font-size:15px">VER EJEMPLOS REALES</a>
</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="background:#080808;padding:20px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:12px">
<div style="margin-bottom:8px">NEO Labs - Soluciones Digitales</div>
<div><a href="{LANDING}" style="color:#ff00ff;text-decoration:none">neolabs.es</a></div>
<div style="margin-top:6px;color:#444">Si no quieres recibir mas emails, responde "baja"</div>
</td>
</tr>

</table>
</td></tr></table>
</body>
</html>"""

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("gmail", "v1", credentials=creds)

def send_html(service, to, subject, body_text, nombre):
    body_html_clean = body_text.replace("\n", "<br>")
    
    html_content = EMAIL_HTML.format(
        BODY_HTML=body_html_clean,
        LANDING=LANDING,
    )
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "dortizs76@gmail.com"
    msg["To"] = to
    msg["Reply-To"] = "dortizs76@gmail.com"
    
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return result["id"]

def send_all():
    service = get_service()

    csv_path = os.path.join(OUTPUT_DIR, "emails.csv")
    if not os.path.exists(csv_path):
        print("No hay emails. Ejecuta personalizer.py primero.")
        return

    with open(csv_path, "r", encoding="utf-8") as f:
        emails = list(csv.DictReader(f))

    sent_path = os.path.join(LOGS_DIR, "sent.csv")
    sent_emails = set()
    if os.path.exists(sent_path):
        with open(sent_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sent_emails.add(row.get("email_destino", ""))

    con_email = [e for e in emails if e.get("email_destino", "").strip()]
    pendientes = [e for e in con_email if e["email_destino"] not in sent_emails]

    print("Total con email: " + str(len(con_email)))
    print("Ya enviados: " + str(len(con_email) - len(pendientes)))
    print("Pendientes: " + str(len(pendientes)))

    if not pendientes:
        print("Todos enviados ya!")
        return

    print("\nEnviando HTML con marca NEO...")
    sent_log = []

    for i, email in enumerate(pendientes):
        to = email["email_destino"]
        nombre = email["nombre"]
        subject = email["asunto"]
        body = email["cuerpo"]

        try:
            msg_id = send_html(service, to, subject, body, nombre)
            sent_log.append({
                "email_destino": to, "nombre": nombre,
                "asunto": subject, "message_id": msg_id, "status": "sent",
            })
            print("  [" + str(i + 1) + "/" + str(len(pendientes)) + "] OK " + nombre + " <" + to + ">")
        except Exception as e:
            print("  [" + str(i + 1) + "/" + str(len(pendientes)) + "] ERR " + nombre + " <" + to + ">: " + str(e))
            sent_log.append({
                "email_destino": to, "nombre": nombre,
                "asunto": subject, "message_id": "", "status": "error: " + str(e),
            })

    with open(sent_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email_destino", "nombre", "asunto", "message_id", "status"])
        if os.path.getsize(sent_path) == 0:
            w.writeheader()
        w.writerows(sent_log)

    enviados = sum(1 for s in sent_log if s["status"] == "sent")
    print("\nEnviados: " + str(enviados) + "/" + str(len(pendientes)))

if __name__ == "__main__":
    send_all()
