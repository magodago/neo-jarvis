#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO LEADS PRO — Email de venta B2B v2 (corregido)
Target: Clínicas dentales
Propuesta real: Leads de negocios aliados que derivan pacientes
"""
import json, os, sys, base64, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ============================================================
# TEXTO PLANO v2 — CORREGIDO
# ============================================================
TEXTO = """Hola [NOMBRE],

Soy David, de NEO Labs. Trabajo con clínicas dentales ayudándoles a conseguir más pacientes sin depender solo de Google Ads o del boca a boca.

La idea es sencilla: en lugar de esperar a que los pacientes te encuentren, identificamos negocios de tu zona que pueden derivarte clientes. Farmacias, ortodoncistas, centros de estética, colegios, clínicas de medicina general... todos ellos tratan con personas que también necesitan dentista.

Nosotros:
  1. Buscamos esos negocios en tu zona (con Google Maps)
  2. Obtenemos sus datos de contacto (email y teléfono)
  3. Te los pasamos listos para contactar

Resultados de nuestra última campaña en clínicas dentales:

  117 clínicas dentales contactadas
  78 con email verificado
  Coste: prácticamente cero

Tú decides cómo contactarlos: una llamada, un email, una visita. Nosotros te damos los leads, tú cierras los acuerdos.

Sin permanencia. Sin riesgos.

Los planes (precios de lanzamiento):

  Starter    50 contactos/mes     97€
  Pro       150 contactos/mes    197€
  Enterprise 500 contactos/mes   397€

Si te interesa, responde a este correo y te paso una muestra de los leads que tenemos en tu zona para que veas la calidad.

David
NEO Labs
neolabs.es"""

# ============================================================
# HTML — mismo diseño NEO
# ============================================================
HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a">
<tr><td align="center" style="padding:40px 20px">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0033 100%);padding:28px 28px 16px;border-radius:12px 12px 0 0;text-align:center">
<div style="font-size:26px;font-weight:800;color:#d946ef;letter-spacing:2px">NEO <span style="color:#ffffff">LABS</span></div>
<div style="color:#555;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-top:2px">Lead Generation</div></td></tr>

<tr><td style="background-color:#111;padding:30px 28px;color:#ddd;font-size:14px;line-height:1.7">

<p style="margin:0 0 14px">Hola [NOMBRE],</p>

<p style="margin:0 0 14px">Soy David, de NEO Labs. Trabajo con cl&iacute;nicas dentales ayud&aacute;ndoles a conseguir m&aacute;s pacientes sin depender solo de Google Ads o del boca a boca.</p>

<p style="margin:0 0 14px">La idea es sencilla: en lugar de esperar a que los pacientes te encuentren, identificamos <strong>negocios de tu zona que pueden derivarte clientes</strong>. Farmacias, ortodoncistas, centros de est&eacute;tica, colegios, cl&iacute;nicas de medicina general&hellip; todos ellos tratan con personas que tambi&eacute;n necesitan dentista.</p>

<p style="margin:0 0 14px;color:#f97316;font-weight:600">C&oacute;mo funciona:</p>

<table style="margin:0 0 16px">
<tr><td style="padding:4px 8px;color:#d946ef;font-weight:700;width:24px">1.</td><td style="padding:4px 0;color:#aaa;font-size:13px">Buscamos negocios aliados en tu zona</td></tr>
<tr><td style="padding:4px 8px;color:#d946ef;font-weight:700">2.</td><td style="padding:4px 0;color:#aaa;font-size:13px">Obtenemos sus datos de contacto reales</td></tr>
<tr><td style="padding:4px 8px;color:#d946ef;font-weight:700">3.</td><td style="padding:4px 0;color:#aaa;font-size:13px">Te los pasamos listos para contactar</td></tr>
</table>

<!-- STATS -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin:18px 0">
<tr>
<td style="background:#1a1a2e;border-radius:8px;padding:12px;text-align:center;width:33%">
<div style="font-size:20px;font-weight:800;color:#d946ef">117</div>
<div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px">Clinicas contactadas</div></td>
<td style="width:4px"></td>
<td style="background:#1a1a2e;border-radius:8px;padding:12px;text-align:center;width:33%">
<div style="font-size:20px;font-weight:800;color:#06b6d4">78</div>
<div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px">Con email</div></td>
<td style="width:4px"></td>
<td style="background:#1a1a2e;border-radius:8px;padding:12px;text-align:center;width:33%">
<div style="font-size:20px;font-weight:800;color:#10b981">0</div>
<div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px">Coste/lead</div></td>
</tr>
</table>

<p style="margin:14px 0;color:#ddd">T&uacute; decides c&oacute;mo contactarlos: una llamada, un email, una visita. Nosotros te damos los leads, t&uacute; cierras los acuerdos.</p>

<p style="margin:14px 0;color:#888;font-style:italic">Sin permanencia. Sin riesgos.</p>

<!-- PRICING -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0">
<tr><td style="background:#1a1a2e;border-radius:8px;padding:10px 14px;border-left:3px solid #d946ef;font-size:12px">
<strong style="color:#d946ef">Starter</strong> &mdash; 50 contactos/mes &middot; <strong>97€</strong></td></tr>
<tr><td style="height:4px"></td></tr>
<tr><td style="background:#1a1a2e;border-radius:8px;padding:10px 14px;border-left:3px solid #06b6d4;font-size:12px">
<strong style="color:#06b6d4">Pro</strong> &mdash; 150 contactos/mes &middot; <strong>197€</strong></td></tr>
<tr><td style="height:4px"></td></tr>
<tr><td style="background:#1a1a2e;border-radius:8px;padding:10px 14px;border-left:3px solid #f97316;font-size:12px">
<strong style="color:#f97316">Enterprise</strong> &mdash; 500 contactos/mes &middot; <strong>397€</strong></td></tr>
</table>

<table cellpadding="0" cellspacing="0" style="margin:18px auto">
<tr><td style="background:linear-gradient(135deg,#d946ef,#7c3aed);border-radius:8px;text-align:center">
<a href="https://magodago.github.io/neo-jarvis/briefing/landing-leads/" style="display:inline-block;color:#fff;text-decoration:none;padding:12px 32px;font-weight:700;font-size:14px">SOLICITAR MUESTRA GRATIS</a></td></tr>
</table>

<p style="margin:14px 0 0;color:#aaa;font-size:13px">Si te interesa, responde a este correo y te paso una muestra de los leads que tenemos en tu zona para que veas la calidad.</p>

</td></tr>

<tr><td style="background:#080808;padding:16px 28px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:11px">
<div style="color:#d946ef;font-weight:600;font-size:12px">David &middot; NEO Labs</div>
<div><a href="https://magodago.github.io/neo-jarvis/briefing/landing-leads/" style="color:#777;text-decoration:none">neolabs.es</a></div>
<div style="margin-top:4px;color:#444">Si prefieres no recibir m&aacute;s correos, responde &quot;baja&quot;</div>
</td></tr></table></td></tr></table></body></html>"""

# ============================================================
# ENVIAR
# ============================================================
def enviar(email_destino, nombre_clinica):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
    SCOPES = ["https://www.googleapis.com/auth/gmail.send",
              "https://www.googleapis.com/auth/gmail.modify"]

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build("gmail", "v1", credentials=creds)

    texto = TEXTO.replace("[NOMBRE]", nombre_clinica)
    html = HTML.replace("[NOMBRE]", nombre_clinica)

    asunto = f"{nombre_clinica}, pacientes nuevos sin depender de Google Ads"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = "dortizs76@gmail.com"
    msg["To"] = email_destino
    msg["Reply-To"] = "dortizs76@gmail.com"
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return result["id"]


if __name__ == "__main__":
    print("=" * 55)
    print("  NEO LEADS PRO v2 — Email venta B2B")
    print("  Target: Clinicas dentales (CORREGIDO)")
    print("=" * 55)
    print()
    print(TEXTO)
    print()
    print("=" * 55)
    print("  Para enviar: enviar('email@clinica.com', 'Clinica Nombre')")
