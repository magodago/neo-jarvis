#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera data.json para el dashboard NEO con datos reales de tracker + logs"""
import json, os, csv, datetime, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "lead-gen"))
import tracker

stats = tracker.get_stats()
sectores = tracker.get_resumen()

LOGS_DIR = os.path.join(BASE, "lead-gen", "logs")
sent_leads = []
sent_path = os.path.join(LOGS_DIR, "sent.csv")
if os.path.exists(sent_path):
    with open(sent_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sent_leads.append({
                "name": row.get("nombre", ""),
                "email": row.get("email_destino", ""),
                "subject": row.get("asunto", ""),
                "status": row.get("status", "pending"),
                "date": "",
            })

# Mapear campos del tracker a lo que espera el JS
data = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "stats": {
        "total": stats["total"],
        "sent": stats["enviados"],
        "bounce": stats["rebotados"],
        "reply": stats["respondidos"],
        "pending": stats["pendientes"],
    },
    "sectors": [
        {
            "sector": s["sector"],
            "total": s["total"],
            "sent": s["enviados"],
            "bounces": s["rebotes"],
            "replies": s["respuestas"],
        }
        for s in sectores
    ],
    "sent_leads": sent_leads,
}

OUT_DIR = os.path.join(BASE, "landing")
os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "data.json"), "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(json.dumps({"status": "ok", "leads": stats["total"], "sent": stats["enviados"]}))
