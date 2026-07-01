#!/usr/bin/env python3
"""
MOTOR DE LEAD GENERATION NEO — Busca leads por cualquier medio disponible
Estrategias:
1. Web scraping de webs leads actuales (extraer emails)
2. Búsqueda en Google de negocios con email
3. Scraping de directorios
4. Google Maps API Places (si hay key)
"""
import os, sys, csv, re, json, sqlite3, time, urllib.request, urllib.error, urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
import base64

LEAD_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(LEAD_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "leads.db")
os.makedirs(DATA_DIR, exist_ok=True)

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
TELF_REGEX = re.compile(r'(?:\+34|0034)?[\s.-]?(\d{3})[\s.-]?(\d{3})[\s.-]?(\d{3})')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_schema():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, sector TEXT, ciudad TEXT, telefono TEXT,
            web TEXT, email TEXT, direccion TEXT, lat REAL, lon REAL,
            enviado INTEGER DEFAULT 0, asunto TEXT, message_id TEXT,
            fecha_envio TEXT, estado_envio TEXT DEFAULT '',
            respondido INTEGER DEFAULT 0,
            encontrado_por TEXT DEFAULT 'manual',
            fecha_scrapeo TEXT
        )
    """)
    # Check if encontrado_por exists
    try:
        cur.execute("SELECT encontrado_por FROM leads LIMIT 1")
    except:
        cur.execute("ALTER TABLE leads ADD COLUMN encontrado_por TEXT DEFAULT 'manual'")
    try:
        cur.execute("SELECT fecha_scrapeo FROM leads LIMIT 1")
    except:
        cur.execute("ALTER TABLE leads ADD COLUMN fecha_scrapeo TEXT")
    conn.commit()
    conn.close()

def scrape_website_for_emails(url, timeout=15):
    """Visita una web y extrae emails + teléfonos"""
    emails = set()
    telfs = set()
    if not url or url == '':
        return emails, telfs
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Extraer emails del HTML
        found = EMAIL_REGEX.findall(html)
        for e in found:
            e_lower = e.lower()
            if any(ignore in e_lower for ignore in ['noreply', 'no-reply', 'test@', 'sentry', '.png', '.jpg', '.gif', '.svg']):
                continue
            if not e_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                emails.add(e_lower)
        
        # Buscar también páginas de contacto
        contact_urls = []
        for link in re.findall(r'href=["\']([^"\']*)["\']', html):
            lower = link.lower()
            if any(word in lower for word in ['contacto', 'contact', 'mail', 'email', 'about', 'nosotros']):
                if link.startswith('/'):
                    from urllib.parse import urlparse
                    parsed = urllib.parse.urlparse(url)
                    contact_urls.append(f"{parsed.scheme}://{parsed.netloc}{link}")
                elif link.startswith('http'):
                    contact_urls.append(link)
        
        for cu in contact_urls[:3]:  # Max 3 páginas de contacto
            try:
                time.sleep(1)
                req2 = urllib.request.Request(cu, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                })
                with urllib.request.urlopen(req2, timeout=timeout) as resp2:
                    html2 = resp2.read().decode('utf-8', errors='ignore')
                found2 = EMAIL_REGEX.findall(html2)
                for e in found2:
                    e_lower = e.lower()
                    if not any(ignore in e_lower for ignore in ['noreply', 'no-reply', 'test@', 'sentry']) and not e_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails.add(e_lower)
                
                telf_found = TELF_REGEX.findall(html2)
                for t in telf_found:
                    telfs.add(f"+34 {t[0]} {t[1]} {t[2]}")
            except:
                pass
    except Exception as e:
        pass
    return emails, telfs

def scrape_webs_leads_existentes():
    """Scrapea emails de las webs de leads que ya tenemos"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, web, ciudad, sector FROM leads WHERE web IS NOT NULL AND web != '' AND (email IS NULL OR email = '')")
    leads = cur.fetchall()
    print(f"📡 Scrapeando {len(leads)} webs para extraer emails...")
    
    encontrados = 0
    for lead in leads:
        lid, nombre, web, ciudad, sector = lead['id'], lead['nombre'], lead['web'], lead['ciudad'], lead['sector']
        print(f"  → {nombre}: {web}")
        emails, telfs = scrape_website_for_emails(web)
        if emails:
            email_principal = list(emails)[0]
            cur.execute("UPDATE leads SET email = ?, fecha_scrapeo = ?, encontrado_por = 'web_scrape' WHERE id = ?",
                       (email_principal, datetime.now().isoformat(), lid))
            print(f"    ✅ Email encontrado: {email_principal}")
            if telfs:
                telf = list(telfs)[0]
                cur.execute("UPDATE leads SET telefono = ? WHERE id = ? AND (telefono IS NULL OR telefono = '')", (telf, lid))
        else:
            print(f"    ❌ Sin email encontrado")
        time.sleep(1.5)  # Rate limiting
    
    conn.commit()
    conn.close()
    print(f"\n✅ Scrapeo completado: {encontrados} emails nuevos de {len(leads)} webs")

def importar_csv_externo(csv_path):
    """Importa leads desde cualquier CSV"""
    conn = get_db()
    cur = conn.cursor()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        nuevos = 0
        for row in reader:
            nombre = row.get('nombre', row.get('name', row.get('Nombre', ''))).strip()
            email = row.get('email', row.get('Email', row.get('mail', ''))).strip().lower()
            telefono = row.get('telefono', row.get('phone', row.get('Teléfono', row.get('Telefono', '')))).strip()
            web = row.get('web', row.get('website', row.get('Web', row.get('Website', '')))).strip()
            ciudad = row.get('ciudad', row.get('city', row.get('Ciudad', ''))).strip()
            sector = row.get('sector', row.get('Sector', 'general')).strip()
            direccion = row.get('direccion', row.get('address', row.get('Dirección', ''))).strip()
            
            if not email and not web:
                continue
            
            # Check duplicado por email o web
            if email:
                cur.execute("SELECT id FROM leads WHERE email = ?", (email,))
                if cur.fetchone():
                    continue
            if web and not email:
                cur.execute("SELECT id FROM leads WHERE web = ?", (web,))
                if cur.fetchone():
                    continue
            
            cur.execute("""
                INSERT INTO leads (nombre, sector, ciudad, telefono, web, email, direccion, encontrado_por, fecha_scrapeo)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'csv_import', ?)
            """, (nombre, sector, ciudad, telefono, web, email, direccion, datetime.now().isoformat()))
            nuevos += 1
        
        conn.commit()
        print(f"✅ Importados {nuevos} leads nuevos de {csv_path}")
    conn.close()

def exportar_leads_csv(output_path=None):
    """Exporta todos los leads a CSV"""
    if not output_path:
        output_path = os.path.join(DATA_DIR, f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads WHERE email IS NOT NULL AND email != '' ORDER BY id")
    rows = cur.fetchall()
    
    if not rows:
        print("No hay leads con email para exportar")
        return
    
    columns = [desc[0] for desc in cur.description]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[c] for c in columns])
    
    conn.close()
    print(f"✅ Exportados {len(rows)} leads a {output_path}")
    return output_path

def stats():
    """Muestra estadísticas de la DB"""
    conn = get_db()
    cur = conn.cursor()
    
    print("=" * 60)
    print("📊 ESTADÍSTICAS DE LEADS")
    print("=" * 60)
    
    cur.execute("SELECT COUNT(*) FROM leads")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''")
    con_email = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM leads WHERE web IS NOT NULL AND web != ''")
    con_web = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''")
    con_telf = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM leads WHERE enviado = 1")
    enviados = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM leads WHERE respondido = 1")
    respondidos = cur.fetchone()[0]
    
    print(f"\n📈 Total leads: {total}")
    print(f"📧 Con email: {con_email}")
    print(f"🌐 Con web: {con_web}")
    print(f"📞 Con teléfono: {con_telf}")
    print(f"📨 Enviados: {enviados}")
    print(f"📩 Respondidos: {respondidos}")
    
    print("\n📂 Por sector:")
    cur.execute("SELECT sector, COUNT(*), SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) FROM leads GROUP BY sector ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} total | {row[2]} con email")
    
    print("\n🗺️ Por ciudad:")
    cur.execute("SELECT ciudad, COUNT(*), SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) FROM leads GROUP BY ciudad ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} total | {row[2]} con email")
    
    conn.close()

def add_lead(nombre, email=None, telefono=None, web=None, ciudad='', sector='general', 
             direccion='', encontrado_por='manual'):
    """Añade un lead individual"""
    conn = get_db()
    cur = conn.cursor()
    
    if email:
        cur.execute("SELECT id FROM leads WHERE email = ?", (email.lower(),))
        if cur.fetchone():
            conn.close()
            return False, "Email duplicado"
    
    cur.execute("""
        INSERT INTO leads (nombre, sector, ciudad, telefono, web, email, direccion, encontrado_por, fecha_scrapeo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, sector, ciudad, telefono, web, email, direccion, encontrado_por, datetime.now().isoformat()))
    
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return True, new_id

if __name__ == '__main__':
    ensure_schema()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'scrape':
            scrape_webs_leads_existentes()
        elif cmd == 'import':
            importar_csv_externo(sys.argv[2])
        elif cmd == 'export':
            exportar_leads_csv()
        elif cmd == 'stats':
            stats()
        elif cmd == 'add' and len(sys.argv) >= 3:
            add_lead(sys.argv[2])
            print(f"Lead añadido: {sys.argv[2]}")
        else:
            print("Comandos: scrape, import <csv>, export, stats, add <nombre>")
    else:
        stats()
