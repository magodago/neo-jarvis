#!/usr/bin/env python3
"""NEO — Continúa el scraper desde query 10 (queda de 11 a 25)"""
import json, os, sqlite3, re, urllib.request, ssl, sys, time
from datetime import datetime

# Import API key from main scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from places_scraper import API_KEY
API_URL = "https://places.googleapis.com/v1/places:searchText"
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'leads.db')
PAGE_SIZE = 20

SECTORS_CITIES = [
    ("restaurantes", "Madrid"), ("restaurantes", "Barcelona"), ("restaurantes", "Valencia"),
    ("restaurantes", "Sevilla"), ("restaurantes", "Málaga"), ("restaurantes", "Bilbao"),
    ("abogados", "Madrid"), ("abogados", "Barcelona"), ("abogados", "Valencia"),
    ("clínicas dentales", "Madrid"),  # hasta aquí completado
    # PENDIENTES (11-25):
    ("clínicas dentales", "Barcelona"),
    ("peluquerías", "Madrid"),
    ("peluquerías", "Barcelona"),
    ("talleres mecánicos", "Madrid"),
    ("clínicas estética", "Madrid"),
    ("inmobiliarias", "Madrid"),
    ("inmobiliarias", "Barcelona"),
    ("odontólogos", "Madrid"),
    ("odontólogos", "Barcelona"),
    ("centros de estética", "Valencia"),
    ("talleres", "Barcelona"),
    ("restaurantes", "Zaragoza"),
    ("restaurantes", "Murcia"),
    ("abogados", "Sevilla"),
    ("clínicas dentales", "Valencia"),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
SKIP_EMAILS = ['example.com','domain.com','noreply','no-reply','donotreply',
               'sentry@','.png','.jpg','.gif','.css','.js','.svg','.webp',
               'google.com','facebook.com','twitter.com','instagram.com',
               'youtube.com','linkedin.com','tiktok.com','pinterest.com',
               'wordpress.com','wixpress.com','cdn.']

def clean_phone(p):
    if not p: return ''
    p = re.sub(r'[^\d+]', '', p)
    return p[:15]

def extract_email(url, timeout=8):
    if not url: return ''
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'es-ES,es;q=0.9',
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        found = EMAIL_RE.findall(html)
        for e in found:
            e = e.strip().lower()
            if any(s in e for s in SKIP_EMAILS): continue
            if len(e) < 6 or len(e) > 80: continue
            if e.count('@') != 1: continue
            if e.split('@')[1] not in ('gmail.com','yahoo.es','yahoo.com','hotmail.com','outlook.com'):
                return e
        for e in found:
            e = e.strip().lower()
            if any(s in e for s in SKIP_EMAILS): continue
            if len(e) > 5 and '@' in e:
                return e
    except:
        pass
    return ''

def search_places(query, sector, city, page_token=None):
    params = {"textQuery": query, "maxResultCount": PAGE_SIZE}
    if page_token:
        params["pageToken"] = page_token
    data = json.dumps(params).encode()
    req = urllib.request.Request(API_URL, data=data, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.websiteUri,places.internationalPhoneNumber,nextPageToken",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return {}

def scrape_restantes():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    total_nuevos = 0
    total_emails = 0

    for idx, (sector, city) in enumerate(SECTORS_CITIES):
        query = f"{sector} en {city}"
        print(f"\n📍 [{idx+1}/{len(SECTORS_CITIES)}] {query}")
        
        page_token = None
        page = 0
        while page < 3:
            result = search_places(query, sector, city, page_token)
            places = result.get('places', [])
            
            if not places:
                if page == 0:
                    print(f"  ⚠️ Sin resultados")
                break
            
            for p in places:
                name = p.get('displayName', {}).get('text', '')
                addr = p.get('formattedAddress', '')
                phone = clean_phone(p.get('internationalPhoneNumber', ''))
                web = p.get('websiteUri', '')
                
                if not name:
                    continue
                
                c.execute("SELECT id, email FROM leads WHERE nombre=? AND ciudad=?", (name, city))
                existing = c.fetchone()
                
                if existing:
                    if not existing[1] and web:
                        email = extract_email(web)
                        if email:
                            c.execute("UPDATE leads SET email=?, web=?, telefono=? WHERE id=?", 
                                     (email, web, phone, existing[0]))
                            conn.commit()
                            total_emails += 1
                            print(f"  ➕ Email nuevo: {email} ({name[:25]})")
                    continue
                
                email = extract_email(web) if web else ''
                c.execute("""INSERT INTO leads (nombre, email, telefono, web, direccion, sector, ciudad, 
                            encontrado_por, fecha_scrapeo, created_at)
                            VALUES (?,?,?,?,?,?,?,'places_api',?,datetime('now'))""",
                         (name, email, phone, web, addr, sector, city, 
                          datetime.now().strftime('%Y-%m-%d %H:%M')))
                conn.commit()
                total_nuevos += 1
                if email:
                    total_emails += 1
                print(f"  ✅ {name[:30]:30s} {'📧' if email else '  '} {phone[:12] if phone else ''}")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                break
            page += 1
            time.sleep(0.5)
        
        time.sleep(1)
    
    conn.close()
    print(f"\n{'='*50}")
    print(f"📊 TOTAL RONDA: {total_nuevos} leads nuevos, {total_emails} con email")
    print(f"{'='*50}")

if __name__ == '__main__':
    scrape_restantes()
