#!/usr/bin/env python3
"""Tracking DB para pipeline de captacion NEO"""
import sqlite3, csv, os, json, datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "leads.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT DEFAULT '',
        telefono TEXT DEFAULT '',
        web TEXT DEFAULT '',
        direccion TEXT DEFAULT '',
        sector TEXT DEFAULT '',
        ciudad TEXT DEFAULT '',
        asunto_email TEXT DEFAULT '',
        email_enviado INTEGER DEFAULT 0,
        fecha_envio TEXT,
        message_id TEXT DEFAULT '',
        estado TEXT DEFAULT 'pendiente',
        reboto INTEGER DEFAULT 0,
        respondio INTEGER DEFAULT 0,
        fecha_respuesta TEXT,
        notas TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.commit()
    return conn

def import_csv(csv_path):
    conn = get_db()
    cur = conn.cursor()
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""INSERT OR IGNORE INTO leads
                (nombre, email, telefono, web, direccion, sector, ciudad)
                VALUES (?,?,?,?,?,?,?)""",
                (row.get('nombre',''), row.get('email',''), row.get('telefono',''),
                 row.get('web',''), row.get('direccion',''), row.get('sector',''), row.get('ciudad','')))
    conn.commit()
    conn.close()

def marcar_enviado(email, asunto, message_id):
    conn = get_db()
    conn.execute("UPDATE leads SET email_enviado=1, fecha_envio=datetime('now'), asunto_email=?, message_id=?, estado='enviado' WHERE email=?", (asunto, message_id, email))
    conn.commit()
    conn.close()

def marcar_rebote(email):
    conn = get_db()
    conn.execute("UPDATE leads SET reboto=1, estado='rebotado' WHERE email=?", (email,))
    conn.commit()
    conn.close()

def marcar_respuesta(email):
    conn = get_db()
    conn.execute("UPDATE leads SET respondio=1, estado='respondio', fecha_respuesta=datetime('now') WHERE email=?", (email,))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    enviados = conn.execute("SELECT COUNT(*) FROM leads WHERE email_enviado=1").fetchone()[0]
    rebotados = conn.execute("SELECT COUNT(*) FROM leads WHERE reboto=1").fetchone()[0]
    respondidos = conn.execute("SELECT COUNT(*) FROM leads WHERE respondio=1").fetchone()[0]
    pendientes = conn.execute("SELECT COUNT(*) FROM leads WHERE email_enviado=0").fetchone()[0]
    conn.close()
    return {"total": total, "enviados": enviados, "rebotados": rebotados, "respondidos": respondidos, "pendientes": pendientes}

def get_resumen():
    conn = get_db()
    rows = conn.execute("""SELECT sector, COUNT(*) as total,
        SUM(email_enviado) as enviados, SUM(reboto) as rebotes,
        SUM(respondio) as respuestas
        FROM leads GROUP BY sector ORDER BY total DESC""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        s = get_stats()
        print(json.dumps(s, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "resumen":
        r = get_resumen()
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print("Tracking DB lista en", DB_PATH)
        s = get_stats()
        print(f"Total: {s['total']} | Enviados: {s['enviados']} | Rebotados: {s['rebotados']} | Respondidos: {s['respondidos']} | Pendientes: {s['pendientes']}")
