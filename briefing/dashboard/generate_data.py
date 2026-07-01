#!/usr/bin/env python3
"""Generate leads_data.json for the NEO Leads Dashboard - reads from tracking DB."""
import json, os, datetime
import sqlite3

DB_PATH = '/home/dorti/neo-jarvis/briefing/lead-gen/data/leads.db'
OUTPUT = '/home/dorti/neo-jarvis/briefing/dashboard/leads_data.json'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
with_email = conn.execute("SELECT COUNT(*) FROM leads WHERE email != ''").fetchone()[0]
sent = conn.execute("SELECT COUNT(*) FROM leads WHERE email_enviado=1").fetchone()[0]
bounced = conn.execute("SELECT COUNT(*) FROM leads WHERE reboto=1").fetchone()[0]
replied = conn.execute("SELECT COUNT(*) FROM leads WHERE respondio=1").fetchone()[0]
pending = total - sent

# Sectors
sector_rows = conn.execute("SELECT sector, COUNT(*) as cnt FROM leads GROUP BY sector ORDER BY cnt DESC").fetchall()
sectors = [{'name': r['sector'], 'count': r['cnt']} for r in sector_rows]

# Cities
city_rows = conn.execute("SELECT ciudad, COUNT(*) as cnt FROM leads WHERE ciudad != '' GROUP BY ciudad ORDER BY cnt DESC LIMIT 10").fetchall()
cities = [{'name': r['ciudad'], 'count': r['cnt']} for r in city_rows]

# Timeline
timeline = conn.execute("SELECT date(fecha_envio) as d, COUNT(*) as c FROM leads WHERE fecha_envio IS NOT NULL GROUP BY d ORDER BY d").fetchall()
timeline_data = [{'date': r['d'], 'count': r['c']} for r in timeline]

# Recent leads
recent_rows = conn.execute("""SELECT nombre, sector, ciudad, email, email_enviado, 
    CASE WHEN respondio=1 THEN 'replied' WHEN reboto=1 THEN 'bounced' WHEN email_enviado=1 THEN 'sent' ELSE 'pending' END as estado,
    fecha_envio FROM leads ORDER BY id DESC LIMIT 20""").fetchall()

recent = []
for r in recent_rows:
    recent.append({
        'nombre': r['nombre'] or '',
        'sector': r['sector'] or '',
        'ciudad': r['ciudad'] or '',
        'email': r['email'] or '',
        'estado': r['estado'],
        'fecha': (r['fecha_envio'] or '')[:10],
    })

data = {
    'total': total,
    'with_email': with_email,
    'sent': sent,
    'bounced': bounced,
    'replied': replied,
    'pending': pending,
    'sectors': sectors,
    'cities': cities,
    'timeline': timeline_data,
    'recent': recent,
    'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}

conn.close()

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Dashboard data generated: {OUTPUT}")
print(f"   Total: {total} | Con email: {with_email} | Enviados: {sent} | Rebotados: {bounced} | Respondidos: {replied}")
