#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae emails de las webs de leads que no tienen email en la DB"""
import sqlite3, csv, os, re, urllib.request, ssl, socket, time
from urllib.parse import urlparse

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "data")
DB = os.path.join(DATA_DIR, "leads.db")

# Patrones de email en HTML
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Patrones de palabras a evitar (emails falsos)
SKIP_DOMAINS = ['example.com', 'domain.com', 'sentry.io', 'analytics', 'google.com', 'facebook.com', 'twitter.com', 'youtube.com', 'instagram.com', 'cdn.', 'tracking', 'e.ventures']

def es_email_valido(email):
    """Filtra emails basura"""
    email = email.strip().lower()
    if not email or '@' not in email:
        return False
    if any(s in email for s in ['@example', '@domain', 'noreply', 'no-reply', 'donotreply', 'sentry@', '.png', '.jpg', '.gif', '.css']):
        return False
    if any(email.endswith('.' + d) for d in ['png', 'jpg', 'gif', 'css', 'js', 'ico', 'svg', 'webp']):
        return False
    if any(d in email for d in SKIP_DOMAINS):
        return False
    if len(email) < 6 or len(email) > 100:
        return False
    if email.count('@') != 1:
        return False
    local, domain = email.split('@')
    if len(local) < 2 or len(domain) < 4:
        return False
    if not domain.startswith('http'):
        return True  # email normal
    return False

def extract_emails_from_url(url, timeout=8):
    """Abre una web y extrae emails"""
    emails = set()
    if not url or url == '':
        return emails
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        
        found = EMAIL_PATTERN.findall(html)
        for e in found:
            e = e.strip().lower()
            if es_email_valido(e):
                emails.add(e)
        
        # También buscar en mailto: links
        for match in re.finditer(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', html):
            e = match.group(1).strip().lower()
            if es_email_valido(e):
                emails.add(e)
        
    except Exception:
        pass
    
    return emails

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Leads sin email que tienen web
    c.execute("""SELECT id, nombre, web, ciudad, sector FROM leads 
                 WHERE (email IS NULL OR email = '') AND web IS NOT NULL AND web != ''
                 ORDER BY id""")
    leads = c.fetchall()
    
    print(f"🎯 {len(leads)} leads sin email pero con web")
    
    encontrados = 0
    for i, (lid, nombre, web, ciudad, sector) in enumerate(leads):
        print(f"  [{i+1}/{len(leads)}] {nombre[:30]:30s} | {web[:35]:35s}...", end=" ", flush=True)
        
        emails = extract_emails_from_url(web)
        
        if emails:
            email_principal = sorted(emails)[0]  # primer email encontrado
            c.execute("UPDATE leads SET email=? WHERE id=?", (email_principal, lid))
            conn.commit()
            encontrados += 1
            otros = ", ".join(sorted(emails)[1:3]) if len(emails) > 1 else ""
            print(f"✅ {email_principal} {otros}")
        else:
            print("❌")
        
        time.sleep(1)  # no saturar servidores
    
    conn.close()
    print(f"\n✅ Encontrados {encontrados} emails nuevos de {len(leads)} webs")

if __name__ == '__main__':
    main()
