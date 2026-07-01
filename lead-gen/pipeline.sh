#!/usr/bin/env bash
# NEO Lead Pipeline - Orquestador completo
# 1. Scrapea leads 2. Personaliza emails 3. (opcional) Envía
# Uso: ./pipeline.sh [--tipo restaurante] [--ciudad Madrid] [--send]

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

TIPO="${2:-restaurante}"
CIUDAD="${4:-Madrid}"
SEND=false

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --tipo) TIPO="$2"; shift 2 ;;
    --ciudad) CIUDAD="$2"; shift 2 ;;
    --send) SEND=true; shift ;;
    --batch) BATCH=true; shift ;;
    *) shift ;;
  esac
done

echo "╔══════════════════════════════════╗"
echo "║     NEO Lead Pipeline v1         ║"
echo "╚══════════════════════════════════╝"
echo "Tipo: $TIPO | Ciudad: $CIUDAD"
echo ""

# 1. SCRAPING
echo "─── FASE 1: Scraping ───"
python3 scraper.py --tipo "$TIPO" --ciudad "$CIUDAD" --limite 20

# Find latest CSV
LATEST_CSV=$(ls -t data/*.csv 2>/dev/null | head -1)
if [ -z "$LATEST_CSV" ]; then
  echo "✗ No se generaron leads"
  exit 1
fi
echo "  Leads: $LATEST_CSV"
echo ""

# 2. PERSONALIZAR
echo "─── FASE 2: Personalizar emails ───"
python3 personalizer.py --input "$LATEST_CSV"

# Find personalized CSV
PERS_CSV=$(ls -t output/*.csv 2>/dev/null | head -1)
echo "  Personalizados: $PERS_CSV"
echo ""

# 3. ENVIAR (opcional)
if $SEND && [ -f "$PERS_CSV" ]; then
  echo "─── FASE 3: Enviar emails ───"
  echo "  Modo send activado. Enviando..."
  python3 -c "
import csv
with open('$PERS_CSV') as f:
    for row in csv.DictReader(f):
        print(f'  → {row.get(\"nombre\",\"?\")[:20]}: {row.get(\"asunto\",\"\")[:40]}')
  "
  echo "  Para enviar real: configura sender.py con Gmail API"
fi

echo ""
echo "✅ Pipeline completo"
echo "  Leads: $(wc -l < "$LATEST_CSV" 2>/dev/null)"
echo "  Emails: $(wc -l < "$PERS_CSV" 2>/dev/null)"
