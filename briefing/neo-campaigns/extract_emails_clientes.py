#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae emails de las webs de clientes de NEO Campaigns.
Lee clientes.db, scrapea cada web y actualiza la DB.
"""
import sqlite3, os, re, time, ssl, urllib.request
from urllib.parse import urlparse, urljoin

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "clientes", "clientes.db")

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
IGNORE_DOMAINS = {
    'example.com', 'domain.com', 'tld.com', 'yoursite.com',
    'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
    'youtube.com', 'wordpress.com', 'wixsite.com', 'blogspot.com',
    'google.com', 'maps.google.com', 'gmail.com', 'hotmail.com', 'yahoo.com',
}

def es_email_valido(email):
    email = email.strip().lower()
    if not email or '@' not in email:
        return False
    if any(s in email for s in ['@example', '@domain', 'noreply', 'no-reply', 'donotreply',
                                  '.png', '.jpg', '.gif', '.css', '.js', '.ico', '.svg']):
        return False
    domain = email.split('@')[-1]
    if domain in IGNORE_DOMAINS:
        return False
    if len(email) < 6 or len(email) > 100:
        return False
    if email.count('@') != 1:
        return False
    local_part = email.split('@')[0]
    if len(local_part) < 2 or len(domain) < 4:
        return False
    return True

def fetch_url(url, timeout=10):
    """Fetch URL content."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        return None

def find_contact_pages(html, base_url):
    """Find contact/about pages."""
    keywords = re.compile(
        r'(contacto|contact|contactar|contacta|hola|info\b|sobre\s+nosotros'
        r'|quienes\s+somos|about|atencion\s+al\s+cliente|soporte|ayuda'
        r'|donde\s+estamos|ubicacion|direccion|escribenos|formulario'
        r'|presupuesto|pedir\s+presupuesto|trabaja\s+con\s+nosotros)',
        re.I
    )
    pages = set()
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html):
        url = m.group(1)
        if keywords.search(url):
            pages.add(urljoin(base_url, url))
    return list(pages)

def extract_emails_from_html(html):
    """Extract valid emails from HTML."""
    emails = set()
    for m in re.finditer(r'href=["\']mailto:([^"\']+)["\']', html, re.I):
        e = m.group(1).split('?')[0].strip()
        if es_email_valido(e):
            emails.add(e.lower())
    for m in EMAIL_RE.finditer(html):
        e = m.group(0)
        if es_email_valido(e):
            emails.add(e.lower())
    return emails

def scrape_website(web):
    """Scrape a website for emails, including contact pages."""
    if not web:
        return set()
    if not web.startswith('http'):
        web = 'https://' + web
    all_emails = set()
    html = fetch_url(web)
    if html:
        emails = extract_emails_from_html(html)
        all_emails.update(emails)
        contact_pages = find_contact_pages(html, web)
        for cp in contact_pages[:3]:
            time.sleep(0.3)
            cp_html = fetch_url(cp)
            if cp_html:
                emails2 = extract_emails_from_html(cp_html)
                all_emails.update(emails2)
    return all_emails

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Empresas sin email pero con web
    c.execute("""SELECT id, nombre, website, sector_comprador FROM clientes 
                 WHERE (email IS NULL OR email = '') AND website IS NOT NULL AND website != ''
                 ORDER BY id""")
    empresas = c.fetchall()
    
    print(f"🎯 {len(empresas)} empresas sin email pero con web\n")
    
    encontrados = 0
    for i, (eid, nombre, web, sector) in enumerate(empresas):
        # Clean URL (remove UTM params)
        web_clean = web.split('?')[0]
        print(f"  [{i+1}/{len(empresas)}] {sector:10s} | {nombre[:35]:35s}", end=" ", flush=True)
        
        emails = scrape_website(web_clean)
        
        if emails:
            # Preferir emails que contengan el dominio de la empresa
            domain = urlparse(web_clean).netloc.replace('www.', '') if web_clean else ''
            emails_ordenados = sorted(emails, key=lambda e: (0 if domain and domain.split('.')[0] in e else 1, e))
            email_principal = emails_ordenados[0]
            
            c.execute("UPDATE clientes SET email=? WHERE id=?", (email_principal, eid))
            conn.commit()
            encontrados += 1
            
            otros = ", ".join(emails_ordenados[1:3]) if len(emails_ordenados) > 1 else ""
            print(f"✅ {email_principal}")
            if otros:
                print(f"  {'':57s}   + {otros}")
        else:
            print("❌ sin email")
        
        time.sleep(0.5)
    
    conn.close()
    print(f"\n✅ Encontrados {encontrados} emails de {len(empresas)} webs")

if __name__ == '__main__':
    main()
