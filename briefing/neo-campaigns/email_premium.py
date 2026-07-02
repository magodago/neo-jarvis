#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO CAMPAIGNS — Email de venta PREMIUM
========================================
3 versiones sectoriales de email para captar clientes de NEO Campaigns.
Cada una con gancho específico del sector + HTML premium oscuro.
"""
import os, base64, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LANDING = "https://magodago.github.io/neo-jarvis/briefing/neo-campaigns/"
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]

# ═══════════════════════════════════════════════
# VERSIÓN 1 — SEGURIDAD (target: talleres)
# ═══════════════════════════════════════════════

SEGURIDAD_ASUNTO = "{nombre}, ¿cómo llegar a decenas de talleres en 24h sin llamar en frío?"

SEGURIDAD_TEXTO = """Hola {nombre},

Imagina que mañana por la mañana decenas de talleres de {zona} reciben un email personalizado ofreciéndoles tu sistema de alarmas.

Sin llamadas en frío. Sin perder horas buscando contactos. Sin depender de Google Ads que cada vez sale más caro.

De esos talleres, varios te responderán interesados. Tú solo los llamas y cierras.

Eso es NEO Campaigns.

Nosotros hacemos tres cosas:
  1. Buscamos talleres de {zona} con datos reales (Google Places)
  2. Personalizamos un email comercial para cada uno con IA
  3. Lo enviamos y te pasamos los que responden interesados

Sin permanencia. Sin riesgos.

  Starter   50 contactos/mes    97€
  Pro      150 contactos/mes   197€  →  recomendado
  Enterprise 500 contactos/mes 397€  →  3 sectores

Si te interesa, responde a este correo y te explico cómo funciona.

David
NEO Labs — neolabs.me
"""

# ═══════════════════════════════════════════════
# VERSIÓN 2 — TPV (target: restaurantes)
# ═══════════════════════════════════════════════

TPV_ASUNTO = "{nombre}, restaurantes de {zona} esperando tu oferta de TPV"

TPV_TEXTO = """Hola {nombre},

Hay cientos de restaurantes en {zona} con email público. Y cada uno de ellos necesita un TPV.

El problema es llegar a ellos antes que tu competencia. Llamar en frío es ineficiente. Google Ads cada vez más caro. Y los directorios online están saturados de ofertas.

Nosotros te ponemos delante de ellos en 24 horas.

NEO Campaigns busca restaurantes de la zona que elijas, personaliza un email para cada uno con IA, y lo envía desde nuestra infraestructura. Los que responden interesados te los pasamos.

Sin permanencia. Sin riesgos.

  Starter   50 contactos/mes    97€
  Pro      150 contactos/mes   197€  →  más vendido
  Enterprise 500 contactos/mes 397€  →  3 sectores

Si te interesa, responde a este correo y te explico cómo funciona.

David
NEO Labs — neolabs.me
"""

# ═══════════════════════════════════════════════
# VERSIÓN 3 — SOFTWARE CLÍNICO (target: clínicas dentales)
# ═══════════════════════════════════════════════

SOFTWARE_ASUNTO = "{nombre}, clínicas dentales en {zona} esperando tu software"

SOFTWARE_TEXTO = """Hola {nombre},

Hay decenas de clínicas dentales en {zona} con email. Y muchas de ellas siguen gestionando pacientes con papel y Excel.

El reto no es tener el mejor software. Es llegar al director de la clínica antes de que tu competencia lo haga.

NEO Campaigns te da acceso directo a esas clínicas en {zona} con un email personalizado para cada una.

Cómo funciona:
  1. Buscamos clínicas dentales de {zona} (datos reales de Google Places)
  2. Personalizamos un email comercial para cada una con IA
  3. Lo enviamos y te pasamos las que responden interesadas

Sin permanencia. Sin riesgos.

  Starter   50 contactos/mes    97€
  Pro      150 contactos/mes   197€  →  recomendado
  Enterprise 500 contactos/mes 397€  →  hasta 3 sectores

Si te interesa, responde a este correo y te explico cómo funciona.

David
NEO Labs — neolabs.me
"""

SECTOR_EMAILS = {
    "seguridad": {"asunto": SEGURIDAD_ASUNTO, "texto": SEGURIDAD_TEXTO},
    "tpv": {"asunto": TPV_ASUNTO, "texto": TPV_TEXTO},
    "software": {"asunto": SOFTWARE_ASUNTO, "texto": SOFTWARE_TEXTO},
}

SECTOR_MAP = {
    "seguridad": "seguridad",
    "alarmas": "seguridad",
    "seguridad privada": "seguridad",
    "tpv": "tpv",
    "pos": "tpv",
    "datáfono": "tpv",
    "pagos": "tpv",
    "software": "software",
    "gestión clínica": "software",
    "clínica": "software",
}

# ═══════════════════════════════════════════════
# CONSTRUCCIÓN HTML
# ═══════════════════════════════════════════════

def generar_html_premium(texto_plano, nombre_empresa):
    """Genera HTML premium oscuro NEO a partir del texto plano"""
    parrafos = [p.strip() for p in texto_plano.split('\n\n') if p.strip()]
    
    cuerpo_html = ""
    for p in parrafos:
        if p.startswith("Starter") or p.startswith("  Starter"):
            # Tabla de precios
            cuerpo_html += """
            <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0">
            <tr>
              <td width="33%" style="padding:4px;vertical-align:top">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:8px;text-align:center">
                <tr><td style="padding:14px 8px">
                  <div style="font-size:10px;color:#888;letter-spacing:2px;text-transform:uppercase">STARTER</div>
                  <div style="font-size:22px;font-weight:700;color:#b8860b;margin:6px 0">97€</div>
                  <div style="font-size:10px;color:#666">/mes</div>
                  <div style="font-size:11px;color:#999;margin-top:10px;border-top:1px solid #2a2a2a;padding-top:10px">50 contactos</div>
                </td></tr></table>
              </td>
              <td width="33%" style="padding:4px;vertical-align:top">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:8px;text-align:center;border:1px solid #b8860b">
                <tr><td style="padding:14px 8px">
                  <div style="font-size:9px;color:#b8860b;letter-spacing:1px;text-transform:uppercase;font-weight:600">RECOMENDADO</div>
                  <div style="font-size:22px;font-weight:700;color:#fff;margin:6px 0">197€</div>
                  <div style="font-size:10px;color:#666">/mes</div>
                  <div style="font-size:11px;color:#999;margin-top:10px;border-top:1px solid #2a2a2a;padding-top:10px">150 contactos</div>
                </td></tr></table>
              </td>
              <td width="33%" style="padding:4px;vertical-align:top">
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:8px;text-align:center">
                <tr><td style="padding:14px 8px">
                  <div style="font-size:10px;color:#888;letter-spacing:2px;text-transform:uppercase">ENTERPRISE</div>
                  <div style="font-size:22px;font-weight:700;color:#b8860b;margin:6px 0">397€</div>
                  <div style="font-size:10px;color:#666">/mes</div>
                  <div style="font-size:11px;color:#999;margin-top:10px;border-top:1px solid #2a2a2a;padding-top:10px">500 contactos</div>
                </td></tr></table>
              </td>
            </tr></table>"""
        elif p.startswith("Sin permanencia"):
            cuerpo_html += f'<p style="margin:0 0 20px;color:#888;font-size:13px;text-align:center">{escape(p)}</p>'
        elif "GRATIS" in p or "muestra" in p.lower():
            cuerpo_html += f'<div style="background:rgba(184,134,11,0.06);border:1px solid rgba(184,134,11,0.15);border-radius:8px;padding:16px;margin:0 0 16px;text-align:center">{escape(p)}</div>'
        else:
            cuerpo_html += f'<p style="margin:0 0 14px">{escape(p)}</p>'
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body{{margin:0;padding:0;background-color:#050505;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}}
a{{color:#b8860b;text-decoration:none}}
</style></head>
<body>
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#050505">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

<!-- HEADER -->
<tr><td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0f00 100%);padding:28px 30px 18px;border-radius:12px 12px 0 0;text-align:center;border-bottom:1px solid rgba(184,134,11,0.1)">
<div style="font-size:24px;font-weight:700;letter-spacing:3px">
<span style="color:#b8860b">NEO</span> <span style="color:#ffffff">LABS</span>
</div>
</td></tr>

<!-- BODY -->
<tr><td style="background-color:#0d0d0d;padding:32px 30px;color:#d0d0d0;font-size:14px;line-height:1.7">
{cuerpo_html}
</td></tr>

<!-- CTA -->
<tr><td style="background-color:#0d0d0d;padding:0 30px 30px;text-align:center">
<a href="{LANDING}" style="display:inline-block;background:linear-gradient(135deg,#b8860b,#8b6508);color:#fff;padding:13px 34px;border-radius:8px;font-weight:600;font-size:13px;letter-spacing:0.5px;text-decoration:none">VER PLANES Y PRECIOS</a>
</td></tr>

<!-- FOOTER -->
<tr><td style="background:#080808;padding:16px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:11px">
<div>NEO Labs &mdash; <a href="{LANDING}" style="color:#b8860b">neolabs.me</a></div>
<div style="margin-top:5px;color:#444;font-size:10px">Si no quieres recibir más emails, responde &quot;baja&quot;</div>
</td></tr>

</table></td></tr></table></body></html>"""
    
    return html

def escape(text):
    """Escapa HTML básico"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

def generar_email_sector(sector_key, datos_empresa):
    """Genera el email completo para un sector específico"""
    email_info = SECTOR_EMAILS.get(sector_key)
    if not email_info:
        raise ValueError(f"Sector '{sector_key}' no encontrado. Usa: {', '.join(SECTOR_EMAILS.keys())}")
    
    asunto = email_info["asunto"].format(**datos_empresa)
    texto = email_info["texto"].format(**datos_empresa)
    html = generar_html_premium(texto, datos_empresa.get("nombre", ""))
    
    return asunto, texto, html

def construir_email(destinatario, asunto, texto_plano, html, remitente="dortizs76@gmail.com"):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Reply-To"] = remitente
    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg

def enviar_email(service, destinatario, asunto, texto_plano, html, remitente="dortizs76@gmail.com"):
    msg = construir_email(destinatario, asunto, texto_plano, html, remitente)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    time.sleep(3)
    return result["id"]

if __name__ == "__main__":
    print("=" * 55)
    print("  NEO CAMPAIGNS — EMAIL PREMIUM")
    print("=" * 55)
    print()
    for k, v in SECTOR_EMAILS.items():
        print(f"  📧 {k.upper():15s} {v['asunto'][:50]}")
    print()
    print("  Usa: from email_premium import generar_email_sector")
