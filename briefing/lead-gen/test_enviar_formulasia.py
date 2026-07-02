#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envío de prueba a formulasia — email NEO Leads Pro para clínicas dentales"""
import os, base64, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]

EMAIL_PLAIN = """Hola,

Soy David, de NEO Labs. Trabajo con clínicas dentales ayudándoles a conseguir más pacientes sin depender solo de Google Ads o del boca a boca.

La idea es sencilla: en lugar de esperar a que los pacientes te encuentren, identificamos negocios de tu zona que pueden derivarte clientes. Farmacias, ortodoncistas, centros de estética, colegios, clínicas de medicina general... todos ellos tratan con personas que también necesitan dentista.

Nosotros hacemos tres cosas:
  1. Buscamos esos negocios en tu zona
  2. Obtenemos sus datos de contacto (email y teléfono)
  3. Te los pasamos listos para contactar

Resultados en clínicas dentales: 117 clínicas analizadas | 78 con email | coste 0€

Sin permanencia. Sin riesgos.

  Starter    50 contactos/mes     97€/mes
  Pro       150 contactos/mes    197€/mes
  Enterprise 500 contactos/mes   397€/mes

Si te interesa, responde a este email y te paso una muestra de los leads de tu zona para que veas la calidad antes de decidir.

Un saludo,
David
NEO Labs
neolabs.es"""

HTML_CONTENT = """
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

<!-- HEADER -->
<tr><td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0033 100%);padding:30px 30px 20px;border-radius:12px 12px 0 0;text-align:center">
<div style="font-size:28px;font-weight:bold;letter-spacing:3px">
<span style="color:#ff00ff">NEO</span> <span style="color:#ffffff">LABS</span>
</div>
<div style="color:#666;font-size:11px;margin-top:4px">CAPTACIÓN DE PACIENTES</div></td></tr>

<!-- BODY -->
<tr><td style="background-color:#111;padding:30px;color:#e0e0e0;font-size:15px;line-height:1.7">

<p style="margin:0 0 16px">Hola,</p>

<p style="margin:0 0 16px">Soy David, de <strong style="color:#ff00ff">NEO Labs</strong>. Trabajo con clínicas dentales ayudándoles a conseguir más pacientes sin depender solo de Google Ads o del boca a boca.</p>

<p style="margin:0 0 16px">La idea es sencilla: en lugar de esperar a que los pacientes te encuentren, identificamos negocios de tu zona que pueden derivarte clientes. Farmacias, ortodoncistas, centros de estética, colegios, clínicas de medicina general&hellip; todos ellos tratan con personas que también necesitan dentista.</p>

<p style="margin:0 0 16px">Nosotros hacemos tres cosas:</p>

<ol style="margin:0 0 16px;padding-left:20px">
<li style="margin-bottom:8px">Buscamos esos negocios en tu zona</li>
<li style="margin-bottom:8px">Obtenemos sus datos de contacto (email y teléfono)</li>
<li style="margin-bottom:8px">Te los pasamos listos para contactar</li>
</ol>

<!-- RESULTADO DESTACADO -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a0033 0%,#0a0a0a 100%);border-radius:8px;margin:0 0 20px">
<tr><td align="center" style="padding:16px">
<div style="font-size:13px;color:#999">RESULTADOS EN CLÍNICAS DENTALES</div>
<div style="font-size:24px;font-weight:bold;color:#ff00ff;margin:8px 0">117 clínicas &middot; 78 con email</div>
<div style="font-size:12px;color:#666">coste de captación: <strong style="color:#4ade80">0€</strong></div>
</td></tr></table>

<p style="margin:0 0 8px;font-size:13px;color:#999">Sin permanencia. Sin riesgos.</p>

<!-- PACKS -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px">
<tr>
<td width="33%" style="padding:4px;vertical-align:top">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:8px;text-align:center">
<tr><td style="padding:12px 8px">
<div style="font-size:11px;color:#999">STARTER</div>
<div style="font-size:18px;font-weight:bold;color:#ff00ff;margin:4px 0">97€</div>
<div style="font-size:11px;color:#666">/mes</div>
<div style="font-size:11px;color:#888;margin-top:8px;border-top:1px solid #333;padding-top:8px">50 contactos</div>
</td></tr></table>
</td>
<td width="33%" style="padding:4px;vertical-align:top">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:8px;text-align:center;border:1px solid #ff00ff">
<tr><td style="padding:12px 8px">
<div style="font-size:11px;color:#ff00ff">RECOMENDADO</div>
<div style="font-size:18px;font-weight:bold;color:#fff;margin:4px 0">197€</div>
<div style="font-size:11px;color:#666">/mes</div>
<div style="font-size:11px;color:#888;margin-top:8px;border-top:1px solid #333;padding-top:8px">150 contactos</div>
</td></tr></table>
</td>
<td width="33%" style="padding:4px;vertical-align:top">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:8px;text-align:center">
<tr><td style="padding:12px 8px">
<div style="font-size:11px;color:#999">ENTERPRISE</div>
<div style="font-size:18px;font-weight:bold;color:#ff00ff;margin:4px 0">397€</div>
<div style="font-size:11px;color:#666">/mes</div>
<div style="font-size:11px;color:#888;margin-top:8px;border-top:1px solid #333;padding-top:8px">500 contactos</div>
</td></tr></table>
</td>
</tr></table>

<p style="margin:0 0 16px">Si te interesa, responde a este email y te paso una <strong style="color:#ff00ff">muestra gratuita</strong> de los leads de tu zona para que veas la calidad antes de decidir.</p>

</td></tr>

<!-- CTA -->
<tr><td style="background-color:#111;padding:0 30px 30px;text-align:center">
<a href="https://magodago.github.io/neo-jarvis/briefing/landing-leads/" style="display:inline-block;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;padding:14px 36px;border-radius:8px;font-weight:bold;font-size:14px">QUIERO VER UNA MUESTRA GRATIS</a>
</td></tr>

<!-- FOOTER -->
<tr><td style="background:#080808;padding:16px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:11px">
<div>NEO Labs &mdash; Captación de Pacientes</div>
<div><a href="https://magodago.github.io/neo-jarvis/briefing/landing-leads/" style="color:#ff00ff;text-decoration:none">neolabs.es</a></div>
<div style="margin-top:6px;color:#444">Si no quieres recibir más emails, responde &quot;baja&quot;</div>
<div style="margin-top:4px;color:#333;font-size:10px">Este correo está dirigido a responsables de clínicas dentales.</div>
</td></tr></table>
</td></tr></table>
"""

def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    print("📧 Conectando Gmail...", end=" ", flush=True)
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    print(f"✅ {profile['emailAddress']}")

    destino = "formulasia76@gmail.com"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Clínica dental, pacientes nuevos sin depender de Google Ads"
    msg["From"] = "dortizs76@gmail.com"
    msg["To"] = destino
    msg["Reply-To"] = "dortizs76@gmail.com"
    msg.attach(MIMEText(EMAIL_PLAIN, "plain", "utf-8"))
    msg.attach(MIMEText(HTML_CONTENT, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    print(f"\n✅ ENVIADO a {destino}")
    print(f"   Message ID: {result['id']}")
    print(f"   Abre Gmail y revísalo.")

if __name__ == "__main__":
    main()
