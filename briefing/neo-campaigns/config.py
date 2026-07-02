#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuración compartida para scripts de NEO Campaigns"""
import os

# ── Google Places API ──
# Lee la clave del scraper (la única fuente de verdad)
_SCRAPER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lead-gen", "places_scraper.py")
import re
_SCRAPER_TEXT = ""
try:
    with open(_SCRAPER_PATH) as f:
        _SCRAPER_TEXT = f.read()
    _KEY_MATCH = re.search(r'AIza[0-9A-Za-z_-]{20,50}', _SCRAPER_TEXT)
    if _KEY_MATCH:
        GOOGLE_PLACES_API_KEY = _KEY_MATCH.group(0)
    else:
        GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
except Exception:
    GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

# ── Rutas ──
BASE = os.path.dirname(os.path.abspath(__file__))
LEAD_DB = os.path.join(BASE, "..", "lead-gen", "data", "leads.db")
LEAD_LOGS = os.path.join(BASE, "..", "lead-gen", "logs")
CLIENTES_DB = os.path.join(BASE, "clientes", "clientes.db")
LANDING_URL = "https://magodago.github.io/neo-jarvis/briefing/neo-campaigns/"

# ── Gmail ──
TOKEN_FILE = os.path.expanduser("~/.hermes/google_token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify"]
