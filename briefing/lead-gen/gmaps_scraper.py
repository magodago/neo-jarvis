#!/usr/bin/env python3
"""
NEO Massive Lead Generator — Playwright + Google Maps
Scrapes Google Maps for business listings with phone and website,
then extracts emails from each website.
"""
import sys, os, csv, re, json, time, random
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urljoin
import urllib.request, ssl

OUTPUT_DIR = '/home/dorti/neo-jarvis/briefing/lead-gen/data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SECTORS_CITIES = [
    # Sector queries for Google Maps
    ("restaurantes", "Madrid"),
    ("restaurantes", "Barcelona"),
    ("restaurantes", "Valencia"),
    ("restaurantes", "Sevilla"),
    ("restaurantes", "Málaga"),
    ("abogados", "Madrid"),
    ("abogados", "Barcelona"),
    ("abogados", "Valencia"),
    ("clínicas+dentales", "Madrid"),
    ("clínicas+dentales", "Barcelona"),
    ("peluquerías", "Madrid"),
    ("talleres+mecánicos", "Madrid"),
]

def extract_emails_from_url(url):
    """Visit a URL and extract email addresses."""
    if not url or 'google.com' in url:
        return []
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'es-ES,es;q=0.9',
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8', errors='replace')
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
        # Filter out junk
        emails = {e for e in emails if not any(x in e.lower() for x in 
            ['png','jpg','gif','css','js','sentry','wixpress','example','.svg','google','facebook','twitter','instagram','noreply','sentry'])}
        # Prefer business emails
        biz_emails = [e for e in emails if not e.split('@')[1] in 
            ('gmail.com','yahoo.es','yahoo.com','hotmail.com','outlook.com','msn.com')]
        return biz_emails if biz_emails else list(emails)
    except:
        return []

def scrape_maps_listings(browser, query, city, max_results=100):
    """Scrape Google Maps listings for a specific query + city."""
    search = f"{query} en {city}"
    url = f"https://www.google.com/maps/search/{search.replace(' ', '+')}/"
    
    page = browser.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    leads = []
    seen_names = set()
    
    try:
        print(f"  📍 Navigando a: {search}")
        page.goto(url, timeout=60000, wait_until='networkidle')
        time.sleep(3)
        
        # Find the results panel
        # Google Maps loads results in a scrollable panel on the left
        scrollable = page.locator('div[role="feed"]')
        
        if scrollable.count() == 0:
            # Try alternative selectors
            scrollable = page.locator('div.m6QErb')
        
        if scrollable.count() == 0:
            # Try the main results container
            scrollable = page.locator('div[aria-label*="Resultados"]')
        
        print(f"  📜 Panel encontrado: {scrollable.count() > 0}")
        
        # Scroll to load more results
        prev_count = 0
        scroll_attempts = 0
        while len(leads) < max_results and scroll_attempts < 30:
            scroll_attempts += 1
            
            # Get all result items
            items = page.locator('a[aria-label]')
            count = items.count()
            
            if count > prev_count:
                for i in range(prev_count, count):
                    try:
                        aria_label = items.nth(i).get_attribute('aria-label') or ''
                        href = items.nth(i).get_attribute('href') or ''
                        
                        # Parse the aria-label for business info
                        # Format: "Nombre · 4.5 ★ · 123 reseñas · info"
                        parts = aria_label.split('·')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            if name and name not in seen_names and len(name) > 2:
                                seen_names.add(name)
                                leads.append({
                                    'nombre': name,
                                    'maps_link': href,
                                    'sector': query,
                                    'ciudad': city,
                                })
                    except:
                        pass
                
                prev_count = count
                print(f"  📊 Encontrados {len(leads)} resultados...")
            
            # Scroll
            try:
                scrollable.first.evaluate("el => el.scrollTop = el.scrollHeight")
            except:
                page.evaluate("window.scrollBy(0, 500)")
            
            time.sleep(1.5)
        
        print(f"  ✅ {len(leads)} leads encontrados para {search}")
        
        # Click on each lead to get detailed info
        print(f"  🔍 Extrayendo detalles...")
        for idx, lead in enumerate(leads):
            try:
                # Click on the result
                items = page.locator('a[aria-label]')
                items.nth(idx).click()
                time.sleep(1.5)
                
                # Wait for details panel
                page.wait_for_selector('div[role="main"]', timeout=5000)
                
                # Extract phone
                phone_selectors = [
                    'button[data-tooltip*="teléfono"]',
                    'button[aria-label*="teléfono"]',
                    'button[data-item-id*="phone"]',
                    'span[aria-label*="teléfono"]',
                ]
                for sel in phone_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.count():
                            phone = btn.get_attribute('aria-label') or btn.text_content()
                            lead['telefono'] = phone.replace('Teléfono:', '').replace('teléfono:', '').strip()
                            break
                    except:
                        pass
                
                # Extract website
                web_selectors = [
                    'a[data-tooltip*="sitio web"]',
                    'a[aria-label*="Sitio web"]',
                    'a[aria-label*="website"]',
                    'a[data-item-id*="authority"]',
                ]
                for sel in web_selectors:
                    try:
                        lnk = page.locator(sel).first
                        if lnk.count():
                            lead['web'] = lnk.get_attribute('href')
                            break
                    except:
                        pass
                
                # Extract address
                addr_selectors = [
                    'button[data-tooltip*="dirección"]',
                    'button[aria-label*="dirección"]',
                    'span[aria-label*="dirección"]',
                ]
                for sel in addr_selectors:
                    try:
                        addr = page.locator(sel).first
                        if addr.count():
                            lead['direccion'] = addr.get_attribute('aria-label') or addr.text_content()
                            break
                    except:
                        pass
                
                # Extract email from website
                if lead.get('web') and not lead.get('email'):
                    try:
                        emails = extract_emails_from_url(lead['web'])
                        if emails:
                            lead['email'] = emails[0]
                            print(f"    ✅ Email: {emails[0]}")
                    except:
                        pass
                
            except Exception as e:
                pass
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    finally:
        page.close()
    
    return [l for l in leads if l.get('telefono') or l.get('email') or l.get('web')]

def save_leads(all_leads):
    """Save leads to CSV."""
    output_file = os.path.join(OUTPUT_DIR, 'google_maps_leads.csv')
    fieldnames = ['nombre', 'sector', 'ciudad', 'telefono', 'web', 'email', 'direccion', 'maps_link']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_leads)
    
    with_email = [l for l in all_leads if l.get('email')]
    with_web = [l for l in all_leads if l.get('web')]
    with_phone = [l for l in all_leads if l.get('telefono')]
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL: {len(all_leads)} leads")
    print(f"   Con teléfono: {len(with_phone)}")
    print(f"   Con web: {len(with_web)}")
    print(f"   Con email: {len(with_email)}")
    print(f"   Guardado en: {output_file}")
    print(f"{'='*60}")

def main():
    print(f"\n{'='*60}")
    print("NEO MASSIVE LEAD GENERATOR — GOOGLE MAPS")
    print(f"{'='*60}\n")
    
    all_leads = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        for sector, city in SECTORS_CITIES:
            try:
                leads = scrape_maps_listings(browser, sector, city, max_results=60)
                all_leads.extend(leads)
                print()
            except Exception as e:
                print(f"  💥 Error en {sector}/{city}: {e}\n")
        
        browser.close()
    
    save_leads(all_leads)

if __name__ == '__main__':
    main()
