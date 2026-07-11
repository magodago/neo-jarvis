#!/bin/bash
# Pipeline completo NEO Leads - 0 gasto de tokens (sin LLM)
# Ejecuta: exportar leads + personalizar + enviar + dashboard + git push

BASE="/home/dorti/neo-jarvis/briefing/lead-gen"
HERMES_VENV="/home/dorti/jarvis/hermes/hermes-agent/.venv/bin/python3"
cd "$BASE"

echo "[$(date '+%H:%M:%S')] 🚀 Pipeline NEO Leads iniciado"

# 1. Enviar emails pendientes (exporta DB -> personaliza -> envia -> actualiza DB)
echo "[1] Enviando emails pendientes..."
python3 enviar_v5.py 2>&1

# 2. Generar dashboard data.json
echo "[2] Generando dashboard..."
$HERMES_VENV /home/dorti/neo-jarvis/briefing/dashboard/generate_data.py 2>&1

# 3. Git push a GitHub Pages
echo "[3] Desplegando a GitHub Pages..."
cd /home/dorti/neo-jarvis
git add data.json landing/data.json dashboard.html 2>/dev/null
git diff --cached --quiet || {
    git commit -m "auto: pipeline update $(date '+%Y-%m-%d %H:%M')"
    git push 2>&1
    echo "   ✅ Desplegado"
}

echo "[$(date '+%H:%M:%S')] ✅ Pipeline completado"
