#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR AUTÓNOMO NEO — Responde leads automáticamente
Revisa inbox cada ejecución, detecta respuestas humanas, responde, limpia rebotes.
Ejecutar vía cron cada 30-60 min.
ATENCIÓN: Guarda token refrescado automáticamente.
"""
import sys, os, json, base64, csv, time
from datetime import datetime, timezone

# Path al venv de Hermes para Google API
HERMES_VENV = '/home/dorti/jarvis/hermes/hermes-agent/.venv/lib/python3.12/site-packages'
if HERMES_VENV not in sys.path:
    sys.path.insert(0, HERMES_VENV)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText

BASE = '/home/dorti/neo-jarvis/briefing/lead-gen'
DATA_DIR = os.path.join(BASE, 'data')
LOGS_DIR = os.path.join(BASE, 'logs')
TOKEN_PATH = os.path.expanduser('~/.hermes/google_token.json')
DB_PATH = os.path.join(DATA_DIR, 'leads.db')
LANDING = 'https://magodago.github.io/neo-jarvis/landing/'

# Palabras clave que indican interés REAL
INTERES_KEYWORDS = [
    'quiero', 'me interesa', 'presupuesto', 'precio', 'cuanto cuesta',
    'información', 'informacion', 'saber más', 'saber mas', 'contactar',
    'llámame', 'llamame', 'escribeme', 'escríbeme', 'web', 'página web',
    'pagina web', 'si', 'adelante', 'cuentame', 'cuéntame', 'ver ejemplos',
    'ejemplos', 'demo', 'me gustaría', 'me gustaria', 'contratar',
    'estoy interesado', 'interesado', 'interesada', 'puedes mandarme',
    'mándame', 'mandame', 'presupuesto', 'orçamento', 'yes', 'hello',
    'hi', 'hola', 'buenas', 'vale', 'ok', 'de acuerdo', 'llamar',
]

# Palabras que indican NO interesado / spam
NO_INTERES_KEYWORDS = [
    'no me interesa', 'no gracias', 'no moleste', 'baja', 'unsubscribe',
    'remove', 'stop', 'cancelar', 'no llamar', 'no escribir',
]

# Palabras de auto-respuesta
AUTO_KEYWORDS = [
    'fuera de la oficina', 'out of office', 'vacaciones', 'ausente',
    'no estoy', 'automático', 'auto-respuesta', 'auto-reply',
    'delivery status', 'failure notice', 'mail delivery', 'undelivered',
    'bounce', 'no ha sido entregado', 'ha rebotado',
]

def get_service():
    """Obtiene servicio Gmail con refresh automático y guarda token refrescado"""
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    creds = Credentials.from_authorized_user_info(
        tok, 
        ['https://www.googleapis.com/auth/gmail.modify',
         'https://www.googleapis.com/auth/gmail.send',
         'https://www.googleapis.com/auth/gmail.readonly']
    )
    service = build('gmail', 'v1', credentials=creds)
    
    # Forzar refresh y guardar token actualizado
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        print('   🔄 Token refrescado y guardado')
    
    return service

def get_db():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def clasificar_respuesta(snippet, subject):
    """Clasifica una respuesta: auto, interesado, no_interesado, duda"""
    text = (snippet + ' ' + subject).lower()
    
    # Auto-respuesta?
    if any(w in text for w in AUTO_KEYWORDS):
        return 'auto'
    
    # No interesado?
    if any(w in text for w in NO_INTERES_KEYWORDS):
        return 'no_interesado'
    
    # Interesado?
    if any(w in text for w in INTERES_KEYWORDS):
        return 'interesado'
    
    # Por defecto: duda (humana pero no sabemos si interesada)
    return 'duda'

def responder_lead(service, to_email, nombre, tipo):
    """Responde automáticamente según el tipo de respuesta"""
    if tipo == 'interesado':
        body = (
            f"¡Hola {nombre}!\n\n"
            f"Gracias por tu interés. Aquí tienes unos ejemplos de nuestro trabajo:\n"
            f"{LANDING}\n\n"
            f"Resumiendo nuestros planes:\n"
            f"• BÁSICA 299€ — Web responsive + SEO básico + formulario + hosting\n"
            f"• PREMIUM 599€ — Diseño premium + SEO completo + blog + panel (el más popular)\n"
            f"• PREMIUM+CURSO 699€ — Todo lo anterior + curso IA Operativa (valor 297€)\n\n"
            f"¿Te parece bien si te llamo para contarte más? Dime un número y te llamo sin compromiso.\n\n"
            f"Un saludo,\n"
            f"David | NEO Labs\n"
            f"neolabs.es"
        )
        subject = f"Re: Tu web profesional — {nombre}"
    elif tipo == 'duda':
        body = (
            f"Hola {nombre},\n\n"
            f"Gracias por responderme. Cuéntame más sobre tu proyecto y te preparo "
            f"una propuesta personalizada sin compromiso.\n\n"
            f"Puedes ver ejemplos aquí: {LANDING}\n\n"
            f"Quedo a tu disposición,\n"
            f"David | NEO Labs\n"
            f"neolabs.es"
        )
        subject = f"Re: Propuesta NEO Labs — {nombre}"
    else:
        return None
    
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = 'dortizs76@gmail.com'
    msg['To'] = to_email
    msg['Reply-To'] = 'dortizs76@gmail.com'
    
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return result['id']

def monitor():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] 🚀 MONITOR NEO iniciado')
    
    service = get_service()
    profile = service.users().getProfile(userId='me').execute()
    print(f'   📧 Conectado como: {profile["emailAddress"]}')
    
    # 1. Buscar respuestas a emails NEO
    query = 'in:inbox ("NEO Labs" OR "neolabs.es" OR "299EUR") after:2026/06/30'
    results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
    msgs = results.get('messages', [])
    print(f'   📨 Posibles respuestas NEO: {len(msgs)}')
    
    # 2. Cargar leads enviados
    conn = get_db()
    cur = conn.cursor()
    
    for m in msgs:
        meta = service.users().messages().get(
            userId='me', id=m['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date', 'To', 'Message-ID', 'In-Reply-To', 'References']
        ).execute()
        headers = {h['name']: h['value'] for h in meta['payload']['headers']}
        
        frm = headers.get('From', '')
        frm_email = frm.split('<')[-1].strip('> ') if '<' in frm else frm
        
        # Saltar si lo envié yo
        if 'dortizs76' in frm_email:
            continue
        
        # Saltar si ya respondí (check en DB)
        cur.execute("SELECT respondio, email FROM leads WHERE email=?", (frm_email,))
        lead = cur.fetchone()
        if lead and lead['respondio'] == 1:
            continue
        
        full = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
        snippet = full.get('snippet', '')
        subj = headers.get('Subject', '')
        
        tipo = clasificar_respuesta(snippet, subj)
        nombre = lead['email'].split('@')[0].replace('.', ' ').title() if lead else frm_email.split('@')[0]
        
        print(f'\n   📩 {frm_email}')
        print(f'      ASUNTO: {subj[:60]}')
        print(f'      TIPO: {tipo}')
        
        if tipo == 'auto':
            print(f'      ⚠️ Auto-respuesta — ignorada')
            # Marcar como rebote si es bounce
            if any(w in snippet.lower() for w in ['delivery status', 'failure', 'bounce', 'undelivered', 'ha rebotado', 'no ha sido entregado']):
                cur.execute("UPDATE leads SET reboto=1, estado='rebotado' WHERE email=?", (frm_email,))
                conn.commit()
                print(f'      📌 Marcado como REBOTE en DB')
            continue
        
        if tipo == 'no_interesado':
            print(f'      ❌ No interesado — marcado como rebote')
            cur.execute("UPDATE leads SET reboto=1, estado='no_interesado' WHERE email=?", (frm_email,))
            conn.commit()
            continue
        
        # Interesado o duda → RESPONDER
        msg_id = responder_lead(service, frm_email, nombre, tipo)
        if msg_id:
            cur.execute("UPDATE leads SET respondio=1, fecha_respuesta=datetime('now'), notas=? WHERE email=?", 
                       (f'Respondido automáticamente. Tipo: {tipo}', frm_email))
            conn.commit()
            print(f'      ✅ Respondido automáticamente (msg_id: {msg_id})')
            
            # Log
            log_path = os.path.join(LOGS_DIR, 'respuestas.csv')
            with open(log_path, 'a', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                if os.path.getsize(log_path) == 0:
                    w.writerow(['fecha', 'email', 'tipo', 'respondido'])
                w.writerow([datetime.now().isoformat(), frm_email, tipo, msg_id])
    
    conn.close()
    
    # 3. Estadísticas finales
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM leads WHERE respondio=1")
    respondidos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE reboto=1")
    rebotados = cur.fetchone()[0]
    conn.close()
    
    print(f'\n   📊 TOTAL: {respondidos} respondidos, {rebotados} rebotados')
    print(f'   [{datetime.now().strftime("%H:%M:%S")}] ✅ Monitor completado')

if __name__ == '__main__':
    monitor()
