#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO CAMPAIGNS — Plantillas de email
====================================
Contiene:
  1. SALES_EMAIL → Email para vender el servicio NEO Campaigns a empresas
  2. PLANTILLAS_CAMPANA → 3 templates sectoriales para enviar a leads finales
"""
import os, json, base64, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── CONFIG ──
LANDING = "https://neo.neolabs.me/briefing/neo-campaigns/"
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]

# ═══════════════════════════════════════════════
# 1. EMAIL DE VENTA — para captar clientes de NEO Campaigns
# ═══════════════════════════════════════════════

SALES_EMAIL_SUBJECT = "[EMPRESA], ¿quieres llegar a {sector} sin pagar anuncios?"

SALES_EMAIL_TEXTO = """Hola,

Soy David, de NEO Labs.

Trabajo con empresas que necesitan llegar a negocios locales concretos (restaurantes, talleres, clínicas...) pero se cansan de perder tiempo y dinero en Google Ads que no convierten.

Nosotros hacemos una cosa sencilla:
  1. Buscamos todos los negocios del sector que quieras en la zona que elijas
  2. Personalizamos un email comercial con IA
  3. Lo enviamos desde nuestra infraestructura

Resultado: tu campaña llega a {num_leads} {sector} de {zona}, sin que muevas un dedo.

Ejemplo real: más de 1.000 restaurantes prospectados solo en Madrid capital.

Te paso los negocios que responden interesados. Tú solo cierras.

Precios desde 97€/mes. Sin permanencia.

¿Te interesa? Respondeme y te cuento cómo empezamos.

David | NEO Labs
neo.neolabs.me
"""

# ═══════════════════════════════════════════════
# 2. PLANTILLAS DE CAMPAÑA — emails que enviamos a los leads finales
# ═══════════════════════════════════════════════

CAMPANA_TALLERES = {
    "asunto": "[Nombre taller], ¿tienes tus instalaciones aseguradas?",
    "texto": """Hola [Nombre],

Te escribo de parte de [CLIENTE], empresa especializada en seguridad para talleres mecánicos en [Zona].

Sabemos que en un taller tienes herramientas, recambios y vehículos de clientes que son un blanco fácil si no tienes las medidas adecuadas.

[CLIENTE] ofrece:
  • Sistemas de alarma con sensor de movimiento y rotura de cristales
  • Cámaras de vigilancia con visión nocturna
  • Control de acceso para empleados
  • Conexión directa con central receptora de alarmas 24h
  • Instalación sin obras

Varios talleres de [Zona] ya confían en nosotros. Si te interesa, respondeme y te paso un presupuesto sin compromiso.

Un saludo,
[VENDEDOR]
[CLIENTE]
[TELEFONO]
"""
}

CAMPANA_RESTAURANTES = {
    "asunto": "[Nombre restaurante], cobra más rápido y sin comisiones abusivas",
    "texto": """Hola [Nombre],

Te escribo de parte de [CLIENTE], especialistas en TPV y soluciones de pago para hostelería en [Zona].

Sabemos que los restaurantes como el tuyo pierden dinero cada mes en comisiones de datáfono y tiempo gestionando cobros.

[CLIENTE] te ofrece:
  • TPV con las comisiones más bajas del mercado (0.3% por operación)
  • Pago en mesa con QR — tus clientes pagan sin esperar
  • Integración con las principales plataformas de delivery
  • Informes de ventas en tiempo real
  • Sin permanencia ni costes ocultos

Más de 50 restaurantes en [Zona] ya han cambiado y ahorran una media de 200€/mes.

¿Te interesa? Respondeme y te paso los detalles sin compromiso.

Un saludo,
[VENDEDOR]
[CLIENTE]
[TELEFONO]
"""
}

CAMPANA_DENTISTAS = {
    "asunto": "[Nombre clínica], gestiona tus pacientes con un software moderno",
    "texto": """Hola [Nombre],

Te escribo de parte de [CLIENTE], especialistas en software de gestión para clínicas dentales.

Sabemos que en una clínica como la tuya, el tiempo perdido con agendas de papel, historiales desordenados y recordatorios manuales se traduce en pacientes que no vuelven.

[CLIENTE] ofrece:
  • Agenda digital con recordatorios automáticos a pacientes
  • Historial clínico digital accesible desde cualquier dispositivo
  • Gestión de facturación y seguros
  • Estadísticas de pacientes, tratamientos y rentabilidad
  • Integración con tu sistema actual sin complicaciones

Varias clínicas de tu zona ya lo usan y han reducido un 30% las ausencias.

¿Te interesa? Respondeme y te enseño cómo funciona en 5 minutos.

Un saludo,
[VENDEDOR]
[CLIENTE]
[TELEFONO]
"""
}

PLANTILLAS = {
    "talleres": CAMPANA_TALLERES,
    "restaurantes": CAMPANA_RESTAURANTES,
    "clinicas dentales": CAMPANA_DENTISTAS,
    "dental": CAMPANA_DENTISTAS,
}

# ═══════════════════════════════════════════════
# 3. CONSTRUCCIÓN DE EMAIL HTML
# ═══════════════════════════════════════════════

HTML_WRAPPER = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">
<tr><td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0033 100%);padding:30px 30px 20px;border-radius:12px 12px 0 0;text-align:center">
<div style="font-size:28px;font-weight:bold;letter-spacing:3px">
<span style="color:#ff00ff">NEO</span> <span style="color:#ffffff">CAMPAIGNS</span>
</div>
<div style="color:#666;font-size:11px;margin-top:4px">EN NOMBRE DE TU EMPRESA</div></td></tr>
<tr><td style="background-color:#111;padding:30px;color:#e0e0e0;font-size:15px;line-height:1.7">
[CUERPO]
</td></tr>
<tr><td style="background-color:#111;padding:0 30px 30px;text-align:center">
<a href="[LANDING]" style="display:inline-block;background:linear-gradient(135deg,#b8860b,#8b6508);color:#fff;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:bold;font-size:14px">SABER MÁS</a>
</td></tr>
<tr><td style="background:#080808;padding:16px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:11px">
<div>NEO Campaigns — Captación B2B</div>
<div style="margin-top:6px;color:#444">Si no quieres recibir más emails, responde &quot;baja&quot;</div>
</td></tr>
</table></td></tr></table></body></html>
"""

def generar_html_campana(texto_plano, landing=None):
    """Convierte texto plano en HTML con el wrapper NEO"""
    html_body = texto_plano.replace("\n", "<br>").replace("[LANDING]", landing or LANDING)
    html = HTML_WRAPPER.replace("[CUERPO]", html_body).replace("[LANDING]", landing or LANDING)
    texto_plano_final = texto_plano.replace("[LANDING]", landing or LANDING)
    return texto_plano_final, html

def construir_email(destinatario, asunto, texto_plano, html, remitente="david@neolabs.me"):
    """Construye el MIMEMultipart listo para enviar"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Reply-To"] = remitente
    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg

def enviar_email(service, destinatario, asunto, texto_plano, html, remitente="david@neolabs.me"):
    """Envía un email via Gmail API, espera 3s entre envíos por rate limit"""
    msg = construir_email(destinatario, asunto, texto_plano, html, remitente)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    time.sleep(3)
    return result["id"]


if __name__ == "__main__":
    print("=" * 55)
    print("  NEO CAMPAIGNS — PLANTILLAS")
    print("=" * 55)
    print()
    print(f"  📧 Sales email: {SALES_EMAIL_SUBJECT}")
    print(f"  📋 Plantillas disponibles:")
    for k in PLANTILLAS:
        print(f"     • {k}")
    print()
    print("  Usa: from plantillas_campana import PLANTILLAS, construir_email, SALES_EMAIL_TEXTO")
    print()
