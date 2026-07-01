#!/usr/bin/env python3
"""Generate leads_data.json for the NEO Leads Dashboard."""
import csv, json, os, datetime
from collections import Counter

DATA_FILE = '/home/dorti/neo-jarvis/briefing/lead-gen/data/leads_updated.csv'
DB_PATH = '/home/dorti/neo-jarvis/briefing/lead-gen/data/leads.db'
OUTPUT = '/home/dorti/neo-jarvis/briefing/dashboard/leads_data.json'

# Read CSV
with open(DATA_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    leads = list(reader)

total = len(leads)
with_email = [l for l in leads if l.get('email', '').strip()]
sent = [l for l in leads if l.get('enviado', '0') == '1']
bounced = [l for l in leads if l.get('estado_envio', '') == 'bounced']
replied = [l for l in leads if l.get('respondido', '0') == '1']

# Sectors
sector_counts = Counter(l['sector'] for l in leads)
sectors = [{'name': s, 'count': c} for s, c in sector_counts.most_common()]

# Cities
city_counts = Counter(l['ciudad'] for l in leads)
cities = [{'name': c, 'count': n} for c, n in city_counts.most_common(10)]

# Timeline - try to read from DB
timeline = []
try:
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('SELECT date(fecha_envio) as d, count(*) as c FROM leads WHERE fecha_envio IS NOT NULL GROUP BY d ORDER BY d')
    timeline = [{'date': r[0], 'count': r[1]} for r in cur.fetchall()]
    conn.close()
except:
    pass

# Recent leads
recent = []
for l in leads[-20:]:
    estado = 'pending'
    if l.get('respondido', '0') == '1':
        estado = 'replied'
    elif l.get('enviado', '0') == '1':
        if l.get('estado_envio', '') == 'bounced':
            estado = 'bounced'
        else:
            estado = 'sent'
    recent.append({
        'nombre': l.get('nombre', ''),
        'sector': l.get('sector', ''),
        'ciudad': l.get('ciudad', ''),
        'email': l.get('email', ''),
        'estado': estado,
        'fecha': l.get('fecha_envio', '')[:10] if l.get('fecha_envio') else '',
    })

data = {
    'total': total,
    'with_email': len(with_email),
    'sent': len(sent),
    'bounced': len(bounced),
    'replied': len(replied),
    'pending': total - len(sent),
    'sectors': sectors,
    'cities': cities,
    'timeline': timeline,
    'recent': recent,
    'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Dashboard data generated: {OUTPUT}")
print(f"   Total: {total} | Con email: {len(with_email)} | Enviados: {len(sent)} | Rebotados: {len(bounced)} | Respondidos: {len(replied)}")
