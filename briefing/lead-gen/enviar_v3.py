#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO EMAIL v3 — Con packs + filtro abogados
"""
import json, os, sys, base64, time, urllib.request, sqlite3, csv
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
LOGS_DIR = os.path.join(BASE, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]
LANDING = "https://magodago.github.io/neo-jarvis/landing/"

# ── Sectores EXCLUIDOS ──
EXCLUIR = ["abogado", "bufete", "legal", "extranjeria"]

# ── Plantilla con PACKS incluidos ──
EMAIL_TEXTO = """Hola,

Soy David, de NEO Labs. Trabajo con pequeños negocios como el tuyo en [CIUDAD].

Os podemos hacer una web profesional desde 299€ (con SEO, formulario, blog si queréis). Y si contratáis cualquier pack, os regalamos nuestro mini-curso IA Operativa, valorado en 297€.

Los packs:
▸ Básica 299€ — Web responsive + SEO + formulario + hosting 1 año
▸ Premium 599€ — Diseño premium + SEO completo + blog + panel (el más popular)
▸ Premium+Curso 699€ — Todo + curso IA Operativa incluido

He hecho proyectos para negocios como el tuyo en [CIUDAD] y funcionan. Si os interesa, responded a este mail y os paso ejemplos concretos.

Un saludo,
David
NEO Labs
neolabs.es"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">
<tr><td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0033 100%);padding:30px 30px 20px;border-radius:12px 12px 0 0;text-align:center">
<div style="font-size:28px;font-weight:bold;color:#ff00ff;letter-spacing:3px">NEO <span style="color:#ffffff">LABS</span></div>
<div style="color:#666;font-size:11px">WEBS PARA NEGOCIOS LOCALES</div></td></tr>
<tr><td style="background-color:#111;padding:30px;color:#e0e0e0;font-size:15px;line-height:1.7">
[CUERPO_HTML]
</td></tr>
<tr><td style="background-color:#111;padding:0 30px 30px;text-align:center">
<a href="[LANDING]" style="display:inline-block;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:bold;font-size:14px">VER EJEMPLOS</a></td></tr>
<tr><td style="background:#080808;padding:16px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:11px">
<div>NEO Labs &mdash; Soluciones Digitales</div>
<div><a href="[LANDING]" style="color:#ff00ff;text-decoration:none">neolabs.es</a></div>
<div style="margin-top:6px;color:#444">Si no quieres recibir m&aacute;s emails, responde &quot;baja&quot;</div></td></tr>
</table></td></tr></table></body></html>"""

def es_sector_excluido(sector):
    if not sector: return False
    s = sector.lower()
    return any(e in s for e in EXCLUIR)

def get_pendientes():
    conn = sqlite3.connect(os.path.join(DATA_DIR, "leads.db"))
    c = conn.cursor()
    c.execute("""SELECT nombre, email, ciudad, sector FROM leads 
                 WHERE email IS NOT NULL AND email != '' 
                 AND (email_enviado IS NULL OR email_enviado=0)""")
    todos = c.fetchall()
    conn.close()
    
    # Filtrar excluidos y ya enviados
    sent = set()
    sp = os.path.join(LOGS_DIR, "sent.csv")
    if os.path.exists(sp):
        with open(sp) as f:
            for row in csv.DictReader(f):
                sent.add(row.get("email_destino", ""))
    
    pendientes = []
    excluidos = 0
    for r in todos:
        if es_sector_excluido(r[3]):
            excluidos += 1
            continue
        if r[1] in sent:
            continue
        pendientes.append(r)
    
    print(f"   Pendientes: {len(pendientes)} | Excluidos: {excluidos}")
    return pendientes

def generar_email(lead):
    nombre, _, ciudad, sector = lead
    sector_limpio = sector.rstrip("s") if sector else "negocio"
    
    body = EMAIL_TEXTO.replace("[CIUDAD]", ciudad or "tu zona").replace("[SECTOR]", sector_limpio or "negocio")
    subj = f"{nombre[:35]}, una idea para tu {sector_limpio or 'negocio'} en {ciudad or 'tu zona'}"
    return subj, body

def main():
    print("=" * 55)
    print("  NEO EMAIL v3 — con packs + sin abogados")
    print("=" * 55)
    
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    
    print("\n📧 Gmail...", end=" ", flush=True)
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        print(f"✅ {profile['emailAddress']}")
    except Exception as e:
        print(f"❌ {e}")
        return
    
    pendientes = get_pendientes()
    if not pendientes:
        print("✅ Todos enviados!")
        return
    
    print(f"\n🚀 Enviando {len(pendientes)} emails (1 cada 3s para evitar rate limit)...\n")
    
    sent_log = []
    ok = 0
    
    for i, lead in enumerate(pendientes):
        nombre, email, ciudad, sector = lead
        subj, body = generar_email(lead)
        
        body_html = body.replace("\n", "<br>")
        html = HTML_TEMPLATE.replace("[CUERPO_HTML]", body_html).replace("[LANDING]", LANDING)
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subj
        msg["From"] = "dortizs76@gmail.com"
        msg["To"] = email
        msg["Reply-To"] = "dortizs76@gmail.com"
        msg.attach(MIMEText(body, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        try:
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
            sent_log.append({"email_destino": email, "nombre": nombre, "asunto": subj,
                           "message_id": result["id"], "status": "sent"})
            ok += 1
            print(f"  [{i+1}/{len(pendientes)}] ✅ {nombre[:28]:28s}")
        except Exception as e:
            sent_log.append({"email_destino": email, "nombre": nombre, "asunto": subj,
                           "message_id": "", "status": f"error: {e}"})
            print(f"  [{i+1}/{len(pendientes)}] ❌ {nombre[:28]:28s}: {str(e)[:60]}")
        
        time.sleep(3)  # 3 segundos entre emails para no rate-limitar
    
    # Guardar log
    sp = os.path.join(LOGS_DIR, "sent.csv")
    existe = os.path.exists(sp) and os.path.getsize(sp) > 0
    with open(sp, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email_destino", "nombre", "asunto", "message_id", "status"])
        if not existe:
            w.writeheader()
        w.writerows(sent_log)
    
    # Marcar DB
    enviados = [s["email_destino"] for s in sent_log if s["status"] == "sent"]
    if enviados:
        conn = sqlite3.connect(os.path.join(DATA_DIR, "leads.db"))
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for e in enviados:
            c.execute("UPDATE leads SET email_enviado=1, estado='enviado', fecha_envio=? WHERE email=?", (now, e))
        conn.commit()
        conn.close()
    
    print(f"\n📊 ENVIADOS: {ok} | PENDIENTES: {len(pendientes)-ok}")
    
    # Próximo slot disponible
    if ok < len(pendientes):
        print(f"\n⏳ Rate limit alcanzado. Los {len(pendientes)-ok} restantes se enviarán en la próxima ejecución.")

if __name__ == "__main__":
    main()
