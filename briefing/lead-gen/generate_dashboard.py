#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera data.json para el dashboard desde la DB de leads"""
import json, os, csv, datetime

LEAD_DIR = "/home/dorti/neo-jarvis/briefing/lead-gen"
DATA_DIR = os.path.join(LEAD_DIR, "data")
LOGS_DIR = os.path.join(LEAD_DIR, "logs")
OUT_DIR = "/home/dorti/neo-jarvis/landing"
os.makedirs(OUT_DIR, exist_ok=True)

# Leer DB
import sys; sys.path.insert(0, LEAD_DIR)
import tracker

stats = tracker.get_stats()
sectores = tracker.get_resumen()

# Leer log de enviados
sent_leads = []
sent_path = os.path.join(LOGS_DIR, "sent.csv")
if os.path.exists(sent_path):
    with open(sent_path) as f:
        for row in csv.DictReader(f):
            sent_leads.append({
                "name": row.get("nombre", ""),
                "email": row.get("email_destino", ""),
                "subject": row.get("asunto", ""),
                "status": "bounced" if "bounce" in row.get("status","").lower() else row.get("status","pending"),
                "date": row.get("fecha_envio", ""),
            })

data = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "stats": stats,
    "sectors": sectores,
    "sent_leads": sent_leads,
}

out_path = os.path.join(OUT_DIR, "data.json")
with open(out_path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(json.dumps({"status": "ok", "leads": stats["total"], "sent": stats["enviados"], "file": out_path}))
