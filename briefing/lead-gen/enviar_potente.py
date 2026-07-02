#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO EMAIL POTENTE v2 — Envío masivo con tono humano real para pymes.
Personaliza con DeepSeek, fallback de alta calidad.
"""
import json, os, sys, base64, time, urllib.request, sqlite3, csv
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Config ──
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
LOGS_DIR = os.path.join(BASE, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Gmail
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.modify"]

# DeepSeek
DS_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DS_URL = "https://api.deepseek.com/v1/chat/completions"

# Landing
LANDING = "https://magodago.github.io/neo-jarvis/landing/"

# ── Mapeo sectores ──
NEGOCIO = {
    "restaurantes": "restaurante", "abogados": "bufete",
    "clinicas": "clínica", "clínicas dentales": "clínica dental",
    "talleres": "taller", "peluquerias": "peluquería",
    "inmobiliarias": "inmobiliaria", "odontólogos": "odontólogo",
    "centros": "centro de estética", "estética": "centro de estética",
    "peluquerías": "peluquería", "talleres mecánicos": "taller mecánico",
    "clínicas estética": "centro de estética",
}

# ── Plantilla humana (fallback) ──
FALLBACK = """Hola,

Soy David, de NEO Labs. Trabajo con pequeños negocios como el tuyo en CIUDAD.

Os podemos hacer una web profesional (con SEO, formulario, blog si queréis) desde 299€. Y si contratáis cualquier pack, os regalamos nuestro mini-curso IA Operativa (valorado en 297€).

Los packs:
▸ Básica 299€ — Web responsive + SEO + formulario + hosting 1 año
▸ Premium 599€ — Diseño premium + SEO completo + blog + panel (el más popular)
▸ Premium+Curso 699€ — Todo + curso IA Operativa incluido

He hecho proyectos para otros SECTOR de la zona y funcionan. Si os interesa, responded a este mail y os paso ejemplos.

Un saludo,
David | NEO Labs
neolabs.es"""

# ── Prompt DeepSeek ──
PROMPT_DS = """Escribe un email corto de venta para NOMBRE, dueño de un SECTOR en CIUDAD.

Formato:
ASUNTO: [asunto, muy corto, sin el nombre del negocio]
CUERPO: [2-3 líneas, tono natural, como de persona real escribiendo a otra]

REGLAS:
- Nada de markdown ni asteriscos. Solo texto plano.
- Suena a persona real, no a vendedor ni a chatbot.
- Menciona el negocio de pasada.
- NO pongas precios en ningún lado.
- Termina con: "Si te va, responde y te paso ejemplos. -- David | NEO Labs"
- Español real, con tildes.
- Máximo 40 palabras el cuerpo."""

# ── HTML visual ──
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
CUERPO_HTML</td></tr>
<tr><td style="background-color:#111;padding:20px 30px 30px;text-align:center">
<a href="LANDING" style="display:inline-block;background:linear-gradient(135deg,#ff00ff,#cc00cc);color:#fff;text-decoration:none;padding:12px 32px;border-radius:8px;font-weight:bold;font-size:14px">VER EJEMPLOS</a></td></tr>
<tr><td style="background:#080808;padding:16px 30px;border-radius:0 0 12px 12px;text-align:center;color:#555;font-size:11px">
<div>NEO Labs &mdash; Soluciones Digitales</div>
<div><a href="LANDING" style="color:#ff00ff;text-decoration:none">neolabs.es</a></div>
<div style="margin-top:6px;color:#444">Si no quieres recibir m&aacute;s emails, responde &quot;baja&quot;</div></td></tr>
</table></td></tr></table></body></html>"""

# ── Funciones ──

def personalizar(lead):
    """Intenta DeepSeek. Si falla → None."""
    nombre, _, ciudad, sector = lead[0], lead[1], lead[2], lead[3]
    negocio = NEGOCIO.get(sector, sector)
    if not DS_KEY or len(DS_KEY) < 10:
        return None
    
    prompt = PROMPT_DS.replace("NOMBRE", nombre).replace("SECTOR", negocio).replace("CIUDAD", ciudad)
    
    for _ in range(2):
        try:
            payload = json.dumps({
                "model": "deepseek-v4-flash",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 250, "temperature": 0.6
            }).encode()
            req = urllib.request.Request(DS_URL, data=payload,
                headers={"Authorization": f"Bearer {DS_KEY}", "Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=20)
            content = json.loads(resp.read())["choices"][0]["message"]["content"]
            
            if "ASUNTO:" in content and "CUERPO:" in content:
                parts = content.split("CUERPO:", 1)
                subj = parts[0].replace("ASUNTO:", "").strip().strip('"').strip("'")
                body = parts[1].strip()
                if subj and body:
                    return subj, body
        except:
            time.sleep(1)
    return None


def fallback(lead):
    """Fallback con tono humano"""
    nombre, ciudad, sector = lead[0], lead[2] or "tu zona", lead[3] or ""
    negocio = NEGOCIO.get(sector, sector)
    n_limpio = nombre.replace("|", "-").strip()[:35]
    subj = f"{n_limpio}, una idea"
    body = FALLBACK.replace("CIUDAD", ciudad).replace("SECTOR", negocio)
    return subj, body


def generar_email(lead):
    """IA si puede → fallback si no"""
    ia = personalizar(lead)
    return ia if ia else fallback(lead)


def get_pendientes():
    """Leads con email, no enviados, no abogados, no en sent.log"""
    conn = sqlite3.connect(os.path.join(DATA_DIR, "leads.db"))
    c = conn.cursor()
    c.execute("""SELECT nombre, email, ciudad, sector FROM leads 
                 WHERE email IS NOT NULL AND email != '' 
                 AND (email_enviado IS NULL OR email_enviado=0)
                 AND sector != 'abogados'""")
    rows = c.fetchall()
    conn.close()
    
    # Filtrar ya enviados
    sent = set()
    sp = os.path.join(LOGS_DIR, "sent.csv")
    if os.path.exists(sp):
        with open(sp) as f:
            for row in csv.DictReader(f):
                sent.add(row.get("email_destino", ""))
    
    return [r for r in rows if r[1] not in sent]


def main():
    print("=" * 55)
    print("  NEO EMAIL POTENTE v2")
    print("  humano · cercano · para pymes")
    print("=" * 55)
    
    # Auth Gmail
    print("\n📧 Gmail...", end=" ", flush=True)
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    
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
    
    # Pendientes
    pendientes = get_pendientes()
    print(f"\n📊 Pendientes: {len(pendientes)}")
    if not pendientes:
        print("   ✅ Todos enviados!")
        return
    
    print(f"\n🚀 Enviando {len(pendientes)} emails...\n")
    
    sent_log = []
    ok = 0
    fail = 0
    
    for i, lead in enumerate(pendientes):
        nombre, email, ciudad, sector = lead
        
        # Generar
        subj, body = generar_email(lead)
        
        # Enviar
        try:
            body_html = body.replace("\n", "<br>")
            html = HTML_TEMPLATE.replace("CUERPO_HTML", body_html).replace("LANDING", LANDING)
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subj
            msg["From"] = "dortizs76@gmail.com"
            msg["To"] = email
            msg["Reply-To"] = "dortizs76@gmail.com"
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(html, "html", "utf-8"))
            
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
            
            sent_log.append({"email_destino": email, "nombre": nombre, "asunto": subj,
                           "message_id": result["id"], "status": "sent"})
            ok += 1
            print(f"  [{i+1}/{len(pendientes)}] ✅ {nombre[:28]:28s} <{email[:22]:22s}>")
        except Exception as e:
            sent_log.append({"email_destino": email, "nombre": nombre, "asunto": subj,
                           "message_id": "", "status": f"error: {e}"})
            fail += 1
            print(f"  [{i+1}/{len(pendientes)}] ❌ {nombre[:28]:28s}: {e}")
        
        time.sleep(1)
    
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
    
    print(f"\n{'='*55}")
    print(f"📊 RESULTADO: {ok} enviados | {fail} fallos")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
