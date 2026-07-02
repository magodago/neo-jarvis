#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO CAMPAIGNS — Prospector de clientes B2B
============================================
Busca empresas que podrían comprar leads sectoriales en Madrid y las guarda.
Luego permite enviarles el sales pitch de NEO Campaigns.

Uso:
  python3 prospector.py --buscar "seguridad privada Madrid"
  python3 prospector.py --buscar "empresas de alarmas" --enviar
"""
import os, sys, json, base64, time, sqlite3, csv, argparse
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import GOOGLE_PLACES_API_KEY, TOKEN_FILE, SCOPES, CLIENTES_DB

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "clientes")
LOGS_DIR = os.path.join(BASE, "..", "lead-gen", "logs")
os.makedirs(DATA_DIR, exist_ok=True)

# ── Sectores compradores vs sectores objetivo ──
# (qué tipo de empresa compra leads de qué sector)
MATRIZ_COMPRA = {
    "seguridad": {
        "compradores": ["seguridad privada", "empresas de alarmas", "protección patrimonial", "seguridad electrónica", "circuito cerrado", "vigilancia", "sistemas de seguridad"],
        "targets": ["talleres mecánicos", "restaurantes", "clínicas dentales", "almacenes", "tiendas"],
        "por_que": "Quieren vender alarmas y cámaras a negocios con inventario valioso"
    },
    "tpv": {
        "compradores": ["tpv", "datáfono", "soluciones de pago", "terminal punto de venta", "pos", "medios de pago"],
        "targets": ["restaurantes", "peluquerías", "tiendas"],
        "por_que": "Negocios con volumen de transacciones necesitan TPV"
    },
    "seguros": {
        "compradores": ["seguros", "correduría de seguros", "mediador de seguros"],
        "targets": ["talleres mecánicos", "clínicas dentales", "restaurantes"],
        "por_que": "Negocios necesitan seguros obligatorios"
    },
    "software": {
        "compradores": ["software gestión", "soluciones cloud", "erp", "crm", "gestión empresarial"],
        "targets": ["clínicas dentales", "restaurantes", "inmobiliarias"],
        "por_que": "Automatizar gestión de clientes y operaciones"
    },
    "limpieza": {
        "compradores": ["limpieza profesional", "mantenimiento", "servicios de limpieza"],
        "targets": ["clínicas dentales", "restaurantes", "clínicas médicas", "peluquerías"],
        "por_que": "Negocios necesitan limpieza profesional periódica"
    },
    "formacion": {
        "compradores": ["formación profesional", "escuela de negocios", "consultoría"],
        "targets": ["talleres mecánicos", "restaurantes", "peluquerías"],
        "por_que": "Negocios necesitan formación continua para sus empleados"
    }
}

def db_init():
    conn = sqlite3.connect(os.path.join(DATA_DIR, "clientes.db"))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT,
        telefono TEXT,
        direccion TEXT,
        website TEXT,
        sector_comprador TEXT,
        fecha_creacion TEXT,
        email_enviado INTEGER DEFAULT 0,
        notas TEXT
    )""")
    conn.commit()
    return conn

def buscar_empresas(query, limite=30):
    """Busca empresas usando Google Places API"""
    api_key = GOOGLE_PLACES_API_KEY
    url = f"https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.websiteUri,places.internationalPhoneNumber"
    }
    
    body = {
        "textQuery": query,
        "pageSize": min(limite, 20)
    }
    
    try:
        import urllib.request
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"❌ Error API: {e}")
        return []
    
    resultados = []
    for p in data.get("places", []):
        d = p.get("displayName", {})
        resultados.append({
            "nombre": d.get("text", ""),
            "email": "",
            "telefono": p.get("internationalPhoneNumber", ""),
            "direccion": p.get("formattedAddress", ""),
            "website": p.get("websiteUri", ""),
        })
    
    return resultados

def guardar_clientes(conn, empresas, sector_comprador):
    """Guarda empresas en la DB"""
    c = conn.cursor()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    insertados = 0
    for emp in empresas:
        if not emp["nombre"]:
            continue
        c.execute("SELECT id FROM clientes WHERE nombre=? AND sector_comprador=?", 
                  (emp["nombre"], sector_comprador))
        if c.fetchone():
            continue
        c.execute("""INSERT INTO clientes (nombre, email, telefono, direccion, website, sector_comprador, fecha_creacion)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (emp["nombre"], emp["email"], emp["telefono"], emp["direccion"],
                   emp["website"], sector_comprador, ahora))
        insertados += 1
    conn.commit()
    return insertados

def listar_sectores_prospectables():
    """Muestra qué sectores podemos prospectar"""
    print("\n🎯 SECTORES PROSPECTABLES")
    print("  (empresas que COMPRAN leads de otros negocios)\n")
    for sector, info in MATRIZ_COMPRA.items():
        print(f"  {sector.upper():20s} → {' + '.join(info['targets'][:2])}")
        print(f"  {'':20s}   {info['por_que']}")
        print(f"  {'':20s}   Buscar: {info['compradores'][0]}")
        print()

def mostrar_resumen(conn):
    """Muestra resumen de clientes captados"""
    c = conn.cursor()
    c.execute("SELECT sector_comprador, COUNT(*) FROM clientes GROUP BY sector_comprador")
    rows = c.fetchall()
    print("\n📊 CLIENTES EN DB")
    for s, n in rows:
        pend = c.execute("SELECT COUNT(*) FROM clientes WHERE sector_comprador=? AND email_enviado=0", (s,)).fetchone()[0]
        print(f"  {s:15s} {n:3d} totales | {pend} pendientes")
    total = c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    print(f"  {'TOTAL':15s} {total:3d} empresas")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEO Campaigns Prospector")
    parser.add_argument("--buscar", help="Query de búsqueda (ej: 'seguridad privada Madrid')")
    parser.add_argument("--sector", help="Sector comprador (ej: seguridad, tpv, software)")
    parser.add_argument("--enviar", action="store_true", help="Enviar email de venta a pendientes")
    parser.add_argument("--resumen", action="store_true", help="Mostrar resumen de clientes")
    parser.add_argument("--listar", action="store_true", help="Listar sectores prospectables")
    
    args = parser.parse_args()
    
    conn = db_init()
    
    if args.listar:
        listar_sectores_prospectables()
    
    if args.buscar:
        sector = args.sector or "general"
        print(f"\n🔍 Buscando: {args.buscar}")
        empresas = buscar_empresas(args.buscar, 20)
        if empresas:
            print(f"  Encontradas: {len(empresas)}")
            for e in empresas[:10]:
                web = f" | {e['website']}" if e.get('website') else ""
                tel = f" | {e['telefono']}" if e.get('telefono') else ""
                print(f"  ✅ {e['nombre'][:40]:40s}{tel[:20]}{web[:30]}")
            
            insertados = guardar_clientes(conn, empresas, sector)
            print(f"\n  Nuevos en DB: {insertados}")
        else:
            print("  No se encontraron resultados")
    
    if args.resumen:
        mostrar_resumen(conn)
    
    if args.enviar:
        conn2 = db_init()
        c = conn2.cursor()
        c.execute("SELECT id, nombre, email FROM clientes WHERE email_enviado=0 AND email != '' LIMIT 10")
        pendientes = c.fetchall()
        
        if not pendientes:
            print("⚠️  No hay clientes pendientes de contactar en DB")
            print("   Primero usa: python3 prospector.py --buscar '...'")
        else:
            print(f"\n📧 Enviando sales pitch a {len(pendientes)} clientes...")
            print("   (Requiere Gmail conectado)")
            # Aquí iría la lógica de envío real
    
    conn.close()
