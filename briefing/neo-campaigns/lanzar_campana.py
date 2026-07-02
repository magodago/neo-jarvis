#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO CAMPAIGNS — Lanzador de campañas
=====================================
Lee clientes.db y envía el email de venta premium a todos los clientes
que tengan email y no hayan recibido envío.

Uso:
  python3 lanzar_campana.py                          # Enviar a todos los pendientes
  python3 lanzar_campana.py --test formulasia76@gmail.com  # Enviar prueba
  python3 lanzar_campana.py --sector seguridad       # Solo un sector
"""
import os, sys, json, base64, time, sqlite3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "clientes", "clientes.db")
sys.path.insert(0, BASE)
from email_premium import SECTOR_EMAILS, SECTOR_MAP, generar_html_premium, escape
from config import TOKEN_FILE, SCOPES

LANDING = "https://magodago.github.io/neo-jarvis/briefing/neo-campaigns/"
LOGS_DIR = os.path.join(BASE, "..", "lead-gen", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# ── Gmail auth ──
def get_gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            print("❌ No hay token de Gmail válido. Ejecuta primero la autenticación.")
            sys.exit(1)
    return build("gmail", "v1", credentials=creds)

def construir_email(destinatario, asunto, texto_plano, html, remitente="david@neolabs.me"):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Reply-To"] = "david@neolabs.me"
    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg

def enviar_email(service, destinatario, asunto, texto_plano, html):
    msg = construir_email(destinatario, asunto, texto_plano, html)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    time.sleep(2)
    return result["id"]

def generar_email_para_cliente(nombre, sector_comprador):
    """Genera el email de venta para un cliente de NEO Campaigns."""
    sector_key = SECTOR_MAP.get(sector_comprador.lower(), sector_comprador.lower())
    if sector_key not in SECTOR_EMAILS:
        # Fallback a seguridad si no encontramos el sector
        sector_key = "seguridad"
    
    datos = {"nombre": nombre}
    email_info = SECTOR_EMAILS[sector_key]
    asunto = email_info["asunto"].format(**datos)
    texto = email_info["texto"].format(**datos)
    html = generar_html_premium(texto, nombre)
    
    return asunto, texto, html

def enviar_prueba():
    """Envía email de prueba a formulasia76@gmail.com"""
    service = get_gmail_service()
    destinatario = "formulasia76@gmail.com"
    
    print(f"📧 Enviando prueba a {destinatario}...")
    asunto, texto, html = generar_email_para_cliente("David", "seguridad")
    asunto = f"[PRUEBA] {asunto}"
    
    try:
        msg_id = enviar_email(service, destinatario, asunto, texto, html)
        print(f"  ✅ Enviado! ID: {msg_id}")
        print(f"  📬 Revisa formulasia76@gmail.com en 1-2 min")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def enviar_campana(sector_filtro=None, limite=20):
    """Envía la campaña a clientes pendientes en DB."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    query = """SELECT id, nombre, email, sector_comprador FROM clientes 
               WHERE email IS NOT NULL AND email != '' AND email_enviado = 0"""
    params = []
    
    if sector_filtro:
        query += " AND sector_comprador = ?"
        params.append(sector_filtro)
    
    query += " ORDER BY id LIMIT ?"
    params.append(limite)
    
    c.execute(query, params)
    pendientes = c.fetchall()
    
    if not pendientes:
        print("❌ No hay clientes pendientes con email en DB")
        conn.close()
        return
    
    service = get_gmail_service()
    
    print(f"\n📧 Enviando campaña a {len(pendientes)} clientes...\n")
    
    enviados = 0
    errores = 0
    for eid, nombre, email, sector in pendientes:
        print(f"  [{enviados+errores+1}/{len(pendientes)}] {nombre[:35]:35s} → {email[:30]:30s}", end=" ", flush=True)
        
        if not email or '@' not in email:
            print("❌ email inválido")
            errores += 1
            continue
        
        try:
            asunto, texto, html = generar_email_para_cliente(nombre, sector)
            msg_id = enviar_email(service, email, asunto, texto, html)
            c.execute("UPDATE clientes SET email_enviado=1, notas=? WHERE id=?", 
                      (f"Enviado {datetime.now().strftime('%Y-%m-%d %H:%M')}", eid))
            conn.commit()
            enviados += 1
            print(f"✅")
        except Exception as e:
            error_str = str(e)[:60]
            # Si es rate limit, paramos
            if "rate" in str(e).lower() or "quota" in str(e).lower() or "429" in str(e):
                print(f"❌ RATE LIMIT - parando")
                break
            c.execute("UPDATE clientes SET notas=? WHERE id=?", 
                      (f"Error: {error_str}", eid))
            conn.commit()
            errores += 1
            print(f"❌ {error_str}")
    
    conn.close()
    print(f"\n✅ Enviados: {enviados} | Errores: {errores}")

def mostrar_resumen():
    """Muestra estado actual de clientes."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    print("\n📊 RESUMEN CLIENTES NEO CAMPAIGNS")
    print("=" * 50)
    
    c.execute("""SELECT sector_comprador, COUNT(*), 
                  SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END),
                  SUM(email_enviado)
                 FROM clientes GROUP BY sector_comprador""")
    
    total = 0
    total_email = 0
    total_enviados = 0
    for s, cnt, con_email, enviados in c.fetchall():
        total += cnt
        total_email += (con_email or 0)
        total_enviados += (enviados or 0)
        print(f"  {s:15s} {cnt:3d} empresas | {con_email or 0:2d} con email | {enviados or 0} enviados")
    
    print(f"  {'TOTAL':15s} {total:3d} empresas | {total_email:2d} con email | {total_enviados} enviados")
    print(f"\n  Pendientes con email: {total_email - total_enviados}")
    conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NEO Campaigns Lanzador")
    parser.add_argument("--test", help="Email de prueba (ej: formulasia76@gmail.com)")
    parser.add_argument("--sector", help="Filtrar por sector (seguridad, tpv, software)")
    parser.add_argument("--limite", type=int, default=20, help="Máx emails a enviar")
    parser.add_argument("--resumen", action="store_true", help="Mostrar resumen")
    
    args = parser.parse_args()
    
    if args.resumen:
        mostrar_resumen()
    elif args.test:
        enviar_prueba()
    else:
        enviar_campana(args.sector, args.limite)
