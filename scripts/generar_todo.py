#!/usr/bin/env python3
"""Genera todas las páginas de los 5 nichos restantes."""
import sys, os, random
sys.path.insert(0, '/home/dorti/neo-jarvis')
from programmatic_seo_v2 import build_html, slugify, BLOG, NICHE_DIR

# Importar los datos del script de contenido
# (ejecutamos inline para no crear dependencias de módulo)
exec(open('/home/dorti/neo-jarvis/generar_contenido.py').read())

ALL_NICHES = {
    "productividad": {"slug":"productividad","name":"Productividad","brand":"#d4a853","brand_dark":"#b8922f","payhip":"EYojF"},
    "finanzas": {"slug":"finanzas","name":"Finanzas","brand":"#66bb6a","brand_dark":"#388e3c","payhip":"uP62G"},
    "marketing": {"slug":"marketing","name":"Marketing","brand":"#42a5f5","brand_dark":"#1976d2","payhip":"Q5RYA"},
    "estudiantes": {"slug":"estudiantes","name":"Estudiantes","brand":"#ffa726","brand_dark":"#ef6c00","payhip":"M3eqn"},
    "rrhh": {"slug":"rrhh","name":"RRHH","brand":"#ec407a","brand_dark":"#c2185b","payhip":"KragB"},
}

PAGES = {
    "productividad": PRODUCTIVIDAD,
    "finanzas": FINANZAS,
    "marketing": MARKETING,
    "estudiantes": ESTUDIANTES,
    "rrhh": RRHH,
}

total_generated = 0
total_skipped = 0

for slug_niche, pages in PAGES.items():
    niche = ALL_NICHES[slug_niche]
    niche_dir = BLOG / slug_niche
    niche_dir.mkdir(parents=True, exist_ok=True)
    
    for data in pages:
        slug = slugify(data["kw"])
        filepath = niche_dir / f"{slug}.html"
        
        if filepath.exists():
            total_skipped += 1
            continue
        
        html = build_html(data, niche)
        with open(filepath, "w") as f:
            f.write(html)
        total_generated += 1
        print(f"  ✅ {slug_niche}/{slug}.html ({len(html)} bytes)")

print(f"\n{'='*60}")
print(f"✅ GENERADAS: {total_generated}  |  YA EXISTIAN: {total_skipped}")
print(f"📁 Total: {total_generated + total_skipped} páginas")
print(f"{'='*60}")
