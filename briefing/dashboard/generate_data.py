#!/usr/bin/env python3
"""Genera datos JSON para el dashboard NEO Leads - claves en ingles para JS"""
import sqlite3, json, os, datetime, sys

DB_PATH = '/home/dorti/neo-jarvis/briefing/lead-gen/data/leads.db'
OUTPUT_DIRS = [
    '/home/dorti/neo-jarvis/landing',
    '/home/dorti/neo-jarvis',
]

def generate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now = datetime.datetime.now()
    
    cur.execute("SELECT COUNT(*) FROM leads")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''")
    con_email = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE telefono IS NOT NULL AND telefono != ''")
    con_telf = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE web IS NOT NULL AND web != ''")
    con_web = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE email_enviado = 1")
    enviados = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE reboto = 1")
    rebotados = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE respondio = 1")
    respondidos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM leads WHERE email != '' AND email_enviado = 0")
    pendientes_envio = cur.fetchone()[0]
    
    # By sector
    cur.execute("""SELECT sector, COUNT(*) as total,
        SUM(CASE WHEN email != '' THEN 1 ELSE 0 END) as con_email,
        SUM(CASE WHEN email_enviado = 1 THEN 1 ELSE 0 END) as enviados
        FROM leads GROUP BY sector ORDER BY total DESC""")
    sectores = []
    for r in cur.fetchall():
        s = dict(r)
        # Add bounce/reply cols
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM leads WHERE sector=? AND reboto=1", (s['sector'],))
        s['rebotes'] = cur2.fetchone()[0]
        cur2.execute("SELECT COUNT(*) FROM leads WHERE sector=? AND respondio=1", (s['sector'],))
        s['respuestas'] = cur2.fetchone()[0]
        sectores.append(s)
    
    # Timeline
    cur.execute("""SELECT DATE(created_at) as dia, COUNT(*) as nuevos
        FROM leads WHERE created_at IS NOT NULL GROUP BY dia ORDER BY dia""")
    timeline = [dict(r) for r in cur.fetchall()]
    
    # Send timeline
    cur.execute("""SELECT DATE(fecha_envio) as dia, COUNT(*) as enviados
        FROM leads WHERE fecha_envio IS NOT NULL GROUP BY dia ORDER BY dia""")
    timeline_envio = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    
    data = {
        "timestamp": now.strftime('%Y-%m-%d %H:%M UTC'),
        "stats": {
            "total": total,
            "con_email": con_email,
            "con_telefono": con_telf,
            "con_web": con_web,
            "sent": enviados,
            "bounce": rebotados,
            "reply": respondidos,
            "pending": pendientes_envio,
            "tasa_respuesta": round(respondidos / max(enviados, 1) * 100, 1),
        },
        "sectors": [
            {"sector": s['sector'], "total": s['total'], "sent": s['enviados'], "bounces": s['rebotes'], "replies": s['respuestas']}
            for s in sectores
        ],
        "timeline_scrapeo": timeline,
        "timeline_envio": timeline_envio,
    }
    
    for out in OUTPUT_DIRS:
        os.makedirs(out, exist_ok=True)
        path = os.path.join(out, 'data.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(json.dumps({"status": "ok", "leads": total, "sent": enviados}))

if __name__ == '__main__':
    generate()
