#!/usr/bin/env python3
"""Extract emails from websites of existing leads that have web but no email."""
import csv, re, time, json, sys
from urllib.parse import urlparse, urljoin
import urllib.request
import urllib.error
import ssl

DATA = 'data/leads.csv'
OUT = 'data/leads_updated.csv'

# Regex for emails
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
# Ignore these domains
IGNORE_DOMAINS = {
    'example.com', 'domain.com', 'tld.com', 'yoursite.com',
    'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
    'youtube.com', 'wordpress.com', 'wixsite.com', 'blogspot.com',
    'google.com', 'maps.google.com',
}

def is_valid_email(e):
    e = e.strip().lower()
    if not e:
        return False
    domain = e.split('@')[-1] if '@' in e else ''
    if domain in IGNORE_DOMAINS:
        return False
    if any(c in e for c in ' _+,;:'):
        return False
    if not domain or '.' not in domain:
        return False
    return True

def fetch_url(url, timeout=10):
    """Fetch URL content with basic headers."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            return html
    except Exception as e:
        return None

def extract_emails_from_html(html, base_url):
    """Extract emails from HTML content."""
    emails = set()
    # Direct mailto: links
    for m in re.finditer(r'href=["\']mailto:([^"\']+)["\']', html, re.I):
        e = m.group(1).split('?')[0].strip()
        if is_valid_email(e):
            emails.add(e.lower())
    # Email patterns in text
    for m in EMAIL_RE.finditer(html):
        e = m.group(0)
        if is_valid_email(e):
            emails.add(e.lower())
    return emails

def find_contact_pages(html, base_url):
    """Find contact/sobre-nosotros pages from the homepage."""
    contact_keywords = re.compile(
        r'(contacto|contact|contactar|contacta|hola|info\b|sobre\s+nosotros'
        r'|quienes\s+somos|about|atencion\s+al\s+cliente|soporte|ayuda'
        r'|donde\s+estamos|ubicacion|direccion|escribenos|formulario'
        r'|presupuesto|pedir\s+presupuesto|trabaja\s+con\s+nosotros)',
        re.I
    )
    pages = set()
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html):
        url = m.group(1)
        if contact_keywords.search(url):
            pages.add(urljoin(base_url, url))
    return list(pages)

def scrape_lead(row):
    """Scrape one lead's website for emails."""
    web = row.get('web', '').strip()
    if not web:
        return None
    
    # Normalize URL
    if not web.startswith('http'):
        web = 'https://' + web
    
    print(f"  Scrapeando: {row['nombre']} -> {web}")
    
    all_emails = set()
    
    # 1. Fetch homepage
    html = fetch_url(web)
    if html:
        emails = extract_emails_from_html(html, web)
        all_emails.update(emails)
        
        # 2. Find and fetch contact pages
        contact_pages = find_contact_pages(html, web)
        for cp in contact_pages[:3]:  # Max 3 contact pages
            time.sleep(0.3)
            cp_html = fetch_url(cp)
            if cp_html:
                cp_emails = extract_emails_from_html(cp_html, cp)
                all_emails.update(cp_emails)
    
    # Filter out common non-business emails
    filtered = set()
    for e in all_emails:
        local = e.split('@')[0].lower()
        domain = e.split('@')[1].lower()
        # Skip generic provider domains that aren't the business
        if domain in ('gmail.com', 'yahoo.es', 'yahoo.com', 'hotmail.com', 'outlook.com', 'msn.com'):
            continue
        # Skip noreply, admin, etc unless they're the only option
        if local in ('noreply', 'no-reply', 'donotreply', 'admin', 'webmaster', 'hostmaster'):
            continue
        filtered.add(e)
    
    if not filtered:
        filtered = all_emails  # fallback to all if nothing survived filter
    
    return list(filtered)

def main():
    # Read leads
    with open(DATA, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    total = len(leads)
    found = 0
    new_emails = 0
    
    print(f"=== EXTRAYENDO EMAILS DE {total} LEADS ===\n")
    
    for i, lead in enumerate(leads):
        existing = lead.get('email', '').strip()
        if existing:
            print(f"  [{i+1}/{total}] {lead['nombre']} -> ya tiene email: {existing}")
            continue
        
        web = lead.get('web', '').strip()
        tlf = lead.get('telefono', '').strip()
        
        if not web:
            print(f"  [{i+1}/{total}] {lead['nombre']} -> sin web ni email, saltando")
            continue
        
        emails = scrape_lead(lead)
        if emails:
            lead['email'] = emails[0]
            new_emails += 1
            found += 1
            print(f"    ✅ ENCONTRADO: {emails[0]}")
            if len(emails) > 1:
                print(f"    📎 También: {', '.join(emails[1:])}")
        else:
            print(f"    ❌ No se encontró email")
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n=== RESUMEN ===")
    print(f"Total leads: {total}")
    print(f"Nuevos emails encontrados: {new_emails}")
    print(f"Leads con email ahora: {len([l for l in leads if l.get('email','').strip()])}")
    
    # Save updated CSV
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(leads)
    
    print(f"\nGuardado en: {OUT}")
    
    # Show leads that still have no email and no web
    stuck = [l for l in leads if not l.get('email','').strip() and not l.get('web','').strip()]
    print(f"\nLeads sin email ni web (necesitan nueva fuente): {len(stuck)}")

if __name__ == '__main__':
    main()
