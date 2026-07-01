#!/usr/bin/env python3
"""Pipeline unificado de captacion NEO con tracking SQLite + email killer"""
import os, csv, sys, json, base64, datetime, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText

LEAD_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(LEAD_DIR, "data")
LOGS_DIR = os.path.join(LEAD_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Tracking
sys.path.insert(0, LEAD_DIR)
import tracker

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")

# Plantilla de email KILLER
PLANTILLA = """Hola {nombre},

Soy David de NEO Labs ({link_equipo}) — creamos webs profesionales para {negocio}s como el tuyo.

Te escribo porque veo que {nombre} necesita mejorar su presencia online. Y tengo algo que te va a interesar:

🎁 REGALO: He preparado una guia GRATIS ({link_guia}) donde te explico las 5 claves para que un negocio local como el tuyo triplique sus clientes con una web bien hecha. Sin tonterias tecnicas.

Ademas, podemos hacerte una web profesional en 48h con estos planes:

--- PLANES NEO WEBS ---

> BASICA · 299€ — Web responsive, SEO local, formulario de contacto, hosting 1 año
> PREMIUM · 599€ (EL MAS ELEGIDO) — Diseno premium, SEO completo, blog, panel admin, WhatsApp integrado
> PREMIUM + CURSO · 699€ — Todo lo anterior + curso IA Operativa (valorado en 297€)

✅ Sin cuotas mensuales
✅ Hosting incluido 1 año
✅ Diseno adaptado a tu sector
✅ Posicionamiento en Google Maps

Mira ejemplos de trabajos recientes: {link_ejemplos}

¿Te interesa? Respondeme a este email y te paso ejemplos de {negocio}s como el tuyo que ya tienen su web con nosotros. Sin compromiso.

Un saludo,
David Ortiz
NEO Labs
{link_web}
📱 {telefono_contacto} (WhatsApp)"""

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build('gmail', 'v1', credentials=creds)

def generar_email(lead):
    nombre = lead.get("nombre", "tu negocio")
    sector = lead.get("sector", "negocio")
    ciudad = lead.get("ciudad", "tu zona")
    
    negocio_tipo = {"restaurantes":"restaurante","clinicas":"centro médico",
        "abogados":"despacho de abogados","talleres":"taller","peluquerias":"peluquería"
    }.get(sector, "negocio")
    
    body = PLANTILLA.format(
        nombre=nombre.split(",")[0].split(" -")[0].strip(),  # Nombre corto
        negocio=negocio_tipo,
        link_equipo="https://magodago.github.io/neo-jarvis/landing/",
        link_guia="https://magodago.github.io/neo-jarvis/landing/#guias",
        link_ejemplos="https://magodago.github.io/neo-jarvis/landing/#ejemplos",
        link_web="https://neolabs.es",
        telefono_contacto="658 237 988",
        ciudad=ciudad,
    )
    subject = f"{nombre} — web profesional desde 299€ (con regalo incluido)"
    return subject, body

def enviar_email(service, to, subject, body):
    msg_text = body.replace("━━", "==")  # Gmail soporta =
    msg = MIMEText(msg_text, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = "David - NEO Labs <dortizs76@gmail.com>"
    msg["To"] = to
    msg["Reply-To"] = "dortizs76@gmail.com"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return result["id"]

def importar_leads_a_db():
    csv_path = os.path.join(DATA_DIR, "leads.csv")
    if os.path.exists(csv_path):
        tracker.import_csv(csv_path)
        print("Leads importados a tracking DB")

def enviar_pendientes(service):
    conn = tracker.get_db()
    cur = conn.cursor()
    pendientes = cur.execute("""
        SELECT nombre, email, sector, ciudad FROM leads 
        WHERE email != '' AND email_enviado = 0
        ORDER BY sector, ciudad
    """).fetchall()
    conn.close()
    
    if not pendientes:
        print("No hay pendientes")
        return 0
    
    enviados = 0
    for row in pendientes:
        lead = dict(row)
        try:
            subject, body = generar_email(lead)
            msg_id = enviar_email(service, lead["email"], subject, body)
            tracker.marcar_enviado(lead["email"], subject, msg_id)
            print(f"  ✅ {lead['nombre'][:30]:30s} → {lead['email']}")
            enviados += 1
            time.sleep(0.5)  # Rate limit
        except Exception as e:
            print(f"  ❌ {lead['nombre'][:30]:30s} → {e}")
    
    return enviados

def procesar_bounces(service):
    """Marca como rebotados los delivery failures"""
    yesterday = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=48)).strftime("%Y/%m/%d")
    q = f"after:{yesterday} from:mailer-daemon@googlemail.com"
    results = service.users().messages().list(userId='me', q=q, maxResults=10).execute()
    for msg in results.get("messages", []):
        d = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        snippet = d.get("snippet", "")
        import re
        # Extraer email que rebotó del snippet
        m = re.search(r'wasn\'?t delivered to ([\w.@-]+)', snippet)
        if m:
            email = m.group(1)
            tracker.marcar_rebote(email)
            print(f"  📬 Rebote: {email}")

def main():
    print("=== PIPELINE NEO ===")
    importar_leads_a_db()
    
    # Mostrar estado actual
    stats = tracker.get_stats()
    print(f"\nEstado: {stats['enviados']} enviados | {stats['rebotados']} rebotados | {stats['respondidos']} respondidos | {stats['pendientes']} pendientes")
    print()
    
    if stats["pendientes"] > 0:
        service = get_service()
        
        # Procesar bounces primero
        print("Procesando bounces...")
        procesar_bounces(service)
        
        # Enviar pendientes
        print(f"\nEnviando {stats['pendientes']} emails pendientes...")
        enviados = enviar_pendientes(service)
        
        # Mostrar resumen final
        final = tracker.get_stats()
        resumen = tracker.get_resumen()
        print(f"\n✅ Completado: {enviados} enviados hoy")
        print(f"Total acumulado: {final['enviados']} enviados | {final['rebotados']} rebotados | {final['respondidos']} respondidos")
        for r in resumen:
            print(f"  {r['sector']}: {r['enviados']} enviados / {r['rebotes']} rebotes")
    else:
        print("Todos los leads ya procesados. Esperando nuevos leads del scraper.")

if __name__ == "__main__":
    main()
