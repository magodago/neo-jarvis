#!/usr/bin/env python3
"""
NEO EMAIL EXTRACTOR — Extrae emails de las webs de leads existentes.
Recorre los leads con web pero sin email, visita la web y extrae emails.
Actualiza la DB in-place. Sin API key, sin coste.
"""
import sqlite3, os, re, urllib.request, ssl, time
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "data", "leads.db")

# Sectores excluidos (abogados)
EXCLUIR = ["abogado", "bufete", "legal", "extranjeria", "procurador", "notaria",
           "notario", "juridico", "tribunal", "juzgado", "litigio",
           "corporativo", "fiscal", "laboralista", "penalista",
           "mercantil", "concursal", "arbitraje", "abogacia"]

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
SKIP_EMAILS = ['example.com', 'domain.com', 'noreply', 'no-reply', 'donotreply',
               '.png', '.jpg', '.gif', '.css', '.js', '.svg', '.webp',
               'google.com', 'facebook.com', 'twitter.com', 'instagram.com',
               'youtube.com', 'linkedin.com', 'tiktok.com']

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def es_excluido(sector, nombre=None):
    if sector:
        if any(e in sector.lower() for e in EXCLUIR):
            return True
    if nombre:
        if any(e in nombre.lower() for e in EXCLUIR):
            return True
    return False


def extract_email(url, timeout=8):
    """Visita una web y extrae emails reales."""
    if not url:
        return ''
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'es-ES,es;q=0.9',
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        found = EMAIL_RE.findall(html)
        # Preferir emails con dominio propio
        for e in found:
            e = e.strip().lower()
            if any(s in e for s in SKIP_EMAILS):
                continue
            if len(e) < 6 or len(e) > 80:
                continue
            if e.count('@') != 1:
                continue
            domain = e.split('@')[1]
            if domain not in ('gmail.com', 'yahoo.es', 'yahoo.com', 'hotmail.com',
                              'outlook.com', 'outlook.es'):
                return e
        # Fallback: primer email válido
        for e in found:
            e = e.strip().lower()
            if any(s in e for s in SKIP_EMAILS):
                continue
            if len(e) > 5 and '@' in e and e.count('@') == 1:
                return e
    except Exception:
        pass
    return ''


def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Leads con web pero sin email (no abogados)
    c.execute("""SELECT id, nombre, web, sector, ciudad FROM leads 
                 WHERE web IS NOT NULL AND web != '' 
                 AND (email IS NULL OR email = '' OR email = 'N/A')""")
    leads = c.fetchall()

    # Filtrar abogados
    pendientes = [l for l in leads if not es_excluido(l[3], l[1])]
    total = len(pendientes)

    print(f"🔍 Leads con web sin email (no abogados): {total}")
    print(f"   De {len(leads)} totales ({len(leads)-total} excluidos)")
    print()

    if total == 0:
        print("✅ No hay leads pendientes de extraer email.")
        conn.close()
        return

    ok = 0
    errors = 0
    start = time.time()

    for i, (lid, nombre, web, sector, ciudad) in enumerate(pendientes, 1):
        email = extract_email(web)
        if email:
            c.execute("UPDATE leads SET email=? WHERE id=?", (email, lid))
            conn.commit()
            ok += 1
            print(f"  ✅ [{i}/{total}] {email} ← {nombre[:30]}")
        else:
            errors += 1
            if i <= 3 or i % 50 == 0:
                print(f"  ➖ [{i}/{total}] {nombre[:30]:30s} — sin email en {web[:40]}")

        # Respeto: 0.5s entre sitios
        time.sleep(0.5)

        # Cada 50, mostrar progreso
        if i % 50 == 0:
            elapsed = time.time() - start
            rate = i / elapsed
            remaining = (total - i) / rate if rate > 0 else 0
            print(f"\n   📊 Progreso: {i}/{total} ({ok} emails, {errors} sin) "
                  f"— ritmo {rate:.1f} leads/s — estimado {remaining:.0f}s restantes\n")

    elapsed = time.time() - start
    print(f"\n{'='*55}")
    print(f"  📊 EXTRACCIÓN COMPLETADA")
    print(f"  Tiempo: {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"  Procesados: {total}")
    print(f"  Emails extraídos: {ok}")
    print(f"  Sin email: {errors}")
    print(f"  Tasa éxito: {100*ok//total if total else 0}%")
    print(f"{'='*55}")

    # Mostrar stats actualizadas
    c.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != '' AND email != 'N/A'")
    con_email = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads")
    total_db = c.fetchone()[0]
    print(f"\n📈 DB actualizada: {con_email}/{total_db} con email ({100*con_email//total_db}%)")
    conn.close()


if __name__ == '__main__':
    main()
