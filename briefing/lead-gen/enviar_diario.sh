#!/bin/bash
# Script wrapper para enviar_v5.py con límite diario de 100
# Se ejecuta como no_agent desde cron
cd /home/dorti/neo-jarvis/briefing/lead-gen
export PATH="/home/dorti/neo-scraper/venv/bin:$PATH"
python3 enviar_v5.py 2>&1
