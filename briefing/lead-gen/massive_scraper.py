#!/usr/bin/env python3
"""
Massive Google Maps lead scraper.
Scrapes Google Maps business listings for: restaurants, clinics, lawyers, etc.
in Madrid, Barcelona, Málaga, and other cities.
Outputs to leads CSV with website, phone — then email scraper finds the emails.
"""

import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
import re
import time
import csv
import os
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== CONFIG =====
CITIES = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Málaga',
    'Bilbao', 'Zaragoza', 'Murcia', 'Palma', 'Alicante',
    'Las Palmas', 'Granada', 'Vigo', 'Gijón', 'Donostia-San Sebastián',
]

SECTORS = {
    'restaurantes': 'restaurante',
    'clinicas': 'clinica+dental+medica',
    'abogados': 'abogado+despacho',
}

# Subtle user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
]

OUTPUT_DIR = '/home/dorti/neo-jarvis/briefing/lead-gen/data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_web_for_businesses(sector, city, page=0):
    """Search Google for business directories/listings with emails."""
    queries = [
        f'{sector} en {city} email contacto',
        f'{sector} {city} info@ correo electrónico',
        f'directorio {sector} {city} email',
        f'lista {sector} {city} teléfono email',
    ]
    
    query = queries[page % len(queries)]
    url = f'https://www.google.com/search?q={urllib.parse.quote(query)}&hl=es&num=20'
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='replace')
        
        # Extract business names and websites from search results
        businesses = []
        
        # Google result links
        for m in re.finditer(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.I):
            link = m.group(1)
            title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if title and len(title) > 3 and not any(x in link for x in ['google.com', 'youtube.com', 'facebook.com', 'instagram.com']):
                businesses.append({'nombre': title[:80], 'web': link, 'sector': sector.replace('+', ' ').split()[0], 'ciudad': city})
        
        # Also try to extract local business results
        local_bizs = re.findall(r'data-dtld="([^"]*)"[^>]*>([^<]+)<', html)
        
        return businesses
    except Exception as e:
        return []

def extract_business_from_webpage(url, sector, city):
    """Visit a page and extract business information."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8', errors='replace')
        
        businesses = []
        
        # Look for structured business data (JSON-LD)
        for ld_match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
            try:
                data = json.loads(ld_match.group(1))
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') in ('LocalBusiness', 'Restaurant', 'MedicalBusiness', 'LegalService'):
                            b = {
                                'nombre': item.get('name', ''),
                                'web': url,
                                'telefono': item.get('telephone', ''),
                                'email': item.get('email', ''),
                                'direccion': item.get('address', {}).get('streetAddress', '') if isinstance(item.get('address'), dict) else '',
                                'sector': sector,
                                'ciudad': city,
                            }
                            if b['nombre']:
                                businesses.append(b)
                elif isinstance(data, dict):
                    if data.get('@type') in ('LocalBusiness', 'Restaurant', 'MedicalBusiness', 'LegalService'):
                        b = {
                            'nombre': data.get('name', ''),
                            'web': url,
                            'telefono': data.get('telephone', ''),
                            'email': data.get('email', ''),
                            'direccion': data.get('address', {}).get('streetAddress', '') if isinstance(data.get('address'), dict) else '',
                            'sector': sector,
                            'ciudad': city,
                        }
                        if b['nombre']:
                            businesses.append(b)
            except:
                pass
        
        # If no JSON-LD, try to extract from page content
        if not businesses:
            # Look for common patterns
            emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
            emails = {e for e in emails if not any(d in e for d in ['.png', '.jpg', '.css', '.js', 'example', 'sentry', 'wixpress'])}
            
            phones = set()
            for phone_match in re.finditer(r'\+?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3}', html):
                phones.add(phone_match.group(0))
            
            # Try to find the business name from the page
            title_match = re.search(r'<title>([^<]+)</title>', html, re.I)
            nombre = title_match.group(1).strip() if title_match else url.split('//')[1].split('/')[0] if '//' in url else url
            
            # Clean title
            for suffix in [' | ', ' - ', ' • ']:
                if suffix in nombre:
                    nombre = nombre.split(suffix)[0]
            
            if emails:
                for email in list(emails)[:1]:
                    businesses.append({
                        'nombre': nombre[:80],
                        'web': url,
                        'telefono': list(phones)[0] if phones else '',
                        'email': email,
                        'direccion': '',
                        'sector': sector,
                        'ciudad': city,
                    })
        
        return businesses
    except Exception as e:
        return []

def scrape_directory_page(url, sector, city):
    """Scrape a business directory/listing page for multiple businesses."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='replace')
        
        businesses = []
        
        # Extract all JSON-LD blocks (many directories embed multiple)
        for ld_match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
            try:
                data = json.loads(ld_match.group(1))
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get('@type') in ('LocalBusiness', 'Restaurant', 'MedicalBusiness', 'LegalService', 'ItemList'):
                        if item.get('@type') == 'ItemList' and 'itemListElement' in item:
                            for element in item['itemListElement']:
                                if isinstance(element, dict):
                                    biz = element.get('item', element)
                                    if isinstance(biz, dict):
                                        b = {
                                            'nombre': biz.get('name', ''),
                                            'web': biz.get('url', ''),
                                            'telefono': biz.get('telephone', ''),
                                            'email': biz.get('email', ''),
                                            'direccion': biz.get('address', {}).get('streetAddress', '') if isinstance(biz.get('address'), dict) else '',
                                            'sector': sector,
                                            'ciudad': city,
                                        }
                                        if b['nombre']:
                                            businesses.append(b)
                        elif item.get('name'):
                            b = {
                                'nombre': item.get('name', ''),
                                'web': item.get('url', ''),
                                'telefono': item.get('telephone', ''),
                                'email': item.get('email', ''),
                                'direccion': item.get('address', {}).get('streetAddress', '') if isinstance(item.get('address'), dict) else '',
                                'sector': sector,
                                'ciudad': city,
                            }
                            if b['nombre']:
                                businesses.append(b)
            except:
                pass
        
        return businesses
    except:
        return []

def run_search():
    """Main search function - searches Google for business listings and extracts them."""
    all_businesses = []
    seen = set()
    
    print("=" * 60)
    print("NEO MASSIVE LEAD SCRAPER")
    print("=" * 60)
    
    # Phase 1: Search Google for business directory pages
    print("\n📡 PHASE 1: Searching for business directories...")
    search_tasks = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        for city in CITIES[:5]:  # Top 5 cities first
            for sector_name, sector_query in SECTORS.items():
                for page in range(3):  # 3 search queries per sector/city
                    search_tasks.append(
                        executor.submit(search_web_for_businesses, sector_query, city, page)
                    )
        
        for future in as_completed(search_tasks):
            results = future.result()
            for biz in results:
                key = biz.get('web', biz.get('nombre', ''))
                if key and key not in seen:
                    seen.add(key)
                    all_businesses.append(biz)
    
    print(f"  Found {len(all_businesses)} potential leads from search results")
    
    # Phase 2: Visit each unique webpage to extract structured data
    print("\n🔍 PHASE 2: Extracting business data from pages...")
    unique_urls = {}
    for biz in all_businesses:
        url = biz.get('web', '')
        if url and url not in unique_urls:
            unique_urls[url] = biz
    
    extracted = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for url, biz_info in list(unique_urls.items())[:50]:  # Limit to 50 pages
            sector = biz_info.get('sector', 'general')
            city = biz_info.get('ciudad', '')
            futures[executor.submit(extract_business_from_webpage, url, sector, city)] = url
        
        for future in as_completed(futures):
            results = future.result()
            if results:
                for r in results:
                    key = r.get('nombre', '') + r.get('email', '')
                    if key and key not in seen:
                        seen.add(key)
                        extracted.append(r)
    
    print(f"  Extracted {len(extracted)} businesses with contact info")
    
    # Phase 3: Also try directory pages
    print("\n📋 PHASE 3: Trying directory pages...")
    directory_urls = [
        f'https://www.empresite.es/buscar/{sector.replace("+","-")}/{city}/' 
        for city in CITIES[:3]
        for sector in SECTORS.values()
    ]
    
    for url in directory_urls[:5]:
        time.sleep(0.5)
        results = scrape_directory_page(url, 'general', '')
        for r in results:
            key = r.get('nombre', '') + r.get('email', '')
            if key and key not in seen:
                seen.add(key)
                extracted.append(r)
    
    # Save results
    output_file = os.path.join(OUTPUT_DIR, 'massive_leads.csv')
    fieldnames = ['nombre', 'sector', 'ciudad', 'telefono', 'web', 'email', 'direccion']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extracted)
    
    print(f"\n✅ Saved {len(extracted)} leads to {output_file}")
    
    # Show email stats
    with_email = [b for b in extracted if b.get('email')]
    with_web = [b for b in extracted if b.get('web')]
    with_phone = [b for b in extracted if b.get('telefono')]
    
    print(f"\n📊 EXTRACTION STATS:")
    print(f"  Total leads: {len(extracted)}")
    print(f"  With email: {len(with_email)}")
    print(f"  With website: {len(with_web)}")
    print(f"  With phone: {len(with_phone)}")
    
    return extracted

if __name__ == '__main__':
    run_search()
