#!/usr/bin/env python3
import os, base64, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build("gmail", "v1", credentials=creds)

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;">
<tr><td align="center" style="padding:30px 20px;">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#111;border-radius:12px;border:1px solid #222;overflow:hidden;">
<tr><td style="padding:30px 35px 15px;text-align:center;background:linear-gradient(135deg,#0a0a0a,#1a0033);">
<div style="font-size:11px;letter-spacing:4px;color:#ff00ff;text-transform:uppercase;">NEO LABS</div>
<div style="font-size:26px;font-weight:700;color:#fff;margin:8px 0 4px;">Web Profesional</div>
<div style="font-size:15px;color:#888;">para tu negocio en 48h</div>
</td></tr>
<tr><td style="padding:25px 35px;">
<div style="font-size:15px;line-height:1.6;color:#ddd;margin-bottom:18px;">Hola <strong style="color:#fff;">{nombre}</strong>,</div>

<div style="font-size:14px;line-height:1.7;color:#bbb;margin-bottom:20px;">
Soy David, de <strong style="color:#fff;">NEO Labs</strong>. Creamos webs profesionales para <strong style="color:#ff00ff;">{negocio}s</strong> como el tuyo.
</div>

<table width="100%" cellpadding="15" cellspacing="0" style="background:#1a0033;border-radius:10px;border:1px solid #ff00ff33;margin-bottom:20px;">
<tr><td style="text-align:center;">
<div style="font-size:30px;">🎁</div>
<div style="font-size:12px;color:#ff00ff;letter-spacing:1px;text-transform:uppercase;">REGALO</div>
<div style="font-size:14px;color:#fff;font-weight:600;">Guia: 5 claves para triplicar clientes con tu web</div>
<div style="font-size:12px;color:#888;margin-top:4px;">GRATIS - Descargala en neolabs.es/guias</div>
</td></tr></table>

<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">

<tr><td style="padding:14px 18px;background:#111;border-radius:8px;border:1px solid #222;display:block;margin-bottom:8px;">
<table width="100%"><tr>
<td width="65%" style="font-size:13px;color:#aaa;">BASICA<br><span style="font-size:11px;color:#666;">Web responsive, SEO local, formulario, hosting 1 ano</span></td>
<td width="35%" style="text-align:right;font-size:24px;font-weight:700;color:#fff;">299<span style="font-size:14px;color:#888;"> EUR</span></td>
</tr></table>
</td></tr>

<tr><td style="padding:16px 20px;background:linear-gradient(135deg,#1a0033,#111);border-radius:8px;border:2px solid #ff00ff;display:block;margin-bottom:8px;">
<div style="float:right;background:#ff00ff;color:#fff;font-size:9px;padding:2px 8px;border-radius:3px;letter-spacing:1px;">MAS ELEGIDO</div>
<table width="100%"><tr>
<td width="65%">
<div style="font-size:14px;font-weight:700;color:#ff00ff;">PREMIUM</div>
<div style="font-size:12px;color:#ccc;">Diseno premium, SEO completo, blog, panel admin, WhatsApp integrado</div>
</td>
<td width="35%" style="text-align:right;font-size:28px;font-weight:700;color:#fff;">599<span style="font-size:14px;color:#888;"> EUR</span></td>
</tr></table>
</td></tr>

<tr><td style="padding:14px 18px;background:#111;border-radius:8px;border:1px solid #222;display:block;">
<table width="100%"><tr>
<td width="65%" style="font-size:13px;color:#aaa;">PREMIUM + CURSO IA<br><span style="font-size:11px;color:#666;">Todo lo de PREMIUM + curso IA Operativa (valor 297 EUR)</span></td>
<td width="35%" style="text-align:right;font-size:24px;font-weight:700;color:#fff;">699<span style="font-size:14px;color:#888;"> EUR</span></td>
</tr></table>
</td></tr></table>

<div style="font-size:12px;color:#4ade80;margin-bottom:18px;">
✅ Sin cuotas  ✅ Hosting 1 ano  ✅ SEO Maps  ✅ Diseno a medida
</div>

<div style="text-align:center;margin:20px 0;">
<a href="https://magodago.github.io/neo-jarvis/landing/" style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;border-radius:8px;font-size:15px;font-weight:600;">VER EJEMPLOS →</a>
</div>

<div style="font-size:13px;color:#666;text-align:center;margin-bottom:20px;">
Te interesa? Responde a este email y te enseno casos reales de {negocio}s como el tuyo. Sin compromiso.
</div>

<hr style="border:none;border-top:1px solid #222;margin:0 0 15px;">
<div style="font-size:13px;color:#888;line-height:1.6;">
<strong style="color:#fff;">David Ortiz</strong> · CEO NEO Labs<br>
<a href="https://neolabs.es" style="color:#ff00ff;text-decoration:none;">neolabs.es</a> · <span style="color:#555;">658 237 988</span>
</div>
</td></tr>
<tr><td style="padding:15px;text-align:center;font-size:10px;color:#444;border-top:1px solid #111;">
NEO Labs · Madrid · Si no quieres recibir mas emails, responde BAJA
</td></tr></table>
</td></tr></table>
</body></html>"""

PLAIN = """Hola {nombre},

Soy David de NEO Labs. Creamos webs profesionales para {negocio}s como el tuyo.

Ofrecemos 3 planes:

- BASICA 299 EUR: web responsive, SEO local, formulario, hosting 1 ano
- PREMIUM 599 EUR (el mas elegido): diseno premium, SEO completo, blog, panel admin, WhatsApp
- PREMIUM+CURSO 699 EUR: todo + curso IA Operativa (valor 297 EUR)

Sin cuotas. Hosting incluido. Diseno a medida.

Ver ejemplos: https://magodago.github.io/neo-jarvis/landing/

Te interesa? Responde a este email sin compromiso.

David Ortiz - NEO Labs
neolabs.es | 658 237 988 (WhatsApp)"""

def send_test():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "NEO Labs - Test formato email premium (revisar)"
    msg["From"] = "dortizs76@gmail.com"
    msg["To"] = "formulasia76@gmail.com"
    
    html = HTML.format(nombre="Restaurante Los Bravos", negocio="restaurante")
    plain = PLAIN.format(nombre="Restaurante Los Bravos", negocio="restaurante")
    
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print("ENVIADO! ID:", result["id"])
    print("Revisa formulasia76@gmail.com")

send_test()
