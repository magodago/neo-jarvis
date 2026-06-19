#!/usr/bin/env python3
"""LinkedIn setup v3 — login en perfil persistente (se reutiliza siempre)."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json, time

PROFILE_DIR = Path.home() / ".hermes" / "linkedin_profile"

print("="*60)
print("  LINKEDIN SETUP v3 — LOGIN EN PERFIL PERSISTENTE")
print("="*60)
print()
print("Esto abre LinkedIn en un perfil Chromium que REUTILIZARÉ siempre.")
print("El fingerprint del navegador será idéntico cada vez.")
print()
print("1. Se abrirá Chromium")
print("2. LOGUÉATE en LinkedIn")
print("3. Cuando veas tu FEED, pulsa ENTER aquí")
print()

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled'],
        viewport={'width': 1280, 'height': 800},
        locale='es-ES',
    )
    
    page = ctx.new_page()
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        window.chrome = { runtime: {} };
    """)
    
    page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded', timeout=30000)
    print("✅ Navegador abierto. LOGUÉATE en LinkedIn y ve a tu feed.")
    print("   Cuando veas tu feed, pulsa ENTER aquí.")
    
    input("   🔵 Pulsa ENTER cuando estés en tu feed...\n")
    
    # Save cookies from this persistent context
    cookies = ctx.cookies()
    storage = ctx.storage_state()
    
    storage_file = Path.home() / ".hermes" / "linkedin_storage.json"
    storage_file.write_text(json.dumps(storage, indent=2))
    
    print(f"✅ Estado guardado: {len(cookies)} cookies")
    print(f"✅ Perfil persistente en: {PROFILE_DIR}")
    
    li_at = any(c.get("name") == "li_at" for c in cookies)
    jsession = any(c.get("name") == "JSESSIONID" for c in cookies)
    print(f"   li_at: {'✅' if li_at else '❌'} | JSESSIONID: {'✅' if jsession else '❌'}")
    
    if li_at and jsession:
        print("\n🎉 SETUP COMPLETO. Ahora los posts funcionarán automáticamente.")
    
    input("\nPulsa ENTER para cerrar el navegador...\n")
    ctx.close()
