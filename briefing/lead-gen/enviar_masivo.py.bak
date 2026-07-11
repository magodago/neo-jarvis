#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envio masivo NEO: DB → personalizar → enviar en un solo comando"""
import json, csv, os, sys, base64, time, urllib.request
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "data")
OUTPUT_DIR = os.path.join(BASE, "output")
LOGS_DIR = os.path.join(BASE, "logs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

TOKEN_PATH = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"]
LANDING = "https://magodago.github.io/neo-jarvis/landing/"

# DeepSeek
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"

NEGOCIO = {
    "restaurantes": "restaurante", "clinicas": "centro medico",
    "abogados": "despacho de abogados", "talleres": "taller mecanico",
    "peluquerias": "peluqueria",
}

EMAIL_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a">
<tr><td align="center" style="padding:40px 20px">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">
<tr><td style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0033 100%);padding:30px 30px 20px;border-radius:12px 12px 0 0;text-align:center">
<div style="font-size:32px;font-weight:bold;color:#ff00ff;letter-spacing:3px">NEO <span style="color:#ffffff">LABS</span></div>
<div style="color:#666;font-size:12px">SOLUCIONES DIGITALES PROFESIONALES</div></td></tr>
<tr><td style="background-color:#111;padding:30px;color:#e0e0e0;font-size:15px;line-height:1.6">
{BODY_HTML}</td></tr>
<tr><td style="background-color:#111;padding:0 30px 20px">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td style="background:#1a1a2e;border-radius:8px;padding:15px;border-left:3px solid #ff00ff">
<div style="color:#ff00ff;font-size:12px;font-weight:bold">Basica - 299 EUR</div>
<div style="color:#aaa;font-size:12px">Web responsive + SEO basico + formulario + hosting 1 ano</div></td></tr>
<tr><td style="height:6px"></td></tr>
<tr><td style="background:#1a1a2e;border-radius:8px;padding:15px;border-left:3px solid #00ffff">
<div style="color:#00ffff;font-size:12px;font-weight:bold">Premium - 599 EUR (mas popular)</div>
<div style="color:#aaa;font-size:12px">Diseno premium + SEO completo + blog + panel</div></td></tr>
<tr><td style="height:6px"></td></tr>
<tr><td style="background:#1a1a2e;border-radius:8px;padding:15px;border-left:3px solid #ff8800">
<div style="color:#ff8800;font-size:12px;font-weight:bold">Premium+Curso - 699 EUR</div>
<div style="color:#aaa;font-size:12px">Todo + curso IA Operativa (valorado en 297 EUR)</div></td></tr>
</table></td></tr>
<tr><td style="background-color:#111;padding:20px 30px 30px;text-align:center">
<a href="{LANDING}" style="display:inline-block;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;padding:14px 40px;border-radius:8px;font-weight:bold;font-size:15px">VER EJEMPLOS REALES</a></td></tr>
<tr><td style="background:#080808;padding:20px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:12px">
<div>NEO Labs - Soluciones Digitales</div>
<div><a href="{LANDING}" style="color:#ff00ff;text-decoration:none">neolabs.es</a></div>
<div style="margin-top:6px;color:#444">Si no quieres recibir mas emails, responde "baja"</div></td></tr>
</table></td></tr></table></body></html>"""


def export_leads_pendientes():
    """Exporta leads de DB a CSV"""
    import sqlite3
    db = os.path.join(DATA_DIR, "leads.db")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    # Obtener leads con email, no enviados
    c.execute("""SELECT nombre, email, ciudad, sector FROM leads 
                 WHERE email IS NOT NULL AND email != '' AND email_enviado=0
                 ORDER BY sector, ciudad""")
    rows = c.fetchall()
    conn.close()
    
    csv_path = os.path.join(DATA_DIR, "leads.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nombre", "email", "ciudad", "sector"])
        w.writerows(rows)
    
    print(f"✅ Exportados {len(rows)} leads a {csv_path}")
    return rows


def generar_email(lead):
    """Genera email personalizado via DeepSeek"""
    nombre = lead[0]
    ciudad = lead[2] if lead[2] else "tu zona"
    sector = lead[3]
    negocio = NEGOCIO.get(sector, "negocio")
    
    prompt = (
        f"Escribe un email de ventas REAL para {nombre}, un {negocio} en {ciudad}.\n"
        "Formato:\n"
        "ASUNTO: [asunto]\n"
        "CUERPO: [texto]\n\n"
        "REGLAS ESTRICTAS:\n"
        "- NO uses ** ni * ni markdown. Solo texto plano.\n"
        "- Suena a persona real, no a plantilla. Nada de 'listo para crecer' ni frases hechas.\n"
        f"- Menciona el negocio por su nombre: {nombre}\n"
        "- 3 planes: BASICA 299EUR, PREMIUM 599EUR (el mas popular), PREMIUM+CURSO 699EUR\n"
        f"- Link ejemplos: {LANDING}\n"
        "- Pide respuesta, no llamada. 'Respondeme a este email y te paso ejemplos'\n"
        "- Maximo 80 palabras en el cuerpo\n"
        "- Firma: -- David | NEO Labs | neolabs.es\n"
        "- Espanol correcto sin faltas de ortografia"
    )
    
    try:
        payload = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.5,
        }).encode()
        req = urllib.request.Request(
            API_URL, data=payload,
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        content = result["choices"][0]["message"]["content"]
        
        if "ASUNTO:" in content and "CUERPO:" in content:
            parts = content.split("CUERPO:", 1)
            subj = parts[0].replace("ASUNTO:", "").strip()
            body = parts[1].strip()
        else:
            subj = f"{nombre} - Tu web profesional desde 299EUR"
            body = content
        return subj, body
    except Exception as e:
        print(f"  API err {nombre}: {e}")
        return fallback(nombre, ciudad, negocio, sector)


def fallback(nombre, ciudad, negocio, sector):
    subj = f"{nombre}, tu web profesional desde 299EUR"
    body = (
        f"Hola, soy David de NEO Labs.\n\n"
        f"Hemos disenado webs para {negocio}s como {nombre} en {ciudad} "
        f"y queremos ofrecerte lo mismo.\n\n"
        f"Nuestros planes:\n"
        f"* BASICA 299EUR - Web responsive + SEO + formulario + hosting\n"
        f"* PREMIUM 599EUR - Diseno premium + SEO completo + blog + panel (el mas popular)\n"
        f"* PREMIUM+CURSO 699EUR - Todo + curso IA Operativa (valor 297EUR)\n\n"
        f"Ver ejemplos: {LANDING}\n\n"
        f"10 minutos sin compromiso para ensenarte lo que podemos hacer.\n\n"
        f"Saludos,\n-- David | Equipo NEO Labs\nneolabs.es"
    )
    return subj, body


def personalizar(leads):
    """Personaliza todos los leads y guarda CSV"""
    emails = []
    total = len(leads)
    for i, lead in enumerate(leads):
        nombre = lead[0]
        print(f"  [{i+1}/{total}] {nombre}...", end=" ", flush=True)
        subj, body = generar_email(lead)
        emails.append({
            "nombre": nombre,
            "email_destino": lead[1],
            "asunto": subj,
            "cuerpo": body,
            "sector": lead[3],
            "ciudad": lead[2],
        })
        print("OK")
        time.sleep(0.3)  # evitar rate limit DeepSeek
    
    csv_out = os.path.join(OUTPUT_DIR, "emails.csv")
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre", "email_destino", "asunto", "cuerpo", "sector", "ciudad"])
        w.writeheader()
        w.writerows(emails)
    print(f"\n✅ {len(emails)} emails personalizados en {csv_out}")
    return emails


def enviar_todos():
    """Envía todos los emails desde output/emails.csv"""
    service = None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        print(f"📧 Autenticado como: {profile['emailAddress']}")
    except Exception as e:
        print(f"❌ Error autenticando Gmail: {e}")
        return
    
    csv_path = os.path.join(OUTPUT_DIR, "emails.csv")
    if not os.path.exists(csv_path):
        print("❌ No hay emails.csv. Ejecuta personalizar primero.")
        return
    
    with open(csv_path, "r", encoding="utf-8") as f:
        emails = list(csv.DictReader(f))
    
    sent_path = os.path.join(LOGS_DIR, "sent.csv")
    sent_emails = set()
    if os.path.exists(sent_path):
        with open(sent_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sent_emails.add(row.get("email_destino", ""))
    
    pendientes = [e for e in emails if e["email_destino"] not in sent_emails]
    
    print(f"\nTotal en CSV: {len(emails)}")
    print(f"Ya enviados: {len(emails) - len(pendientes)}")
    print(f"Pendientes: {len(pendientes)}")
    
    if not pendientes:
        print("✅ Todos enviados ya!")
        return
    
    print("\n🚀 Enviando...")
    sent_log = []
    
    for i, email in enumerate(pendientes):
        to = email["email_destino"]
        nombre = email["nombre"]
        subject = email["asunto"]
        body = email["cuerpo"]
        
        try:
            body_html = body.replace("\n", "<br>")
            html_content = EMAIL_HTML.format(BODY_HTML=body_html, LANDING=LANDING)
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = "dortizs76@gmail.com"
            msg["To"] = to
            msg["Reply-To"] = "dortizs76@gmail.com"
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
            msg_id = result["id"]
            
            sent_log.append({"email_destino": to, "nombre": nombre, "asunto": subject, "message_id": msg_id, "status": "sent"})
            print(f"  [{i+1}/{len(pendientes)}] ✅ {nombre} <{to}>")
        except Exception as e:
            print(f"  [{i+1}/{len(pendientes)}] ❌ {nombre} <{to}>: {e}")
            sent_log.append({"email_destino": to, "nombre": nombre, "asunto": subject, "message_id": "", "status": f"error: {e}"})
        
        time.sleep(1)  # evitar rate limits Gmail
    
    with open(sent_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email_destino", "nombre", "asunto", "message_id", "status"])
        if os.path.getsize(sent_path) == 0:
            w.writeheader()
        w.writerows(sent_log)
    
    ok = sum(1 for s in sent_log if s["status"] == "sent")
    fail = sum(1 for s in sent_log if s["status"] != "sent")
    print(f"\n📊 RESULTADO: {ok} enviados, {fail} fallos")
    
    # Actualizar DB
    import sqlite3
    db = os.path.join(DATA_DIR, "leads.db")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for s in sent_log:
        if s["status"] == "sent":
            c.execute("UPDATE leads SET email_enviado=1, estado='enviado', fecha_envio=? WHERE email=?", 
                     (now, s["email_destino"]))
    conn.commit()
    conn.close()
    print(f"✅ DB actualizada")


if __name__ == "__main__":
    print("=" * 60)
    print("  NEO MASSIVE EMAIL ENGINE")
    print("=" * 60)
    
    # 1. Exportar leads pendientes de DB
    leads = export_leads_pendientes()
    if not leads:
        print("❌ No hay leads pendientes con email")
        sys.exit(1)
    
    # 2. Personalizar
    print(f"\n🎯 Personalizando {len(leads)} emails con DeepSeek...")
    personalizar(leads)
    
    # 3. Enviar
    print(f"\n📤 Enviando {len(leads)} emails...")
    enviar_todos()
    
    print("\n✨ COMPLETADO")
