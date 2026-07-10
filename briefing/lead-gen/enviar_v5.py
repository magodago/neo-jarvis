#!/usr/bin/env python3
"""
NEO EMAIL v5 — Envío con límite diario de 100 emails (Gmail API).
Respeta el límite, lleva contabilidad diaria, reintenta 429 con backoff.
"""
import json, os, sys, base64, time, sqlite3, csv, re
from datetime import datetime, timezone

BASE = "/home/dorti/neo-jarvis/briefing/lead-gen"
DATA_DIR = os.path.join(BASE, "data")
LOGS_DIR = os.path.join(BASE, "logs")
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]
LANDING = "https://magodago.github.io/neo-jarvis/landing/"

# ── LÍMITE DIARIO ──
DAILY_LIMIT = 100
DELAY_BETWEEN = 3  # segundos entre emails

# ── Sectores EXCLUIDOS ──
EXCLUIR = ["abogado", "bufete", "legal", "extranjeria"]

# ── BLACKLIST ──
BLACKLIST = [
    'carmen.blancopico@gmail.com',
]

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
    return any(e in sector.lower() for e in EXCLUIR)


def contar_enviados_hoy():
    """Cuenta emails enviados hoy desde la DB."""
    conn = sqlite3.connect(os.path.join(DATA_DIR, "leads.db"))
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM leads WHERE fecha_envio LIKE ?", (today + "%",))
    count = c.fetchone()[0]
    conn.close()
    return count


def get_pendientes(limit):
    """Obtiene hasta `limit` leads pendientes (no enviados, no excluidos, no blacklist)."""
    conn = sqlite3.connect(os.path.join(DATA_DIR, "leads.db"))
    c = conn.cursor()
    c.execute("""SELECT nombre, email, ciudad, sector FROM leads 
                 WHERE email IS NOT NULL AND email != '' 
                 AND (email_enviado IS NULL OR email_enviado=0)""")
    todos = c.fetchall()
    conn.close()

    sp = os.path.join(LOGS_DIR, "sent.csv")
    sent = set()
    if os.path.exists(sp):
        with open(sp) as f:
            for row in csv.DictReader(f):
                sent.add(row.get("email_destino", ""))

    pendientes = []
    excluidos = 0
    blacklisted = 0
    for r in todos:
        if len(pendientes) >= limit:
            break
        if es_sector_excluido(r[3]):
            excluidos += 1
            continue
        if r[1] in sent:
            continue
        if r[1].lower() in [b.lower() for b in BLACKLIST]:
            blacklisted += 1
            continue
        pendientes.append(r)

    return pendientes


def generar_email(lead):
    nombre, _, ciudad, sector = lead
    sector_limpio = sector.rstrip("s") if sector else "negocio"
    body = EMAIL_TEXTO.replace("[CIUDAD]", ciudad or "tu zona").replace("[SECTOR]", sector_limpio or "negocio")
    subj = f"{nombre[:35]}, una idea para tu {sector_limpio or 'negocio'} en {ciudad or 'tu zona'}"
    return subj, body


def parse_retry_after(err_str):
    m = re.search(r"Retry after (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)", err_str)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return None


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Guardar token refrescado a disco
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()

    # ── Calcular cuántos podemos enviar hoy ──
    enviados_hoy = contar_enviados_hoy()
    disponibles = max(0, DAILY_LIMIT - enviados_hoy)

    if disponibles <= 0:
        return

    # ── Intentos con reintentos por 429 ──
    max_intentos = 10
    total_ok = 0

    for intento in range(1, max_intentos + 1):
        # Recalcular disponibles por si se enviaron entre reintentos
        enviados_hoy = contar_enviados_hoy()
        disponibles_hoy = max(0, DAILY_LIMIT - enviados_hoy)
        if disponibles_hoy <= 0:
            break

        pendientes = get_pendientes(disponibles_hoy)
        if not pendientes:
            break

        sent_log = []
        ok = 0

        for i, lead in enumerate(pendientes):
            nombre, email, ciudad, sector = lead
            subj, body = generar_email(lead)

            body_html = body.replace("\n", "<br>")
            html = HTML_TEMPLATE.replace("[CUERPO_HTML]", body_html).replace("[LANDING]", LANDING)

            msg = __import__("email.mime.multipart", fromlist=["MIMEMultipart"]).MIMEMultipart("alternative")
            msg["Subject"] = subj
            msg["From"] = "dortizs76@gmail.com"
            msg["To"] = email
            msg["Reply-To"] = "dortizs76@gmail.com"
            msg.attach(__import__("email.mime.text", fromlist=["MIMEText"]).MIMEText(body, "plain", "utf-8"))
            msg.attach(__import__("email.mime.text", fromlist=["MIMEText"]).MIMEText(html, "html", "utf-8"))

            try:
                raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
                sent_log.append({"email_destino": email, "nombre": nombre, "asunto": subj,
                                 "message_id": result["id"], "status": "sent"})
                ok += 1
                time.sleep(DELAY_BETWEEN)
            except Exception as e:
                err_str = str(e)
                sent_log.append({"email_destino": email, "nombre": nombre, "asunto": subj,
                                 "message_id": "", "status": f"error: {err_str}"})
                if "429" in err_str or "rate" in err_str.lower():
                    retry_ts = parse_retry_after(err_str)
                    if retry_ts:
                        now = datetime.now(timezone.utc)
                        wait = (retry_ts - now).total_seconds() + 5
                        wait = max(wait, 10)
                        if wait > 7200:
                            break
                        time.sleep(min(wait, 7200))
                    else:
                        time.sleep(10)
                else:
                    time.sleep(10)
                break  # stop this batch, will retry next iteration

        total_ok += ok

        # Guardar log
        if sent_log:
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

    # ── Resumen final ──
    conn = sqlite3.connect(os.path.join(DATA_DIR, "leads.db"))
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM leads')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM leads WHERE email_enviado=1')
    enviados_total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != "" AND (email_enviado IS NULL OR email_enviado=0)')
    pendientes = c.fetchone()[0]
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM leads WHERE fecha_envio LIKE ?", (today + "%",))
    enviados_hoy_final = c.fetchone()[0]
    conn.close()

    print(f"\n{'='*55}")
    print(f"  📊 RESUMEN FINAL")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")
    print(f"  Enviados esta ejecución: {total_ok}")
    print(f"  Enviados hoy:            {enviados_hoy_final}/{DAILY_LIMIT}")
    print(f"  DB enviados total:       {enviados_total}")
    print(f"  DB pendientes:           {pendientes}")
    print(f"  DB total leads:          {total}")


if __name__ == "__main__":
    main()
