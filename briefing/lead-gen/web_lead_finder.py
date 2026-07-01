#!/usr/bin/env python3
"""
NEO Web Lead Finder — searches the web for business listings with emails.
Uses web search + direct HTTP scraping of pages that respond.
"""
import urllib.request, urllib.parse, ssl, re, csv, os, time, json, random
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

OUTPUT_DIR = '/home/dorti/neo-jarvis/briefing/lead-gen/data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

# Pages that typically list businesses with contact info
SEARCHES = [
    # Restaurants - review sites and directories
    ('gastronome.es', 'gastronome.es/dondecomer/madrid/restaurantes/'),
    ('gastronome.es bcn', 'gastronome.es/dondecomer/barcelona/restaurantes/'),
    
    # Cylex directory (usually has phone + web)
    ('cylex restaurantes', 'https://www.cylex.es/madrid/restaurantes/'),
    ('cylex abogados', 'https://www.cylex.es/madrid/abogados/'),
    ('cylex bcn', 'https://www.cylex.es/barcelona/restaurantes/'),
    ('cylex clinicas', 'https://www.cylex.es/madrid/clinicas/'),
    
    # Páginas Blancas business search
    ('pages blancas madrid', 'https://www.paginasblancas.es/buscar/restaurantes/madrid/'),
    
    # Other directories
    ('nuestrosrestaurantes', 'https://www.nuestrosrestaurantes.es/restaurantes-madrid'),
]

def fetch_url(url, max_size=500000):
    """Fetch URL content."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='replace')
        if len(html) > max_size:
            html = html[:max_size]
        return html, resp.status
    except Exception as e:
        return None, str(e)

def extract_business_ldjson(html, sector, city):
    """Extract LocalBusiness JSON-LD data."""
    businesses = []
    for match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(match.group(1))
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    btype = item.get('@type', '')
                    if isinstance(btype, list):
                        btype = btype[0] if btype else ''
                    if btype in ('LocalBusiness', 'Restaurant', 'MedicalBusiness', 'LegalService', 
                                 'BarOrPub', 'CafeOrCoffeeShop', 'FastFoodRestaurant',
                                 'HealthAndBeautyBusiness', 'AutomotiveBusiness', 'Store',
                                 'ProfessionalService'):
                        name = item.get('name', '')
                        if name:
                            email = item.get('email', '')
                            b = {
                                'nombre': name.strip(),
                                'web': item.get('url', ''),
                                'telefono': item.get('telephone', ''),
                                'email': email if '@' in str(email) else '',
                                'direccion': '',
                                'sector': sector,
                                'ciudad': city,
                            }
                            # Extract address
                            addr = item.get('address', {})
                            if isinstance(addr, dict):
                                b['direccion'] = addr.get('streetAddress', '')
                            businesses.append(b)
        except:
            pass
    return businesses

def extract_businesses_from_html(html, base_url, sector, city):
    """Extract business info from HTML using various patterns."""
    businesses = []
    seen = set()
    
    # Pattern 1: JSON-LD structured data
    ld_biz = extract_business_ldjson(html, sector, city)
    for b in ld_biz:
        key = b['nombre'] + b.get('email', '') or b.get('telefono', '')
        if key not in seen:
            seen.add(key)
            businesses.append(b)
    
    # Pattern 2: Look for mailto links with business names nearby
    mailto_pattern = re.compile(
        r'<a[^>]*href="mailto:([^"]+)"[^>]*>([^<]*)</a>'
        r'|([^<]{5,100})<a[^>]*href="mailto:([^"]+)"',
        re.I
    )
    
    for match in mailto_pattern.finditer(html):
        email = match.group(1) or match.group(4)
        context = match.group(2) or match.group(3)
        email = email.strip().split('?')[0]
        if '@' in email:
            # Try to find a business name near the email
            # Clean up context  
            context = re.sub(r'<[^>]+>', '', context).strip()
            # Look for business-ish names
            name_match = re.search(r'([A-Z][a-záéíóú]+(?:\s+[A-Z][a-záéíóú]+){1,4})', context)
            name = name_match.group(1) if name_match else context[:50]
            
            key = email
            if key not in seen:
                seen.add(key)
                businesses.append({
                    'nombre': name.strip()[:80],
                    'web': base_url,
                    'telefono': '',
                    'email': email.lower(),
                    'direccion': '',
                    'sector': sector,
                    'ciudad': city,
                })
    
    # Pattern 3: Phone numbers + web links for business discovery
    phones = set(re.findall(r'\+(?:34)?[-\s]?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3}', html))
    # Clean phones
    clean_phones = set()
    for p in phones:
        p = re.sub(r'[^\d+]', '', p)
        if len(p) >= 9:
            clean_phones.add(p)
    
    return businesses

def search_and_extract(source_name, url, sector='general', city='Madrid'):
    """Search a source URL and extract businesses."""
    print(f"  🔍 {source_name:30s} {url[:60]}...", end=' ', flush=True)
    
    html, status = fetch_url(url)
    if not html:
        print(f'❌ {status}')
        return []
    
    businesses = extract_businesses_from_html(html, url, sector, city)
    print(f'✅ {len(businesses)} leads')
    return businesses

def search_google_for_business_listings(query, sector, city, max_pages=3):
    """Search Google for business listing pages and extract from each."""
    print(f"\n  🌐 Google search: {query}")
    all_biz = []
    seen_urls = set()
    
    for page in range(max_pages):
        start = page * 10
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=es&start={start}"
        
        html, status = fetch_url(url)
        if not html:
            continue
        
        # Extract search result links
        # Google heavily obfuscates HTML, try various patterns
        links = set()
        for m in re.finditer(r'<a[^>]*href="(https?://[^"]+)"[^>]*><br>|<h3[^>]*>.*?<a[^>]*href="(https?://[^"]+)"', html):
            link = m.group(1) or m.group(2)
            if link and not any(x in link for x in ['google.com','youtube.com','facebook.com']):
                links.add(link)
        
        for link in list(links)[:5]:
            if link not in seen_urls:
                seen_urls.add(link)
                time.sleep(0.5)
                biz = search_and_extract(link.split('/')[2][:30], link, sector, city)
                all_biz.extend(biz)
    
    return all_biz

def main():
    print(f"\n{'='*60}")
    print("NEO WEB LEAD FINDER")
    print(f"{'='*60}\n")
    
    all_leads = []
    seen = set()
    
    # Phase 1: Known directory URLs
    print("📡 PHASE 1: Known directories")
    for name, url in SEARCHES:
        time.sleep(1)
        sector = 'restaurantes' if 'restaurante' in url else 'abogados' if 'abogado' in url else 'clinicas' if 'clinica' in url else 'general'
        city = 'Madrid' if 'madrid' in url.lower() else 'Barcelona' if 'bcn' in url.lower() or 'barcelona' in url.lower() else 'Madrid'
        
        businesses = search_and_extract(name, url, sector, city)
        for b in businesses:
            key = b.get('email', '') or b.get('nombre', '')
            if key and key not in seen:
                seen.add(key)
                all_leads.append(b)
    
    # Phase 2: Google search for listing pages
    print("\n📡 PHASE 2: Google searches for business listings")
    google_searches = [
        ('restaurantes en Madrid con email', 'restaurantes', 'Madrid'),
        ('abogados en Madrid email contacto', 'abogados', 'Madrid'),
        ('clínicas dentales Madrid email', 'clinicas', 'Madrid'),
        ('restaurantes Barcelona email', 'restaurantes', 'Barcelona'),
        ('listado restaurantes Madrid correo electronico', 'restaurantes', 'Madrid'),
        ('peluquerías Madrid email contacto', 'peluquerias', 'Madrid'),
    ]
    
    for query, sector, city in google_searches:
        try:
            biz = search_google_for_business_listings(query, sector, city, max_pages=2)
            for b in biz:
                key = b.get('email', '') or b.get('nombre', '')
                if key and key not in seen:
                    seen.add(key)
                    all_leads.append(b)
        except Exception as e:
            print(f"  💥 Error: {e}")
    
    # Save all
    output_file = os.path.join(OUTPUT_DIR, 'web_leads.csv')
    fieldnames = ['nombre', 'sector', 'ciudad', 'telefono', 'web', 'email', 'direccion']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for b in all_leads:
            # Ensure all fields exist
            row = {k: b.get(k, '') for k in fieldnames}
            writer.writerow(row)
    
    with_email = [b for b in all_leads if b.get('email')]
    with_web = [b for b in all_leads if b.get('web')]
    with_phone = [b for b in all_leads if b.get('telefono')]
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL: {len(all_leads)} leads")
    print(f"   Con email: {len(with_email)}")
    print(f"   Con web: {len(with_web)}")
    print(f"   Con teléfono: {len(with_phone)}")
    print(f"{'='*60}")
    
    return all_leads

if __name__ == '__main__':
    main()
