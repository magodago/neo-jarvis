#!/usr/bin/env python3
"""LinkedIn setup: one-time login, then saves session for automation."""
from playwright.sync_api import sync_playwright

print("="*50)
print("LINKEDIN SETUP — LOGIN UNA SOLA VEZ")
print("="*50)
print("Se va a abrir una ventana del navegador.")
print("Introduce tus credenciales de LinkedIn MANUALMENTE.")
print("Después del login, la sesión se guardará automáticamente.")
print("A partir de ahí, los posts serán automáticos.")
input("\nPresiona ENTER para continuar...")

with sync_playwright() as p:
    b = p.chromium.launch(headless=False, args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 1280, 'height': 800})
    page = ctx.new_page()
    
    page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded', timeout=30000)
    print("\n✅ Navegador abierto. LOGUÉATE MANUALMENTE en LinkedIn.")
    print("   Cuando termines, vuelve aquí y presiona ENTER...")
    input("   (Esperando a que termines el login...)")
    
    page.wait_for_timeout(3000)
    current_url = page.url
    print(f"\nURL actual: {current_url[:60]}")
    
    if 'feed' in current_url:
        print("✅ Login detectado! Guardando cookies...")
        import json
        from pathlib import Path
        
        cookies = ctx.cookies()
        cookie_file = Path.home() / ".hermes" / "linkedin_cookies.json"
        cookie_file.write_text(json.dumps(cookies, indent=2))
        print(f"Cookies guardadas en {cookie_file}")
        
        # Also save local storage
        storage = page.context.storage_state()
        storage_file = Path.home() / ".hermes" / "linkedin_storage.json"
        storage_file.write_text(json.dumps(storage, indent=2))
        print(f"Storage guardado en {storage_file}")
        
        print("\n✅ SETUP COMPLETO. A partir de ahora los posts serán automáticos.")
    else:
        print("❌ No se detectó login. La URL no contiene /feed/")
    
    ctx.close()
    b.close()
