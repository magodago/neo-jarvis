#!/usr/bin/env python3
"""
NEO Daily Briefing Generator v2
Briefing diario premium en HTML con noticias en español, mundial, videos del día y más.
Ejecutar: python3 generate_briefing.py
"""

import json, os, sys, re, subprocess, time, urllib.request
from datetime import datetime, date, timedelta
from xml.etree import ElementTree
from html import unescape

REPO_DIR = "/home/dorti/neo-jarvis"
AUDIO_DIR = os.path.join(REPO_DIR, "briefing")
TEMPLATE = os.path.join(REPO_DIR, "briefing", "template.html")
OUTPUT = os.path.join(REPO_DIR, "briefing", "index.html")
AUDIO_FILE = os.path.join(AUDIO_DIR, "podcast.mp3")
SCRIPT_FILE = os.path.join(AUDIO_DIR, "script.txt")

# YouTube channels
CHANNELS = [
    ("DotCSV", "UCOTko-zmnQTcOxSRdg5_uOQ"),
    ("Xavier Mitjana", "UCeu3sN4T72Fka1rhQFR447A"),
]

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def fetch(url, timeout=15):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp = urllib.request.urlopen(req, timeout=timeout)
            data = resp.read()
            try: return data.decode('utf-8', errors='replace')
            except: return data.decode('latin-1', errors='replace')
        except Exception as e:
            if attempt < 2: time.sleep(2)
            else: log(f"  failed: {url[:50]}... {e}")
    return ""

def strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    return ' '.join(text.split())[:300]

# ─── 1. WEATHER ──────────────────────────────────────────────
def get_weather():
    try:
        data = fetch("https://wttr.in/Illescas?format=j1")
        if data:
            d = json.loads(data)
            cc = d['current_condition'][0]
            temp = cc['temp_C']
            desc = cc['weatherDesc'][0]['value']
            hum = cc['humidity']
            wind = cc['windspeedKmph']
            return f"{temp}°C · {desc} · Hum {hum}%"
    except Exception as e:
        log(f"  weather: {e}")
    return "—"

# ─── 2. WORLD CUP ────────────────────────────────────────────
def get_world_cup():
    try:
        data = fetch("https://worldcup26.ir/get/games")
        if not data: return fallback_wc()
        raw = json.loads(data)
        
        matches = []
        if isinstance(raw, dict):
            for v in raw.values():
                if isinstance(v, list): matches = v; break
        elif isinstance(raw, list): matches = raw
        
        if not matches: return fallback_wc()
        
        # Filter to matches with team names and recent/pending
        valid = [m for m in matches if m.get("home_team_name_en") and m.get("away_team_name_en")]
        if not valid: return fallback_wc()
        
        def sort_key(m):
            elapsed = m.get("time_elapsed", "").lower()
            finished = m.get("finished", "false").upper() == "TRUE"
            # Live = elapsed is a number (minute like "45'")
            is_live = bool(re.match(r"^\d+", elapsed))
            if is_live: return (0, 0)
            if finished: return (2, m.get("local_date", "zzz"))
            return (1, m.get("local_date", "zzz"))
        
        valid.sort(key=sort_key)
        
        html = ""
        count = 0
        for m in valid:
            if count >= 6: break
            
            home = m["home_team_name_en"]
            away = m["away_team_name_en"]
            hs = m.get("home_score", "")
            as_ = m.get("away_score", "")
            finished = m.get("finished", "false").upper() == "TRUE"
            elapsed = m.get("time_elapsed", "").lower()
            local_date = m.get("local_date", "")
            
            is_live = bool(re.match(r"^\d+", elapsed))
            
            if is_live:
                status_class = "live"
                status_text = f"EN VIVO · {elapsed}"
                score_html = f"<span class='live-dot'></span>{hs}–{as_}"
            elif finished:
                status_class = "finished"
                status_text = "FINAL"
                score_html = f"{hs}–{as_}"
            else:
                status_class = "pending"
                status_text = "PRÓXIMO"
                time_match = re.search(r'(\d{2}:\d{2})$', local_date)
                score_html = f"<span class='vs'>{time_match.group(1) if time_match else '—'}</span>"
            
            html += f"""
<div class="wc-card">
  <div class="wc-status {status_class}">{status_text}</div>
  <div class="wc-match">
    <div class="wc-team home"><span class="wc-team-name">{home}</span></div>
    <div class="wc-score">{score_html}</div>
    <div class="wc-team away"><span class="wc-team-name">{away}</span></div>
  </div>
</div>"""
            count += 1
        
        html += '<a href="https://www.fifa.com/tournaments/mens/worldcup/usa-canada-mexico2026/" class="wc-more" target="_blank" rel="noopener">Ver todos →</a>'
        return html
    except Exception as e:
        log(f"  wc: {e}")
        return fallback_wc()

def fallback_wc():
    return '<div class="wc-card"><p style="color:var(--muted);font-size:.8rem">Mundial 2026 · 48 equipos · 16 sedes</p></div>'

# ─── 3. AI NEWS (ESPAÑOL) ────────────────────────────────────
def get_ai_news_es():
    feeds = [
        ("Hipertextual", "https://hipertextual.com/feed"),
        ("WWWhatsnew", "https://wwwhatsnew.com/feed"),
    ]
    
    items = []
    seen_titles = set()
    
    for source, url in feeds:
        data = fetch(url)
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for item in root.iter("item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                desc = strip_html(item.findtext("description", ""))
                pubdate = item.findtext("pubDate", "")[:16]
                
                if not title or not link: continue
                # Dedup
                key = title.lower()[:40]
                if key in seen_titles: continue
                seen_titles.add(key)
                
                # Only AI/tech relevant
                items.append({
                    "source": source, "title": title, "link": link,
                    "desc": desc[:200], "pubdate": pubdate
                })
                if len(items) >= 10: break
            if len(items) >= 10: break
        except Exception as e:
            log(f"  rss {source}: {e}")
    
    return items[:8]

def news_to_html(items):
    if not items: return ""
    
    # Store summaries as data attributes for the modal
    html = ""
    for i, item in enumerate(items):
        summary = item["desc"].replace('"', "'")
        html += f"""
<div class="news-card" onclick="openNewsModal({i})" data-index="{i}">
  <div class="news-card-img">📰</div>
  <div class="news-card-body">
    <div class="news-card-source">{item['source']}</div>
    <div class="news-card-title">{item['title'][:90]}</div>
    <div class="news-card-time">{item['pubdate']}</div>
  </div>
</div>"""
    return html, items

# ─── 4. YOUTUBE (SOLO HOY) ───────────────────────────────────
def get_youtube_today():
    today = date.today()
    html = ""
    seen = set()
    
    for name, ch_id in CHANNELS:
        data = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}")
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")[:80]
                video_id = entry.findtext("{http://www.youtube.com/xml/schemas/2015}videoId", "")
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")[:10]
                
                if not video_id or video_id in seen: continue
                seen.add(video_id)
                
                # Only today's videos
                if published:
                    try:
                        pub_date = datetime.strptime(published[:10], "%Y-%m-%d").date()
                        if pub_date != today: continue
                    except: continue
                
                html += f"""
<a class="video-card" href="https://youtube.com/watch?v={video_id}" target="_blank" rel="noopener">
  <div class="video-thumb">
    <img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" alt="" loading="lazy" onerror="this.style.display='none'">
  </div>
  <div class="video-info">
    <div class="video-title">{title}</div>
    <div class="video-channel">{name}</div>
    <div class="video-date">Hoy</div>
  </div>
</a>"""
        except Exception as e:
            log(f"  yt {name}: {e}")
    
    if not html:
        html = '<p style="color:var(--muted);font-size:.8rem;padding:12px">No hay videos nuevos hoy de los canales seguidos</p>'
    return html

# ─── 5. PODCAST ──────────────────────────────────────────────
def generate_podcast(news_items, date_str):
    news_lines = "\n".join(f"- {item['title'][:60]}" for item in news_items[:4]) if news_items else "Hoy sin noticias destacadas."
    
    script = f"""Buenos días. Bienvenido al NEO Briefing de {date_str}.

Hoy en inteligencia artificial:
{news_lines}

En el Mundial 2026, la competición continúa. Revisa los resultados en neolabs.es/briefing.

Prompt del día: piensa en una tarea que haces cada día y que podrías delegar completamente a un agente de IA. Describe el resultado ideal, no el proceso.

Gracias por escuchar. Que tengas un gran día."""
    
    os.makedirs(AUDIO_DIR, exist_ok=True)
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script)
    log(f"  script: {len(script)} chars")
    
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)
    
    cmd = [sys.executable, "-m", "edge_tts", "-f", SCRIPT_FILE,
           "-v", "es-ES-AlvaroNeural", "--rate=-5%",
           "--write-media", AUDIO_FILE]
    
    log(f"  audio...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        log(f"  audio error: {r.stderr[:200]}")
        return "no-audio", "—"
    
    if os.path.exists(AUDIO_FILE):
        log(f"  audio: {os.path.getsize(AUDIO_FILE)/1024:.0f}KB")
        secs = max(20, round(len(script.split()) / 150 * 60))
        return "./podcast.mp3", f"{secs//60:02d}:{secs%60:02d}"
    return "no-audio", "—"

# ─── 6. PROMPT ───────────────────────────────────────────────
def get_prompt():
    prompts = [
        "Diseña un flujo donde un agente AI investige un tema mientras otro escribe y un tercero revisa. Tres agentes, un solo resultado.",
        "Describe cómo usarías IA para transformar una reunión de 1 hora en: notas, acciones, follow-ups y un resumen ejecutivo. Sin escribir nada tú.",
        "Crea un sistema donde cada email que recibes es respondido automáticamente con el tono y conocimiento de tu negocio. ¿Cómo lo entrenarías?",
        "Imagina un asistente AI que conoce tu calendario, tus correos y tus proyectos. Cada mañana te da 3 decisiones que debes tomar hoy. Nada más.",
        "Diseña un pipeline donde una idea en voz se convierte en: tweet, hilo, artículo de blog y video corto. Todo automático, todo con IA.",
    ]
    return prompts[datetime.now().day % len(prompts)]

# ─── 7. QUOTE ────────────────────────────────────────────────
def get_quote():
    quotes = [
        "La mejor manera de predecir el futuro es crearlo.",
        "No se trata de tener tiempo, se trata de tener prioridades.",
        "La IA no reemplazará a los humanos, pero los humanos con IA reemplazarán a los que no la usen.",
        "La automatización no es perder el control, es ganar libertad.",
        "El mayor riesgo es no correr ningún riesgo.",
    ]
    return quotes[datetime.now().day % len(quotes)]

# ─── 8. ASSEMBLE ─────────────────────────────────────────────
def assemble(params):
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()
    for key, value in params.items():
        html = html.replace("{{" + key + "}}", str(value))
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"  HTML: {len(html)} bytes")

# ─── 9. DEPLOY ───────────────────────────────────────────────
def deploy():
    log("  deploying...")
    subprocess.run(["git", "-C", REPO_DIR, "add", "briefing/"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"briefing {datetime.now().strftime('%Y-%m-%d')}"], capture_output=True)
    r = subprocess.run(["git", "-C", REPO_DIR, "push"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0: return True
    log(f"  push: {r.stderr[:200]}")
    return False

# ─── 10. MODAL HTML ──────────────────────────────────────────
def news_modal_html(items):
    if not items: return ""
    html = '<div id="news-modal" class="news-modal" onclick="if(event.target===this)closeNewsModal()"><div class="news-modal-content" id="news-modal-content"></div></div>'
    data = []
    for item in items:
        data.append({
            "source": item["source"],
            "title": item["title"],
            "desc": item["desc"][:500],
            "link": item["link"]
        })
    return html, data

# ─── MAIN ─────────────────────────────────────────────────────
def main():
    log("=== NEO DAILY BRIEFING ===")
    today = date.today()
    date_str = today.strftime("%d de %B de %Y")
    date_short = today.strftime("%d.%m.%Y")
    day_name = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"][today.weekday()]
    week_num = today.isocalendar()[1]
    
    log("1. Weather...")
    weather = get_weather()
    
    log("2. World Cup...")
    wc = get_world_cup()
    
    log("3. News (ES)...")
    news_items = get_ai_news_es()
    news_html, news_data = news_to_html(news_items)
    log(f"   {len(news_items)} noticias")
    
    log("4. YouTube today...")
    yt = get_youtube_today()
    
    log("5. Prompt...")
    prompt = get_prompt()
    
    log("6. Quote...")
    quote = get_quote()
    
    log("7. Podcast...")
    audio_url, duration = generate_podcast(news_items, date_str)
    
    log("8. Assembling...")
    now = datetime.now().strftime("%H:%M")
    
    # Build news modal JS
    modal = '<div id="news-modal" class="news-modal" onclick="if(event.target===this)closeNewsModal()"><div class="news-modal-content" id="news-content"></div></div>'
    
    params = {
        "DATE": date_str,
        "DATE_SHORT": date_short,
        "DAY_NAME": day_name,
        "WEEK_NUM": str(week_num),
        "WEATHER": weather,
        "WORLD_CUP": wc,
        "AI_NEWS": news_html,
        "YOUTUBE_VIDEOS": yt,
        "PROMPT": prompt,
        "QUOTE": quote,
        "PODCAST_AUDIO": audio_url,
        "PODCAST_DURATION": duration,
        "PODCAST_TOPICS": "Noticias IA · Mundial · Productividad",
        "GENERATED_AT": f"{date_str} · {now}",
        "NEWS_MODAL": modal,
        "NEWS_DATA": json.dumps(news_data, ensure_ascii=False),
    }
    
    assemble(params)
    
    log("9. Deploying...")
    ok = deploy()
    
    url = "https://magodago.github.io/neo-jarvis/briefing/"
    log(f"\n✅ {url}")
    return ok

if __name__ == "__main__":
    main()
