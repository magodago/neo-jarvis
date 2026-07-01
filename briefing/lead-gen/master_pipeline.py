#!/usr/bin/env python3
"""
NEO Lead Gen Pipeline — Full automated pipeline.
1. Scrape Google Maps for new leads (if no recent scrape)
2. Merge with existing leads
3. Personalize emails with DeepSeek
4. Send emails via Gmail API
5. Update dashboard data
6. Clean inbox
"""
import os, sys, csv, json, datetime, subprocess, time

BASE = '/home/dorti/neo-jarvis/briefing/lead-gen'
DATA = f'{BASE}/data'
DASHBOARD = '/home/dorti/neo-jarvis/briefing/dashboard'

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_script(name, timeout=120):
    """Run a Python script and return (success, output)."""
    path = f'{BASE}/{name}'
    if not os.path.exists(path):
        return False, f"File not found: {path}"
    try:
        result = subprocess.run(
            ['python3', path],
            capture_output=True, text=True, timeout=timeout,
            cwd=BASE
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output.strip()
    except subprocess.TimeoutExpired:
        return False, "Timeout"

def main():
    print(f"\n{'='*60}")
    print(f"🚀 NEO LEAD GEN PIPELINE — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    # Step 1: Scrape Google Maps for leads (run daily, not every time)
    maps_file = f'{DATA}/google_maps_leads.csv'
    need_scrape = False
    if os.path.exists(maps_file):
        mtime = os.path.getmtime(maps_file)
        days_old = (time.time() - mtime) / 86400
        need_scrape = days_old > 1
    else:
        need_scrape = True
    
    if need_scrape:
        log("📡 Step 1: Scraping Google Maps for new leads...")
        success, output = run_script('gmaps_scraper.py', timeout=600)
        if success:
            log(f"✅ Scrape completado")
            # Count leads
            try:
                with open(maps_file, newline='', encoding='utf-8') as f:
                    leads = list(csv.DictReader(f))
                log(f"   {len(leads)} leads extraídos")
            except:
                pass
        else:
            log(f"⚠️ Scrape falló: {output[:200]}")
    else:
        log(f"⏭️ Scrape no necesario (datos de hace < 1 día)")
    
    # Step 2: Merge new leads into master DB
    log("\n💾 Step 2: Merging leads into database...")
    success, output = run_script('tracker.py', timeout=30)
    if success:
        log("✅ Merge completado")
    else:
        log(f"⚠️ Merge falló: {output[:200]}")
    
    # Step 3: Generate dashboard data
    log("\n📊 Step 3: Generating dashboard data...")
    data_gen = f'{DASHBOARD}/generate_data.py'
    result = subprocess.run(['python3', data_gen], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        log(f"✅ Dashboard actualizado")
    else:
        log(f"⚠️ Dashboard falló: {result.stderr[:100]}")
    
    # Step 4: Send emails to new leads
    log("\n📧 Step 4: Sending emails to leads...")
    success, output = run_script('pipeline.py', timeout=120)
    if success:
        log(f"✅ Emails enviados")
        # Parse sent count
        for line in output.split('\n'):
            if 'enviado' in line.lower() or 'Enviados' in line or 'sent' in line.lower():
                log(f"   {line.strip()}")
    else:
        log(f"⚠️ Envío falló: {output[:200]}")
    
    # Step 5: Clean inbox
    log("\n🧹 Step 5: Cleaning inbox...")
    success, output = run_script('inbox_cleaner.py', timeout=30)
    if success:
        log(f"✅ Inbox limpiado")
    else:
        log(f"⚠️ Limpieza falló: {output[:200]}")
    
    # Summary
    print(f"\n{'='*60}")
    log(f"✅ PIPELINE COMPLETADO")
    try:
        with open(f'{DATA}/leads.db_info', 'w') as f:
            f.write(f'Last run: {datetime.datetime.now().isoformat()}\n')
    except:
        pass
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
