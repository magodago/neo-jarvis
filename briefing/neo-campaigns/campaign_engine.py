#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO CAMPAIGNS — Motor de campañas automatizadas
================================================
Lanza una campaña para un cliente: busca leads del sector,
personaliza con DeepSeek y envía desde Gmail.

Uso:
  python3 campaign_engine.py --cliente "SegurTaller SL" --sector talleres --zona Madrid
  python3 campaign_engine.py --cliente "TPV Express" --sector restaurantes --zona "Madrid Centro"
"""
import os, sys, json, base64, time, sqlite3, csv, argparse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE = os.path.dirname(os.path.abspath(__file__))
LEAD_DIR = os.path.join(os.path.dirname(BASE), "lead-gen", "data")
LOGS_DIR = os.path.join(os.path.dirname(BASE), "lead-gen", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]

# ── Plantillas por sector ──
PLANTILLAS = {
    "talleres": {
        "asunto": "{nombre_taller}, protege tu taller con las mejores alarmas",
        "texto": """Hola {nombre_taller},

Te escribo de {cliente}, especialistas en seguridad para talleres mecánicos.

Sabemos que en un taller tienes herramientas, recambios y vehículos de clientes que pueden ser objetivo de robos si no tienes las medidas adecuadas.

{cliente} ofrece:
  • Sistemas de alarma con sensores de movimiento
  • Cámaras de vigilancia HD con visión nocturna
  • Control de acceso para empleados
  • Conexión directa con central receptora 24h
  • Instalación en 24h sin obras

Varios talleres de tu zona ya confían en nosotros. Si te interesa, responde a este email y te paso un presupuesto sin compromiso.

Un saludo,
{nombre_vendedor}
{cliente}
{telefono}
"""
    },
    "restaurantes": {
        "asunto": "{nombre_restaurante}, ahorra en comisiones de TPV",
        "texto": """Hola {nombre_restaurante},

Te escribo de {cliente}, especialistas en soluciones de pago para hostelería.

Sabemos que los restaurantes pierden dinero cada mes en comisiones de datáfono y tiempo gestionando cobros.

{cliente} te ofrece:
  • TPV con comisiones desde 0.3% por operación
  • Pago en mesa con QR — tus clientes pagan sin esperar
  • Integración con plataformas de delivery
  • Informes de ventas en tiempo real
  • Sin permanencia ni costes ocultos

Más de 50 restaurantes ya han cambiado y ahorran una media de 200€/mes.

¿Quieres verlo? Responde a este email y te paso los detalles sin compromiso.

Un saludo,
{nombre_vendedor}
{cliente}
{telefono}
"""
    },
    "clinicas dentales": {
        "asunto": "{nombre_clinica}, gestiona tu clínica con un software moderno",
        "texto": """Hola {nombre_clinica},

Te escribo de {cliente}, especialistas en software de gestión para clínicas dentales.

Sabemos que el tiempo perdido con agendas manuales, historiales en papel y recordatorios sin automatizar se traduce en pacientes que no vuelven.

{cliente} ofrece:
  • Agenda digital con recordatorios automáticos
  • Historial clínico online desde cualquier dispositivo
  • Gestión de facturación y seguros
  • Estadísticas de pacientes y rentabilidad
  • Integración sin complicaciones

Varias clínicas de tu zona ya lo usan y han reducido un 30% las ausencias.

¿Te interesa? Responde y te enseño cómo funciona en 5 minutos.

Un saludo,
{nombre_vendedor}
{cliente}
{telefono}
"""
    }
}

# ── Mapeo de sectores (normalizar) ──
SECTOR_MAP = {
    "taller": "talleres",
    "talleres": "talleres",
    "mecanico": "talleres",
    "restaurant": "restaurantes",
    "restaurante": "restaurantes",
    "hosteleria": "restaurantes",
    "dental": "clinicas dentales",
    "dentista": "clinicas dentales",
    "clinica dental": "clinicas dentales",
    "clinicas dentales": "clinicas dentales",
}

def normalizar_sector(sector):
    s = sector.lower().strip()
    return SECTOR_MAP.get(s, s)

def cargar_leads(sector, zona=None, limite=100):
    """Carga leads del sector desde la DB de leads"""
    db_path = os.path.join(LEAD_DIR, "leads.db")
    if not os.path.exists(db_path):
        print(f"⚠️  No se encuentra DB de leads en {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    query = "SELECT nombre, email, ciudad, sector, telefono FROM leads WHERE "
    params = []
    
    # Filtro por sector
    if sector:
        query += "(LOWER(sector) LIKE ? OR LOWER(sector) LIKE ?) "
        params.append(f"%{sector}%")
        params.append(f"%{sector.rstrip('s')}%")
    
    # Filtro por zona
    if zona:
        query += "AND LOWER(ciudad) LIKE ? "
        params.append(f"%{zona.lower()}%")
    
    query += "AND email IS NOT NULL AND email != '' LIMIT ?"
    params.append(limite)
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    print(f"   Leads encontrados: {len(rows)}")
    return rows

def generar_email_personalizado(plantilla, lead, cliente_info):
    """Rellena la plantilla con datos del lead y del cliente"""
    nombre = lead[0] or "Negocio"
    ciudad = lead[2] or ""
    
    texto = plantilla["texto"].format(
        nombre_taller=nombre,
        nombre_restaurante=nombre,
        nombre_clinica=nombre,
        cliente=cliente_info["nombre"],
        nombre_vendedor=cliente_info.get("vendedor", "El equipo comercial"),
        telefono=cliente_info.get("telefono", ""),
    )
    asunto = plantilla["asunto"].format(
        nombre_taller=nombre,
        nombre_restaurante=nombre,
        nombre_clinica=nombre,
    )
    
    return asunto, texto

def construir_email(destinatario, asunto, texto_plano, html, remitente="dortizs76@gmail.com"):
    """Construye el MIMEMultipart"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Reply-To"] = remitente
    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg

def enviar_campana(cliente_info, sector, zona, limite=50):
    """Ejecuta la campaña completa"""
    print(f"\n{'='*55}")
    print(f"  NEO CAMPAIGN ENGINE")
    print(f"  Cliente: {cliente_info['nombre']}")
    print(f"  Sector:  {sector}")
    print(f"  Zona:    {zona or 'Todas'}")
    print(f"  Límite:  {limite} leads")
    print(f"{'='*55}\n")
    
    # ── 1. Conectar Gmail ──
    print("📧 Gmail...", end=" ", flush=True)
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        print(f"✅ {profile['emailAddress']}")
    except Exception as e:
        print(f"❌ {e}")
        return
    
    # ── 2. Cargar leads ──
    print(f"\n🔍 Buscando {sector} en {zona or 'todas las zonas'}...")
    leads = cargar_leads(sector, zona, limite)
    if not leads:
        print("❌ No se encontraron leads para este sector/zona")
        return
    
    # ── 3. Obtener plantilla ──    
    template_key = normalizar_sector(sector)
    plantilla = PLANTILLAS.get(template_key)
    if not plantilla:
        opts = ", ".join(PLANTILLAS.keys())
        print(f"❌ Sector '{sector}' no tiene plantilla. Disponibles: {opts}")
        return
    
    # ── 4. Enviar ──
    print(f"\n🚀 Enviando campaña a {len(leads)} leads...\n")
    
    ok = 0
    errors = 0
    log = []
    
    for i, lead in enumerate(leads):
        nombre, email, ciudad, sector_lead, telefono = lead
        
        asunto, texto = generar_email_personalizado(plantilla, lead, cliente_info)
        
        # Versión HTML simple
        html_texto = texto.replace("\n", "<br>")
        html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;font-family:sans-serif">
<table width="100%"><tr><td align="center" style="padding:30px 20px">
<table width="600" style="background:#111;border-radius:12px">
<tr><td style="padding:30px;color:#e0e0e0;font-size:14px;line-height:1.7">
{html_texto}
</td></tr>
<tr><td style="padding:0 30px 30px;text-align:center;color:#555;font-size:11px">
{cliente_info['nombre']} · Si no quiere recibir más emails, responda "baja"</td></tr>
</table></td></tr></table></body></html>"""
        
        try:
            msg = construir_email(email, asunto, texto, html)
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
            ok += 1
            log.append({"email": email, "nombre": nombre, "message_id": result["id"], "status": "sent"})
            print(f"  [{i+1}/{len(leads)}] ✅ {nombre[:28]:28s} → {email}")
        except Exception as e:
            if "429" in str(e):
                print(f"\n⚠️  Rate limit alcanzado. Enviados: {ok}. Reanuda más tarde.")
                break
            errors += 1
            log.append({"email": email, "nombre": nombre, "message_id": "", "status": f"error: {str(e)[:60]}"})
            print(f"  [{i+1}/{len(leads)}] ❌ {nombre[:28]:28s}: {str(e)[:60]}")
        
        time.sleep(3)
    
    # ── 5. Guardar log ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = os.path.join(LOGS_DIR, f"campana_{cliente_info['nombre'].lower().replace(' ','_')}_{timestamp}.csv")
    with open(log_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email", "nombre", "message_id", "status"])
        w.writeheader()
        w.writerows(log)
    
    print(f"\n{'='*55}")
    print(f"  📊 CAMPAÑA COMPLETADA")
    print(f"  Enviados: {ok} | Errores: {errors}")
    print(f"  Log: {log_file}")
    print(f"{'='*55}")
    
    return log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEO Campaign Engine")
    parser.add_argument("--cliente", required=True, help="Nombre del cliente")
    parser.add_argument("--sector", required=True, help="Sector: talleres, restaurantes, clinicas dentales")
    parser.add_argument("--zona", default="", help="Zona geográfica (ej: Madrid)")
    parser.add_argument("--vendedor", default="El equipo comercial", help="Nombre del vendedor")
    parser.add_argument("--telefono", default="", help="Teléfono de contacto")
    parser.add_argument("--limite", type=int, default=50, help="Máximo de leads a enviar")
    
    args = parser.parse_args()
    
    cliente_info = {
        "nombre": args.cliente,
        "vendedor": args.vendedor,
        "telefono": args.telefono,
    }
    
    enviar_campana(cliente_info, args.sector, args.zona or None, args.limite)
