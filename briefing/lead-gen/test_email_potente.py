#!/usr/bin/env python3
"""Test del nuevo email potente — prueba con 3 leads reales"""
import json, os, sys, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enviar_potente import generar_email_personalizado

db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'leads.db')
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('''SELECT id, nombre, email, ciudad, sector FROM leads 
             WHERE email IS NOT NULL AND email != "" AND email_enviado=0 
             LIMIT 3''')
leads = c.fetchall()
conn.close()

print("=" * 60)
print("NUEVO EMAIL POTENTE — EJEMPLOS")
print("=" * 60)

for lead in leads:
    lid, nombre, email, ciudad, sector = lead
    subj, body = generar_email_personalizado(lead)
    
    print(f'\n--- {nombre} ({sector}, {ciudad}) ---')
    print(f'ASUNTO: {subj}')
    print(f'CUERPO:')
    print(body)
    print()
    
    if 'responde a este mail' in body.lower() or 'responde a este correo' in body.lower():
        print('  [FALLBACK — pero suena bien igual]')
    else:
        print('  [PERSONALIZADO por DeepSeek]')
