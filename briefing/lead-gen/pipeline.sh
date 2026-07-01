#!/bin/bash
# Pipeline de captacion NEO Labs
# Uso: bash pipeline.sh [sector] [ciudad]
# Ej: bash pipeline.sh restaurantes Madrid

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "=== NEO LEAD GEN PIPELINE ==="
echo "Fecha: $DATE"
echo ""

# Paso 1: Scrapear leads
echo "--- Paso 1: Scrapear leads ---"
python3 "$DIR/scraper.py" 2>&1 | tail -20
echo ""

# Paso 2: Personalizar emails
echo "--- Paso 2: Personalizar emails ---"
python3 "$DIR/personalizer.py" 2>&1 | tail -10
echo ""

# Paso 3: Enviar emails
echo "--- Paso 3: Enviar emails ---"
python3 "$DIR/sender.py" 2>&1
echo ""

echo "=== PIPELINE COMPLETADO ==="
