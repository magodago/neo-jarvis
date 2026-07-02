#!/usr/bin/env python3
"""
SCRAPER OSM MASIVO — 20 ciudades, 10 sectores, miles de leads
Luego extrae emails via web scraping de las webs encontradas
"""
import json, csv, os, sys, time, urllib.request, urllib.parse, re, sqlite3
from datetime import datetime
from collections import Counter

LEAD_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(LEAD_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "leads.db")
os.makedirs(DATA_DIR, exist_ok=True)

# Fix urllib imports
import urllib.error as urlerror

# 20 CIUDADES principales de España con coordenadas y radio
CIUDADES = {
    "Madrid": (40.4168, -3.7038, 15000),
    "Barcelona": (41.3874, 2.1686, 15000),
    "Valencia": (39.4699, -0.3763, 12000),
    "Sevilla": (37.3891, -5.9845, 12000),
    "Zaragoza": (41.6488, -0.8891, 10000),
    "Malaga": (36.7213, -4.4214, 10000),
    "Murcia": (37.9922, -1.1307, 10000),
    "Palma": (39.5696, 2.6502, 10000),
    "Bilbao": (43.2630, -2.9350, 10000),
    "Alicante": (38.3452, -0.4810, 10000),
    "Cordoba": (37.8882, -4.7794, 8000),
    "Valladolid": (41.6523, -4.7245, 8000),
    "Vigo": (42.2406, -8.7207, 8000),
    "Gijon": (43.5322, -5.6611, 8000),
    "Granada": (37.1773, -3.5986, 8000),
    "San Sebastian": (43.3183, -1.9812, 8000),
    "Pamplona": (42.8125, -1.6458, 8000),
    "Santander": (43.4623, -3.8099, 8000),
    "Toledo": (39.8628, -4.0273, 8000),
    "Badajoz": (38.8794, -6.9706, 8000),
}

# 10 SECTORES con sus etiquetas OSM
SECTORES = {
    "restaurantes": "amenity=restaurant",
    "bares": "amenity=cafe",
    "clinicas": "healthcare=clinic",
    "dentistas": "amenity=dentist",
    "abogados": "office=lawyer",
    "talleres": "shop=car_repair",
    "peluquerias": "shop=hairdresser",
    "farmacias": "amenity=pharmacy",
    "gimnasios": "leisure=fitness_centre",
    "inmobiliarias": "office=estate_agent",
}

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db():
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
            encontrado_por TEXT DEFAULT 'osm',
            fecha_scrapeo TEXT
        )
    """)
    for col in ['encontrado_por', 'fecha_scrapeo']:
        try:
            cur.execute(f"SELECT {col} FROM leads LIMIT 1")
        except:
            cur.execute(f"ALTER TABLE leads ADD COLUMN {col} TEXT")
    conn.commit()
    conn.close()

def osm_search(tag_str, lat, lng, rad, retry=3):
    """Query Overpass API con retry"""
    k, v = tag_str.split("=", 1)
    q = f'[out:json][timeout:30];(node["{k}"="{v}"](around:{rad},{lat},{lng});way["{k}"="{v}"](around:{rad},{lat},{lng});rel["{k}"="{v}"](around:{rad},{lat},{lng}););out center tags 30;'
    data = urllib.parse.urlencode({"data": q}).encode()
    
    for attempt in range(retry + 1):
        try:
            req = urllib.request.Request("https://overpass-api.de/api/interpreter", 
                data=data, headers={"User-Agent": "NEO-Leads-Massive/2.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read()).get("elements", [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retry:
                wait = 5 * (attempt + 1)
                print(f"\n    ⏳ Rate limit, esperando {wait}s...")
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            if attempt < retry:
                time.sleep(3)
                continue
            raise
    return []

def extract_lead(el, sector, ciudad):
    """Extrae datos de un elemento OSM"""
    tags = el.get("tags", {})
    name = tags.get("name", "")
    if not name:
        return None
    
    if el["type"] == "node":
        lat, lon = el.get("lat", 0), el.get("lon", 0)
    else:
        c = el.get("center", {})
        lat, lon = c.get("lat", 0), c.get("lon", 0)
    
    phone = tags.get("phone", "") or tags.get("contact:phone", "")
    email = (tags.get("email", "") or tags.get("contact:email", "")).strip().lower()
    web = (tags.get("website", "") or tags.get("contact:website", "")).strip()
    street = tags.get("addr:street", "")
    number = tags.get("addr:housenumber", "")
    addr_city = tags.get("addr:city", "")
    direction = f"{street} {number} {addr_city}".strip().strip(",")
    
    return {
        "nombre": name.strip(),
        "sector": sector,
        "ciudad": ciudad,
        "telefono": phone,
        "email": email,
        "web": web,
        "direccion": direction,
        "lat": lat,
        "lon": lon,
    }

def save_lead(lead):
    """Guarda lead en DB si no existe ya"""
    conn = get_db()
    cur = conn.cursor()
    
    # Check duplicado por nombre+ciudad o email
    if lead["email"]:
        cur.execute("SELECT id FROM leads WHERE email = ?", (lead["email"],))
        if cur.fetchone():
            conn.close()
            return
    elif lead["web"]:
        cur.execute("SELECT id FROM leads WHERE web = ? AND nombre = ?", (lead["web"], lead["nombre"]))
        if cur.fetchone():
            conn.close()
            return
    else:
        cur.execute("SELECT id FROM leads WHERE nombre = ? AND ciudad = ? AND sector = ?", 
                   (lead["nombre"], lead["ciudad"], lead["sector"]))
        if cur.fetchone():
            conn.close()
            return
    
    cur.execute("""
        INSERT INTO leads (nombre, sector, ciudad, telefono, web, email, direccion, lat, lon, encontrado_por, fecha_scrapeo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'osm', ?)
    """, (lead["nombre"], lead["sector"], lead["ciudad"], lead["telefono"], 
          lead["web"], lead["email"], lead["direccion"], lead["lat"], lead["lon"],
          datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def scrape_webs_emails():
    """Visita webs de leads que tienen web pero no email, y extrae email"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, web FROM leads WHERE web IS NOT NULL AND web != '' AND (email IS NULL OR email = '')")
    targets = cur.fetchall()
    conn.close()
    
    if not targets:
        print("  ✅ No hay leads con web pendientes de scrapear")
        return 0
    
    print(f"\n  🌐 Scrapeando {len(targets)} webs para extraer emails...")
    encontrados = 0
    
    for t in targets:
        lid, nombre, web = t['id'], t['nombre'], t['web']
        if not web.startswith('http'):
            web = 'https://' + web
        
        emails = set()
        try:
            time.sleep(1.2)
            req = urllib.request.Request(web, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html',
                'Accept-Language': 'es-ES,es;q=0.9',
            })
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            found = EMAIL_REGEX.findall(html)
            for e in found:
                el = e.lower()
                if not any(x in el for x in ['noreply', 'no-reply', 'test@', 'sentry', '.png', '.jpg', '.gif', '.svg']):
                    if not el.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails.add(el)
            
            # Buscar también páginas de contacto
            contact_links = []
            for link in re.findall(r'href=["\']([^"\']*)["\']', html):
                lower = link.lower()
                if any(w in lower for w in ['contacto', 'contact', 'mail', 'about', 'nosotros']):
                    if link.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urllib.parse.urlparse(web)
                        contact_links.append(f"{parsed.scheme}://{parsed.netloc}{link}")
                    elif link.startswith('http'):
                        contact_links.append(link)
            
            for cu in contact_links[:2]:
                try:
                    time.sleep(1)
                    req2 = urllib.request.Request(cu, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    })
                    with urllib.request.urlopen(req2, timeout=10) as resp2:
                        html2 = resp2.read().decode('utf-8', errors='ignore')
                    found2 = EMAIL_REGEX.findall(html2)
                    for e in found2:
                        el = e.lower()
                        if not any(x in el for x in ['noreply', 'no-reply', 'test@', 'sentry']) and not el.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                            emails.add(el)
                except:
                    pass
        except Exception as e:
            pass
        
        if emails:
            email = list(emails)[0]
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE leads SET email = ?, fecha_scrapeo = ?, encontrado_por = 'osm+web' WHERE id = ?",
                       (email, datetime.now().isoformat(), lid))
            conn.commit()
            conn.close()
            encontrados += 1
            print(f"    ✅ {email}")
        else:
            print(f"    ❌ Sin email")
    
    return encontrados

def run_massive_scrape():
    """Scrapea todas las ciudades x sectores"""
    print(f"\n{'='*60}")
    print(f"🔍 SCRAPER OSM MASIVO")
    print(f"📊 {len(CIUDADES)} ciudades x {len(SECTORES)} sectores = {len(CIUDADES)*len(SECTORES)} queries")
    print(f"{'='*60}")
    
    ensure_db()
    total = 0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    for skey, stag in SECTORES.items():
        for cname, (lat, lng, rad) in CIUDADES.items():
            sys.stdout.write(f"\n  📍 {skey} en {cname}... ")
            sys.stdout.flush()
            try:
                elements = osm_search(stag, lat, lng, rad)
                count = 0
                for el in elements:
                    lead = extract_lead(el, skey, cname)
                    if lead:
                        save_lead(lead)
                        count += 1
                total += count
                print(f"{count} leads", end="")
                # Mostrar email count
                emails = sum(1 for el in elements if el.get("tags", {}).get("email") or el.get("tags", {}).get("contact:email"))
                if emails:
                    print(f" ({emails} emails directos)", end="")
                print()
            except Exception as e:
                print(f"❌ ERROR: {e}")
            time.sleep(0.8)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL: {total} leads nuevos (ejecución: {timestamp})")
    print(f"{'='*60}")
    
    return total

def stats():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM leads")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''")
    con_email = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE web IS NOT NULL AND web != ''")
    con_web = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''")
    con_telf = cur.fetchone()[0]
    
    print(f"\n📊 ESTADO DE LA BASE DE DATOS")
    print(f"{'='*40}")
    print(f"📈 Total leads:     {total}")
    print(f"📧 Con email:       {con_email} ({con_email*100//max(total,1)}%)")
    print(f"🌐 Con web:         {con_web} ({con_web*100//max(total,1)}%)")
    print(f"📞 Con teléfono:    {con_telf} ({con_telf*100//max(total,1)}%)")
    
    print(f"\n📂 Por sector:")
    cur.execute("SELECT sector, COUNT(*), SUM(CASE WHEN email!='' THEN 1 ELSE 0 END) FROM leads GROUP BY sector ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} (📧{row[2]})")
    
    print(f"\n🗺️  Por ciudad (top 10):")
    cur.execute("SELECT ciudad, COUNT(*), SUM(CASE WHEN email!='' THEN 1 ELSE 0 END) FROM leads GROUP BY ciudad ORDER BY COUNT(*) DESC LIMIT 10")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} (📧{row[2]})")
    
    conn.close()

if __name__ == '__main__':
    ensure_db()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'scrape':
            run_massive_scrape()
            print("\n🔍 Fase 2: Scrapeando webs para emails...")
            encontrados = scrape_webs_emails()
            print(f"  ✅ {encontrados} emails nuevos scrapeados de webs")
            stats()
        elif cmd == 'web-scrape':
            scrape_webs_emails()
            stats()
        elif cmd == 'stats':
            stats()
        else:
            print("Comandos: scrape, web-scrape, stats")
    else:
        stats()
