#!/usr/bin/env python3
"""
NEO Lead Scraper v1
Busca leads en directorios online por tipo de negocio + ciudad.
Extrae nombre, dirección, teléfono, web, email.
Filtra leads sin web o con web básica.
"""
import requests, re, json, csv, os, sys, time, random
from datetime import datetime
from urllib.parse import quote_plus
from html import unescape

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def fetch(url, timeout=10):
    for attempt in range(3):
        try:
            h = {"User-Agent": random.choice(USER_AGENTS)}
            r = requests.get(url, headers=h, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt < 2: time.sleep(2)
            else: log(f"  fail: {url[:50]}.. {e}")
    return ""

def is_basic_web(url):
    """Detecta si es web básica/gratuita (wix, webnode, etc.)"""
    if not url or url == "No": return True
    basic = ["wixsite", "webnode", "wordpress.com", "blogspot", "jimdo", "weebly"]
    for b in basic:
        if b in url.lower(): return True
    return False

def extract_email(text):
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    return emails[0] if emails else ""

# ─── Scraper: Páginas Amarillas ──────────────────────────────
def scrape_paginas_amarillas(tipo, ciudad, limite=30):
    """Busca en paginasamarillas.es"""
    log(f"Scraping Páginas Amarillas: {tipo} en {ciudad}")
    leads = []
    page = 1
    
    while len(leads) < limite and page <= 5:
        url = f"https://www.paginasamarillas.es/search/{quote_plus(tipo)}/all/{quote_plus(ciudad)}/all/all/all/all/all/{page}"
        html = fetch(url)
        if not html: break
        
        # Extract result cards
        cards = re.findall(r'<div class="bloque-negocio[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>\s*</article>', html, re.DOTALL)
        if not cards:
            # Try alternative pattern
            cards = re.findall(r'<article[^>]*class="[^"]*resultado-busqueda[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL)
        
        if not cards:
            log(f"  No more results on page {page}")
            break
        
        for card in cards:
            if len(leads) >= limite: break
            try:
                name_m = re.search(r'<h2[^>]*>(.*?)</h2>', card, re.DOTALL)
                name = re.sub(r'<[^>]+>', '', name_m.group(1)).strip() if name_m else ""
                name = unescape(name)
                
                addr_m = re.search(r'<p class="direccion"[^>]*>(.*?)</p>', card, re.DOTALL)
                addr = re.sub(r'<[^>]+>', '', addr_m.group(1)).strip() if addr_m else ""
                
                phone_m = re.search(r'<span class="telefono"[^>]*>(.*?)</span>', card, re.DOTALL)
                phone = re.sub(r'<[^>]+>', '', phone_m.group(1)).strip() if phone_m else ""
                
                web_m = re.search(r'<a[^>]*href="(https?://[^"]+)"[^>]*class="[^"]*web[^"]*"', card, re.DOTALL)
                web = web_m.group(1) if web_m else "No"
                
                if not name: continue
                
                leads.append({
                    "nombre": name, "direccion": addr, "telefono": phone,
                    "web": web, "email": "", "tipo": tipo, "ciudad": ciudad
                })
            except: pass
        
        page += 1
        time.sleep(random.uniform(1, 3))
    
    log(f"  → {len(leads)} leads encontrados")
    return leads

# ─── Scraper: Cylex ──────────────────────────────────────────
def scrape_cylex(tipo, ciudad, limite=30):
    """Busca en cylex.es"""
    log(f"Scraping Cylex: {tipo} en {ciudad}")
    leads = []
    page = 1
    
    while len(leads) < limite and page <= 5:
        url = f"https://www.cylex.es/search?q={quote_plus(tipo)}&page={page}&city={quote_plus(ciudad)}"
        html = fetch(url)
        if not html: break
        
        cards = re.findall(r'<div class="result-item"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*<div class="search-engine', html, re.DOTALL)
        if not cards:
            cards = re.findall(r'<div[^>]*class="[^"]*result[^"]*"[^>]*itemscope[^>]*>(.*?)</div>\s*</div>\s*</article>', html, re.DOTALL)
        
        if not cards:
            log(f"  No more results on page {page}")
            break
        
        for card in cards:
            if len(leads) >= limite: break
            try:
                name_m = re.search(r'<span[^>]*itemprop="name"[^>]*>(.*?)</span>', card, re.DOTALL)
                name = re.sub(r'<[^>]+>', '', name_m.group(1)).strip() if name_m else ""
                
                web_m = re.search(r'<a[^>]*href="(https?://[^"]+)"[^>]*rel="nofollow"[^>]*>', card, re.DOTALL)
                web = web_m.group(1) if web_m else "No"
                
                phone_m = re.search(r'<span[^>]*itemprop="telephone"[^>]*>(.*?)</span>', card, re.DOTALL)
                phone = re.sub(r'<[^>]+>', '', phone_m.group(1)).strip() if phone_m else ""
                
                addr_m = re.search(r'<span[^>]*itemprop="streetAddress"[^>]*>(.*?)</span>', card, re.DOTALL)
                addr = re.sub(r'<[^>]+>', '', addr_m.group(1)).strip() if addr_m else ""
                
                if not name: continue
                leads.append({
                    "nombre": name, "direccion": addr, "telefono": phone,
                    "web": web, "email": "", "tipo": tipo, "ciudad": ciudad
                })
            except: pass
        
        page += 1
        time.sleep(random.uniform(1, 2))
    
    log(f"  → {len(leads)} leads encontrados")
    return leads

# ─── Email Finder (simple) ───────────────────────────────────
def find_email(lead):
    """Intenta encontrar email del negocio"""
    web = lead.get("web", "")
    if web and web != "No":
        try:
            html = fetch(web, timeout=8)
            if html:
                emails = re.findall(r'[\w.+-]+@[\w-]+\.(?:com|es|net|org|info)', html)
                for e in emails:
                    if "info@" in e.lower() or "contacto@" in e.lower() or "hola@" in e.lower():
                        return e
                if emails:
                    return emails[0]
        except: pass
    
    # Try common patterns
    nombre = lead.get("nombre", "").lower().split()[0] if lead.get("nombre") else ""
    # info@{empresa}.com, hola@{empresa}.com
    return ""

# ─── Main ────────────────────────────────────────────────────
def save_csv(leads, tipo, ciudad):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = os.path.join(OUT_DIR, f"leads_{tipo}_{ciudad}_{ts}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre","direccion","telefono","web","email","tipo","ciudad"])
        w.writeheader()
        w.writerows(leads)
    log(f"Guardado: {path} ({len(leads)} leads)")
    return path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NEO Lead Scraper")
    parser.add_argument("--tipo", "-t", default="restaurante", help="Tipo de negocio")
    parser.add_argument("--ciudad", "-c", default="Madrid", help="Ciudad")
    parser.add_argument("--limite", "-l", type=int, default=30, help="Máx leads")
    parser.add_argument("--batch", action="store_true", help="Modo batch")
    parser.add_argument("--ciudades", default="Madrid,Barcelona", help="Ciudades (batch)")
    parser.add_argument("--tipos", default="restaurante,clinica dental,taller mecanico,abogado,peluqueria", help="Tipos (batch)")
    args = parser.parse_args()
    
    if args.batch:
        ciudades = [c.strip() for c in args.ciudades.split(",")]
        tipos = [t.strip() for t in args.tipos.split(",")]
        all_leads = []
        for ciudad in ciudades:
            for tipo in tipos:
                leads = scrape_paginas_amarillas(tipo, ciudad, args.limite)
                # Try cylex if few results
                if len(leads) < 5:
                    leads2 = scrape_cylex(tipo, ciudad, args.limite)
                    leads.extend([l for l in leads2 if l["nombre"] not in {x["nombre"] for x in leads}])
                all_leads.extend(leads)
                time.sleep(random.uniform(2, 4))
        save_csv(all_leads, "batch", f"{len(ciudades)}ciudades")
    else:
        leads = scrape_paginas_amarillas(args.tipo, args.ciudad, args.limite)
        if len(leads) < 5:
            leads2 = scrape_cylex(args.tipo, args.ciudad, args.limite)
            leads.extend([l for l in leads2 if l["nombre"] not in {x["nombre"] for x in leads}])
        save_csv(leads, args.tipo, args.ciudad)

if __name__ == "__main__":
    main()
