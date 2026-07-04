#!/usr/bin/env python3
"""Wrapper que ejecuta enviar_v3.py con reintentos inteligentes en caso de 429."""
import subprocess, re, time, sys, json
from datetime import datetime, timezone

SCRIPT = "/home/dorti/neo-jarvis/briefing/lead-gen/enviar_v3.py"
PYTHON = "/home/dorti/neo-scraper/venv/bin/python3"
MAX_RETRIES = 10
RETRY_BASE_DELAY = 60  # seconds minimum wait between retries

def parse_retry_after(output):
    """Busca el timestamp 'Retry after YYYY-MM-DDTHH:MM:SS.FFFZ' en el output."""
    m = re.search(r"Retry after (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)", output)
    if m:
        ts_str = m.group(1)
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return ts
    return None

def count_success(output):
    """Busca 'ENVIADOS: N' en el output."""
    m = re.search(r"ENVIADOS:\s*(\d+)", output)
    return int(m.group(1)) if m else 0

def count_pending(output):
    """Busca 'PENDIENTES: N' en el output."""
    m = re.search(r"PENDIENTES:\s*(\d+)", output)
    return int(m.group(1)) if m else 0

def main():
    print("=" * 60)
    print(f"  NEO EMAIL v3 — Retry Wrapper")
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total_sent_ever = 0

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n{'─'*60}")
        print(f"  🔄 Intento {attempt}/{MAX_RETRIES}")
        print(f"  ⏰ {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'─'*60}\n")

        try:
            result = subprocess.run(
                [PYTHON, SCRIPT],
                capture_output=True, text=True, timeout=900
            )
            output = result.stdout + "\n" + result.stderr
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
            output = stdout + "\n" + stderr if (stdout or stderr) else "(timeout - no output)"
        print(output)

        sent_now = count_success(output)
        total_sent_ever += sent_now
        remaining = count_pending(output)

        # Check if we're done
        if remaining == 0:
            print(f"\n✅ COMPLETO — Todos los emails enviados!")
            break

        # Check for 429
        if "429" in output or "rateLimitExceeded" in output:
            retry_ts = parse_retry_after(output)
            if retry_ts:
                now = datetime.now(timezone.utc)
                wait_seconds = (retry_ts - now).total_seconds() + 5  # 5s buffer
                wait_seconds = max(wait_seconds, RETRY_BASE_DELAY)
                if wait_seconds > 3600:
                    print(f"\n⏳ La espera sugerida es de {wait_seconds/60:.0f} minutos — probable límite diario.")
                    print(f"   Esperando hasta: {retry_ts.strftime('%H:%M:%S')} UTC")
                    print(f"   Se han enviado {total_sent_ever} en esta ejecución.")
                    if wait_seconds > 7200:
                        print(f"   ⚠️ Espera demasiado larga (>2h). Deteniendo por hoy.")
                        break
                else:
                    print(f"\n⏳ Esperando {wait_seconds:.0f}s hasta {retry_ts.strftime('%H:%M:%S')} UTC...")
                wait_seconds = min(wait_seconds, 7200)
                for remaining_wait in range(int(wait_seconds), 0, -30):
                    mins = remaining_wait // 60
                    secs = remaining_wait % 60
                    print(f"    ⏱  {mins}m {secs}s restantes...")
                    time.sleep(min(30, remaining_wait))
            else:
                print(f"\n⏳ 429 detectado sin timestamp. Esperando {RETRY_BASE_DELAY}s...")
                time.sleep(RETRY_BASE_DELAY)
        else:
            # No 429, some other error or partial success
            if sent_now > 0 and remaining > 0:
                print(f"\n⚠️ Envío parcial: {sent_now} enviados, {remaining} pendientes.")
                print(f"   Reintentando en 30s...")
                time.sleep(30)
            else:
                print(f"\n⚠️ Error sin 429. Reintentando en 60s...")
                time.sleep(RETRY_BASE_DELAY)
    else:
        print(f"\n⚠️ Se alcanzó el máximo de reintentos ({MAX_RETRIES}).")

    # Final summary from DB
    print(f"\n{'='*60}")
    print(f"  📊 RESUMEN FINAL")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"  Enviados en esta ejecución: {total_sent_ever}")
    
    # Query DB for final state
    import sqlite3
    db = "/home/dorti/neo-jarvis/briefing/lead-gen/data/leads.db"
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM leads')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM leads WHERE email_enviado=1')
    enviados = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != "" AND (email_enviado IS NULL OR email_enviado=0)')
    pendientes = c.fetchone()[0]
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM leads WHERE fecha_envio LIKE ?", (today+'%',))
    enviados_hoy = c.fetchone()[0]
    conn.close()
    
    print(f"  DB total leads:       {total}")
    print(f"  DB enviados total:    {enviados}")
    print(f"  DB pendientes:        {pendientes}")
    print(f"  Enviados hoy:         {enviados_hoy}")

if __name__ == "__main__":
    main()
