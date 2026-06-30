#!/usr/bin/env python3
"""
NEO Daily Briefing Generator
Genera un briefing diario premium en HTML con podcast, noticias, mundial, videos y mas.
Ejecutar: python3 generate_briefing.py
"""

import json, os, sys, re, subprocess, time, urllib.request, urllib.error
from datetime import datetime, date
from xml.etree import ElementTree

REPO_DIR = "/home/dorti/neo-jarvis"
AUDIO_DIR = os.path.join(REPO_DIR, "briefing")
TEMPLATE = os.path.join(REPO_DIR, "briefing", "template.html")
OUTPUT = os.path.join(REPO_DIR, "briefing", "index.html")
AUDIO_FILE = os.path.join(AUDIO_DIR, "podcast.mp3")
SCRIPT_FILE = os.path.join(AUDIO_DIR, "script.txt")

# Verified YouTube channels with working RSS feeds
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
            return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                log(f"  fetch failed: {url[:50]}... {e}")
    return ""

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
            return f"{temp}°C · {desc}"
    except: pass
    return "—"

# ─── 2. WORLD CUP ────────────────────────────────────────────
def get_world_cup():
    try:
        data = fetch("https://worldcup26.ir/get/games")
        if not data:
            return fallback_wc()
        
        raw = json.loads(data)
        matches = []
        if isinstance(raw, dict):
            for v in raw.values():
                if isinstance(v, list):
                    matches = v
                    break
        elif isinstance(raw, list):
            matches = raw
        
        if not matches:
            return fallback_wc()
        
        # Sort: live first, then by date
        def sort_key(m):
            finished = m.get("finished", "FALSE").upper() == "TRUE"
            elapsed = m.get("time_elapsed", "")
            if elapsed and elapsed != "finished":
                return (0, 0)  # live
            if finished:
                return (2, m.get("local_date", "zzz"))
            return (1, m.get("local_date", "zzz"))
        
        matches.sort(key=sort_key)
        
        html = ""
        count = 0
        for m in matches:
            if count >= 6: break
            
            home = m.get("home_team_name_en", "?")
            away = m.get("away_team_name_en", "?")
            hs = m.get("home_score", "")
            as_ = m.get("away_score", "")
            finished = m.get("finished", "FALSE").upper() == "TRUE"
            elapsed = m.get("time_elapsed", "")
            local_date = m.get("local_date", "")
            
            is_live = elapsed and elapsed != "finished"
            
            if is_live:
                status_class = "live"
                status_text = f"EN VIVO · {elapsed}'"
                score_html = f"<span class='live-dot'></span>{hs}–{as_}"
            elif finished:
                status_class = "finished"
                status_text = "FINAL"
                score_html = f"{hs}–{as_}"
            else:
                status_class = "pending"
                status_text = "PRÓXIMO"
                # Extract time from local_date
                time_match = re.search(r'(\d{2}:\d{2})$', local_date)
                score_html = f"<span class='vs'>{time_match.group(1) if time_match else '—'}</span>"
            
            html += f"""
<div class="wc-card">
  <div class="wc-status {status_class}">{status_text}</div>
  <div class="wc-match">
    <div class="wc-team home">
      <div class="wc-team-name">{home}</div>
    </div>
    <div class="wc-score">{score_html}</div>
    <div class="wc-team away">
      <div class="wc-team-name">{away}</div>
    </div>
  </div>
</div>"""
            count += 1
        
        html += """<a href="https://www.fifa.com/tournaments/mens/worldcup/usa-canada-mexico2026/" class="wc-more" target="_blank" rel="noopener">Ver todos los partidos →</a>"""
        return html
    except Exception as e:
        log(f"  wc error: {e}")
        return fallback_wc()

def fallback_wc():
    return '<div class="wc-card"><p style="color:var(--muted);font-size:.8rem">Mundial 2026 · 48 equipos · 16 sedes</p></div>'

# ─── 3. AI NEWS ──────────────────────────────────────────────
def get_ai_news():
    rss_feeds = [
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("MIT News AI", "https://news.mit.edu/topic/artificial-intelligence/rss2"),
        ("HackerNews", "https://hnrss.org/frontpage?count=10"),
    ]
    
    items = []
    seen = set()
    
    for source_name, url in rss_feeds:
        data = fetch(url)
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for item in root.iter("item"):
                title = item.findtext("title", "")[:90]
                link = item.findtext("link", "")
                pubdate = item.findtext("pubDate", "")[:16]
                if title and link and title not in seen:
                    seen.add(title)
                    items.append((source_name, title, link, pubdate))
            if len(items) < 5:
                for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                    title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")[:90]
                    link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    link = link_el.get("href", "") if link_el is not None else ""
                    if title and link and title not in seen:
                        seen.add(title)
                        items.append((source_name, title, link, ""))
        except Exception as e:
            log(f"  rss parse {source_name}: {e}")
    
    if not items:
        return ""
    
    # Max 8 items, variety of sources
    final = []
    for item in items:
        if len(final) >= 8: break
        final.append(item)
    
    emoji_map = {"TechCrunch AI": "📱", "MIT News AI": "🔬", "HackerNews": "💻"}
    html = ""
    for source, title, link, pubdate in final:
        emoji = emoji_map.get(source, "📰")
        html += f"""
<a class="news-card" href="{link}" target="_blank" rel="noopener">
  <div class="news-card-img">{emoji}</div>
  <div class="news-card-body">
    <div class="news-card-source">{source}</div>
    <div class="news-card-title">{title}</div>
    <div class="news-card-time">{pubdate}</div>
  </div>
</a>"""
    return html

# ─── 4. YOUTUBE ──────────────────────────────────────────────
def get_youtube_videos():
    html = ""
    seen = set()
    
    for name, ch_id in CHANNELS:
        data = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}")
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            count = 0
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                if count >= 3: break
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")[:80]
                video_id = entry.findtext("{http://www.youtube.com/xml/schemas/2015}videoId", "")
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")[:10]
                if video_id and video_id not in seen:
                    seen.add(video_id)
                    pub_date = ""
                    if published:
                        try:
                            pub_date = datetime.strptime(published[:10], "%Y-%m-%d").strftime("%d %b")
                        except: pass
                    html += f"""
<a class="video-card" href="https://youtube.com/watch?v={video_id}" target="_blank" rel="noopener">
  <div class="video-thumb">
    <img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" alt="" loading="lazy" onerror="this.style.display='none'">
  </div>
  <div class="video-info">
    <div class="video-title">{title}</div>
    <div class="video-channel">{name}</div>
    <div class="video-date">{pub_date}</div>
  </div>
</a>"""
                    count += 1
        except Exception as e:
            log(f"  yt parse {name}: {e}")
    
    if not html:
        html = '<p style="color:var(--muted);font-size:.8rem;padding:12px">Explora los canales de IA en YouTube</p>'
    return html

# ─── 5. PODCAST ──────────────────────────────────────────────
def generate_podcast(news_headlines, date_str):
    """Generate podcast script and audio."""
    news_text = "\n".join(f"- {h}" for h in news_headlines[:5]) if news_headlines else "Hoy sin noticias destacadas."
    
    script = f"""Buenos días. Bienvenido al NEO Briefing de {date_str}.

Hoy en inteligencia artificial:
{news_text}

En el Mundial 2026, la competición sigue con intensidad. Revisa los resultados en neolabs.es/briefing.

Para el prompt de hoy: imagina que eres un estratega de negocio con acceso a inteligencia artificial. Describe cómo automatizarías una tarea que consumes cada día. No pienses en la tecnología, piensa en el resultado.

Gracias por escuchar. Nos vemos mañana. Que tengas un gran día."""
    
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script)
    log(f"  script: {len(script)} chars")
    
    # Generate audio
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)
    
    cmd = [
        sys.executable, "-m", "edge_tts",
        "-f", SCRIPT_FILE,
        "-v", "es-ES-AlvaroNeural",
        "--rate=-5%",
        "--write-media", AUDIO_FILE,
    ]
    
    log(f"  generating audio...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        log(f"  audio error: {result.stderr[:200]}")
        return "no-audio", "—"
    
    if os.path.exists(AUDIO_FILE):
        size = os.path.getsize(AUDIO_FILE)
        log(f"  audio: {size/1024:.0f}KB")
        duration = _estimate_duration(script)
        return "./podcast.mp3", duration
    
    return "no-audio", "—"

def _estimate_duration(text):
    words = len(text.split())
    secs = max(30, round(words / 150 * 60))
    return f"{secs // 60}:{secs % 60:02d} min"

# ─── 6. PROMPT ───────────────────────────────────────────────
def get_prompt():
    prompts = [
        "Eres un estratega de negocio con acceso a cualquier herramienta de IA. Describe paso a paso cómo eliminarías una tarea repetitiva que consumes cada día.",
        "Actúa como un consultor de productividad personal. Analiza tu rutina y sugiere tres automatizaciones con IA que podrían ahorrarte 30 minutos cada día.",
        "Imagina que tienes un asistente AI que puede leer todos tus correos, calendario y notas. Pídele que te prepare un resumen ejecutivo de tu día antes de que empiece.",
        "Eres un copywriter experto que usa IA. Describe cómo generarías 30 días de contenido para redes sociales a partir de un solo post del blog.",
        "Piensa como un CTO. Diseña un sistema donde agentes AI se repartan el trabajo de tu equipo: uno investiga, otro escribe, otro revisa, otro despliega.",
        "Eres un diseñador de producto. Pídele a una IA que genere 10 variaciones de un mismo concepto visual y explícale cómo quieres que itere sobre ellos.",
        "Actúa como un analista de datos. Describe cómo usarías IA para encontrar patrones ocultos en los datos de tu negocio que nadie ha visto antes.",
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
        "La tecnología es solo una herramienta. La gente usa herramientas para mejorar sus vidas.",
        "No sobrevive la especie más fuerte, sino la que mejor se adapta al cambio.",
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
    log(f"  HTML written")

# ─── 9. DEPLOY ───────────────────────────────────────────────
def deploy():
    log("  deploying...")
    subprocess.run(["git", "-C", REPO_DIR, "add", "briefing/"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"daily briefing {datetime.now().strftime('%Y-%m-%d %H:%M')}"], capture_output=True)
    
    result = subprocess.run(["git", "-C", REPO_DIR, "push"], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        log("  deployed!")
        return True
    log(f"  push error: {result.stderr[:200]}")
    return False

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
    
    log("3. RSS News...")
    news = get_ai_news()
    
    log("4. YouTube...")
    yt = get_youtube_videos()
    
    log("5. Prompt...")
    prompt = get_prompt()
    
    log("6. Quote...")
    quote = get_quote()
    
    log("7. Podcast...")
    audio_url, duration = generate_podcast([], date_str)
    topics = "Noticias AI · Mundial · Productividad"
    
    log("8. Assembling...")
    now = datetime.now().strftime("%H:%M")
    
    params = {
        "DATE": date_str,
        "DATE_SHORT": date_short,
        "DAY_NAME": day_name,
        "WEEK_NUM": str(week_num),
        "WEATHER": weather,
        "WORLD_CUP": wc,
        "AI_NEWS": news,
        "YOUTUBE_VIDEOS": yt,
        "PROMPT": prompt,
        "QUOTE": quote,
        "PODCAST_AUDIO": audio_url,
        "PODCAST_DURATION": duration,
        "PODCAST_TOPICS": topics,
        "GENERATED_AT": f"{date_str} · {now}",
    }
    
    assemble(params)
    
    log("9. Deploying...")
    ok = deploy()
    
    url = "https://neolabs.es/briefing/"
    log(f"\n✅ {url}")
    return ok

if __name__ == "__main__":
    main()
