#!/usr/bin/env python3
import sqlite3, os
db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'leads.db')
if os.path.exists(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM leads')
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != ''")
    con_email = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads WHERE encontrado_por='places_api'")
    places = c.fetchone()[0]
    c.execute("SELECT MIN(fecha_scrapeo) FROM leads WHERE encontrado_por='places_api'")
    min_f = c.fetchone()[0]
    c.execute("SELECT MAX(fecha_scrapeo) FROM leads WHERE encontrado_por='places_api'")
    max_f = c.fetchone()[0]
    conn.close()
    print(f"Total leads DB: {total}")
    print(f"Con email: {con_email}")
    print(f"De Places API: {places}")
    print(f"Primer scrapeo Places: {min_f}")
    print(f"Ultimo scrapeo Places: {max_f}")
else:
    print("DB no existe")
