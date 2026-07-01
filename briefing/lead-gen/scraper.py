#!/usr/bin/env python3
"""Scraper OSM con escritura incremental y retry"""
import json, csv, os, sys, time, urllib.request, urllib.parse
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Reducido a lo que funciona bien en OSM
SECTORES = {
    "restaurantes": "amenity=restaurant",
    "clinicas": "healthcare=clinic",
    "abogados": "office=lawyer",
}
CIUDADES = {"Madrid": (40.4168, -3.7038, 10000), "Barcelona": (41.3874, 2.1686, 10000), "Malaga": (36.7213, -4.4214, 10000)}

def query_osm(tag_str, lat, lng, rad, retry=2):
    k, v = tag_str.split("=", 1)
    q = f'[out:json][timeout:20];(node["{k}"="{v}"](around:{rad},{lat},{lng});way["{k}"="{v}"](around:{rad},{lat},{lng}););out center tags 20;'
    data = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(retry + 1):
        try:
            req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=data,
                headers={"User-Agent": "NEO-Leads/1.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read()).get("elements", [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retry:
                time.sleep(5)
                continue
            raise

def extract(el):
    tags = el.get("tags", {})
    name = tags.get("name", "")
    if not name: return None
    if el["type"] == "node": lat, lon = el.get("lat", 0), el.get("lon", 0)
    else:
        c = el.get("center", {}); lat, lon = c.get("lat", 0), c.get("lon", 0)
    return {"nombre": name.strip(), "telefono": tags.get("phone","") or tags.get("contact:phone",""),
        "email": tags.get("email","") or tags.get("contact:email",""),
        "web": tags.get("website","") or tags.get("contact:website",""),
        "direccion": f'{tags.get("addr:street","")} {tags.get("addr:housenumber","")} {tags.get("addr:city","")}'.strip().strip(","),
        "lat": lat, "lon": lon}

def append_csv(lead):
    path = os.path.join(DATA_DIR, "leads.csv")
    write_header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre","sector","ciudad","telefono","email","web","direccion","lat","lon"])
        if write_header: w.writeheader()
        w.writerow(lead)

def scrape_all():
    total = 0
    for skey, stag in SECTORES.items():
        for cname, (lat, lng, rad) in CIUDADES.items():
            print(f"  {skey} en {cname}...", end=" ", flush=True)
            try:
                elements = query_osm(stag, lat, lng, rad)
                c = 0
                for el in elements:
                    lead = extract(el)
                    if lead:
                        lead["sector"] = skey
                        lead["ciudad"] = cname
                        append_csv(lead)
                        total += 1
                        c += 1
                print(f"{c} leads")
            except Exception as e:
                print(f"SKIP ({e})")
            time.sleep(1)
    return total

if __name__ == "__main__":
    print("=== SCRAPER OSM ===")
    total = scrape_all()
    print(f"\nTotal leads: {total}")
    # Resumen
    if os.path.exists(os.path.join(DATA_DIR, "leads.csv")):
        with open(os.path.join(DATA_DIR, "leads.csv")) as f:
            leads = list(csv.DictReader(f))
        for s, c in Counter(l["sector"] for l in leads).most_common():
            c_e = sum(1 for l in leads if l["sector"]==s and l["email"])
            c_t = sum(1 for l in leads if l["sector"]==s and l["telefono"])
            print(f"  {s}: {c} (email:{c_e} tel:{c_t})")
