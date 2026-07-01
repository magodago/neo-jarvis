#!/usr/bin/env python3
"""
NEO Lead Scraper v2
Busca leads usando OpenStreetMap Overpass API + Google Maps como fallback.
Gratis, sin API key, sin límites significativos.
"""
import requests, re, json, csv, os, sys, time, random, urllib.parse
from datetime import datetime

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)

# Mapeo: tipo de negocio -> tags de OSM + sector legible
SECTOR_MAP = {
    "restaurante":     {"tags": [('amenity','restaurant'),('amenity','fast_food'),('cuisine','')], "sector": "Restaurante"},
    "clinica dental":  {"tags": [('amenity','dentist'),('healthcare','dentist')], "sector": "Clínica Dental"},
    "taller mecanico": {"tags": [('shop','car_repair'),('craft','mechanic')], "sector": "Taller"},
    "abogado":         {"tags": [('office','lawyer'),('craft','lawyer')], "sector": "Abogado"},
    "peluqueria":      {"tags": [('shop','hairdresser'),('craft','hairdresser')], "sector": "Peluquería"},
    "clinica":         {"tags": [('amenity','clinic'),('healthcare','clinic')], "sector": "Clínica"},
    "gimnasio":        {"tags": [('leisure','fitness_centre'),('sport','gym')], "sector": "Gimnasio"},
    "tienda":          {"tags": [('shop','*')], "sector": "Tienda"},
}

CIUDAD_COORDS = {
    "Madrid":    {"lat": 40.4168, "lon": -3.7038, "radio": 5000},
    "Barcelona": {"lat": 41.3874, "lon": 2.1686, "radio": 5000},
    "Valencia":  {"lat": 39.4699, "lon": -0.3763, "radio": 4000},
    "Sevilla":   {"lat": 37.3891, "lon": -5.9845, "radio": 4000},
    "Málaga":    {"lat": 36.7213, "lon": -4.4213, "radio": 4000},
    "Zaragoza":  {"lat": 41.6488, "lon": -0.8891, "radio": 3500},
    "Bilbao":    {"lat": 43.2630, "lon": -2.9350, "radio": 3000},
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def fetch_overpass(query, timeout=30):
    for attempt in range(3):
        try:
            r = requests.get(OVERPASS_URL, params={"data": query}, 
                           headers={"User-Agent": "NEOLeads/1.0"},
                           timeout=timeout)
            if r.status_code == 429:
                t = int(r.headers.get("Retry-After", 5))
                log(f"  rate limited, waiting {t}s...")
                time.sleep(t)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                log(f"  Overpass error: {e}")
    return {"elements": []}

def scrape_osm(tipo, ciudad, limite=50):
    """Busca negocios en OpenStreetMap"""
    if tipo not in SECTOR_MAP and tipo not in CIUDAD_COORDS:
        if tipo not in SECTOR_MAP:
            log(f"  Tipo '{tipo}' no mapeado, usando tag genérico")
            tags = [(k,v) for k,v in SECTOR_MAP.get(list(SECTOR_MAP.keys())[0])["tags"]]
        else:
            tags = SECTOR_MAP[tipo]["tags"]
    else:
        tags = SECTOR_MAP.get(tipo, {"tags": [('shop','*')]})["tags"]
    
    city_data = CIUDAD_COORDS.get(ciudad, {"lat":40.4168,"lon":-3.7038,"radio":5000})
    lat, lon, radio = city_data["lat"], city_data["lon"], city_data["radio"]
    
    sector_label = SECTOR_MAP.get(tipo, {}).get("sector", tipo)
    
    # Build Overpass query - search for nodes and ways with the tags
    tag_filters = []
    for k, v in tags:
        if v == '*':
            tag_filters.append(f'["{k}"]')
        elif v:
            tag_filters.append(f'["{k}"="{v}"]')
        else:
            tag_filters.append(f'["{k}"]')
    
    tag_str = "".join(tag_filters)
    
    query = f"""
    [out:json][timeout:25];
    (
      node{tag_str}(around:{radio},{lat},{lon});
      way{tag_str}(around:{radio},{lat},{lon});
    );
    out center {limite};
    """
    
    log(f"  Query OSM: {tipo} en {ciudad} (radio {radio}m)")
    data = fetch_overpass(query)
    elements = data.get("elements", [])
    log(f"  → {len(elements)} resultados OSM")
    
    leads = []
    for el in elements[:limite]:
        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name: continue
        
        # Get coordinates
        if el["type"] == "node":
            el_lat, el_lon = el.get("lat", 0), el.get("lon", 0)
        else:
            center = el.get("center", {})
            el_lat, el_lon = center.get("lat", 0), center.get("lon", 0)
        
        phone = tags.get("phone", tags.get("contact:phone", ""))
        website = tags.get("website", tags.get("contact:website", ""))
        email = tags.get("email", tags.get("contact:email", ""))
        
        # Clean phone (Spanish format)
        phone = re.sub(r'[^\d+]', '', phone)
        if phone and not phone.startswith('+34') and len(phone) == 9:
            phone = "+34" + phone
        
        # Build address
        addr_parts = [tags.get(k, "") for k in ["addr:street", "addr:housenumber", "addr:postcode", "addr:city"]]
        address = ", ".join(p for p in addr_parts if p)
        if not address:
            address = f"{ciudad}"
        
        lead = {
            "nombre": name,
            "direccion": address,
            "telefono": phone,
            "web": website if website else "No",
            "email": email,
            "tipo": sector_label,
            "ciudad": ciudad,
            "lat": el_lat,
            "lon": el_lon,
        }
        leads.append(lead)
    
    log(f"  → {len(leads)} leads con nombre")
    return leads

def find_website_via_google(lead):
    """Try to find website by googling the business name + city"""
    name = lead.get("nombre", "")
    ciudad = lead.get("ciudad", "")
    if not name: return ""
    try:
        q = urllib.parse.quote(f"{name} {ciudad}")
        r = requests.get(f"https://www.google.com/search?q={q}", 
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code == 200:
            # Extract first result URL
            urls = re.findall(r'href="(https?://[^"]+)"', r.text)
            for url in urls:
                if "google.com" not in url and "youtube.com" not in url:
                    return url.split('&')[0]
    except: pass
    return ""

def enrich_leads(leads):
    """Enrich leads: find websites/emails for those without"""
    for i, lead in enumerate(leads):
        if lead["web"] in ("No", "") or not lead["email"]:
            log(f"  Enriching [{i+1}/{len(leads)}] {lead['nombre'][:30]}...")
            if lead["web"] in ("No", ""):
                web = find_website_via_google(lead)
                if web:
                    lead["web"] = web
            time.sleep(1)

def save_csv(leads, tipo, ciudad):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = os.path.join(OUT_DIR, f"leads_{tipo}_{ciudad}_{ts}.csv")
    fieldnames = ["nombre","direccion","telefono","web","email","tipo","ciudad","lat","lon"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(leads)
    log(f"  Guardado: {path} ({len(leads)} leads)")
    return path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NEO Lead Scraper v2")
    parser.add_argument("--tipo", "-t", default="restaurante", 
                       choices=list(SECTOR_MAP.keys()) + ["todas"],
                       help="Tipo de negocio (o 'todas')")
    parser.add_argument("--ciudad", "-c", default="Madrid", help="Ciudad")
    parser.add_argument("--limite", "-l", type=int, default=30, help="Máx leads por tipo")
    parser.add_argument("--batch", action="store_true", help="Modo batch múltiples ciudades/tipos")
    parser.add_argument("--enrich", action="store_true", help="Enriquecer (buscar webs)")
    args = parser.parse_args()
    
    if args.batch or args.tipo == "todas":
        ciudades = list(CIUDAD_COORDS.keys())
        tipos = list(SECTOR_MAP.keys())
        all_leads = []
        for ciudad in ciudades[:3]:  # Top 3 ciudades por defecto
            for tipo in tipos:
                log(f"\n--- {tipo} en {ciudad} ---")
                leads = scrape_osm(tipo, ciudad, args.limite)
                all_leads.extend(leads)
                time.sleep(3)
        if args.enrich and all_leads:
            log("\n--- Enriching leads ---")
            enrich_leads(all_leads)
        save_csv(all_leads, "batch", f"{len(ciudades)}ciudades")
    else:
        leads = scrape_osm(args.tipo, args.ciudad, args.limite)
        if args.enrich and leads:
            enrich_leads(leads)
        save_csv(leads, args.tipo, args.ciudad)

if __name__ == "__main__":
    main()
