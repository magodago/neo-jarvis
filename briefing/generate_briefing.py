#!/usr/bin/env python3
"""
NEO Daily Briefing Generator
Genera un briefing diario premium en HTML con podcast, noticias, mundial, videos y más.
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

CHANNELS = [
    ("DotCSV", "@DotCSV", "UCFmkKLYOqXJzS_JxUF4xWKw"),
    ("Jon Hernández", "@la_inteligencia_artificial", "UCnIl3dpIkWQEnMZQF08HnGg"),
    ("Xavier Mitjana", "@XavierMitjana", "UCeY1OieApUqS0QFYFIhjGAg"),
    ("Laura IA", "@Laura_IA", "UCvMQhL1ZzKMcYhW9apW3X6w"),
]

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def fetch(url, timeout=15):
    """Fetch URL with retry and headers."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp = urllib.request.urlopen(req, timeout=timeout)
            return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            log(f"  fetch attempt {attempt+1}/3 failed: {e}")
            time.sleep(2)
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
            return f"{temp}°C · {desc} · 💨 {wind} km/h"
    except Exception as e:
        log(f"  weather error: {e}")
    return "—"

# ─── 2. WORLD CUP ────────────────────────────────────────────
def get_world_cup():
    """Fetch matches from worldcup26.ir free API."""
    try:
        data = fetch("https://worldcup26.ir/get/games")
        if not data:
            return "<div class='wc-card'><p style='color:var(--muted);font-size:.8rem'>Mundial 2026 — consulta resultados en FIFA.com</p></div>"
        
        matches = json.loads(data)
        html = ""
        count = 0
        
        # Get today's matches first, then recent results
        today = date.today().isoformat()
        
        # Sort: live first, then by date
        def sort_key(m):
            status = m.get("status", "")
            if status == "live": return (0, 0)
            if status in ("ft", "finished", "completed"): return (2, m.get("date", "zzz"))
            return (1, m.get("date", "zzz"))
        
        matches.sort(key=sort_key)
        
        for m in matches:
            if count >= 6:
                break
            
            home = m.get("home", {}).get("name", "?")
            away = m.get("away", {}).get("name", "?")
            home_score = m.get("home", {}).get("score", "")
            away_score = m.get("away", {}).get("score", "")
            status = m.get("status", "pending").lower()
            match_date = m.get("date", "")
            match_time = m.get("time", "")
            
            if status in ("ft", "finished", "completed"):
                status_class = "finished"
                status_text = "FINAL"
                score_html = f"{home_score}–{away_score}"
            elif status == "live":
                status_class = "live"
                minute = m.get("minute", "")
                status_text = "EN VIVO"
                score_html = f"<span class='live-dot'></span>{home_score}–{away_score}"
            else:
                status_class = "pending"
                status_text = "PRÓXIMO"
                score_html = f"<span class='vs'>{match_time or '—'}</span>"
            
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
        
        html += """<a href="https://www.fifa.com/tournaments/mens/worldcup/usa-canada-mexico2026/" class="wc-more" target="_blank">Ver todos los partidos →</a>"""
        return html
    except Exception as e:
        log(f"  world cup error: {e}")
        return "<div class='wc-card'><p style='color:var(--muted);font-size:.8rem'>Mundial 2026 en curso</p></div>"

# ─── 3. AI NEWS (RSS) ────────────────────────────────────────
def get_ai_news():
    rss_feeds = [
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("MIT News AI", "https://news.mit.edu/topic/artificial-intelligence/rss2"),
        ("HackerNews", "https://hnrss.org/frontpage?count=10"),
    ]
    
    items = []
    seen = set()
    
    for source_name, url in rss_feeds:
        try:
            data = fetch(url)
            if not data: continue
            root = ElementTree.fromstring(data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            # RSS 2.0
            for item in root.iter("item"):
                title = item.findtext("title", "")[:80]
                link = item.findtext("link", "")
                pubdate = item.findtext("pubDate", "")[:16]
                if title and link and title not in seen:
                    seen.add(title)
                    items.append((source_name, title, link, pubdate))
                    if len(items) >= 12: break
            
            # Atom
            if not items:
                for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                    title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")[:80]
                    link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    link = link_el.get("href", "") if link_el is not None else ""
                    if title and link and title not in seen:
                        seen.add(title)
                        items.append((source_name, title, link, ""))
                        if len(items) >= 12: break
            
            if len(items) >= 12: break
            
        except Exception as e:
            log(f"  rss {source_name} error: {e}")
            continue
    
    # Limit to 10 items, ensure variety
    used_sources = set()
    final_items = []
    for item in items:
        if len(final_items) >= 8: break
        source = item[0]
        if source not in used_sources or len([x for x in final_items if x[0]==source]) < 3:
            final_items.append(item)
            used_sources.add(source)
    
    if not final_items:
        return ""
    
    emoji_map = {"TechCrunch AI": "📱", "MIT News AI": "🔬", "HackerNews": "💻"}
    html = ""
    for source, title, link, pubdate in final_items:
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
    """Try RSS feeds for YouTube channels."""
    html = ""
    seen = set()
    
    for name, handle, ch_id in CHANNELS:
        try:
            data = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}")
            if not data:
                # Try handle-based feed
                data = fetch(f"https://www.youtube.com/feeds/videos.xml?user={handle.replace('@','')}")
            if not data: continue
            
            root = ElementTree.fromstring(data)
            ns = {"yt": "http://www.youtube.com/xml/schemas/2015"}
            
            count = 0
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                if count >= 3: break
                title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")[:80]
                video_id = entry.findtext("{http://www.youtube.com/xml/schemas/2015}videoId", "")
                published = entry.findtext("{http://www.w3.org/2005/Atom}published", "")[:10]
                if video_id and video_id not in seen:
                    seen.add(video_id)
                    pub_date = datetime.strptime(published[:10], "%Y-%m-%d").strftime("%d %b") if published else ""
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
            log(f"  yt {name} error: {e}")
            continue
    
    if not html:
        html = '<p style="color:var(--muted);font-size:.8rem;padding:12px">No hay videos nuevos hoy</p>'
    return html

# ─── 5. PODCAST ──────────────────────────────────────────────
def generate_podcast(news_items, date_str):
    """Generate podcast script and audio with edge-tts."""
    script_path = os.path.join(AUDIO_DIR, "script.txt")
    
    # Get news headlines for the script
    headlines = []
    if news_items:
        for item in news_items[:5]:
            headlines.append(f"- {item[1]}")
    news_text = "\n".join(headlines) if headlines else "Hoy sin noticias destacadas."
    
    # Get world cup status
    try:
        wc_data = fetch("https://worldcup26.ir/get/games")
        wc_matches = json.loads(wc_data) if wc_data else []
        live_matches = [m for m in wc_matches if m.get("status") == "live"]
        wc_info = f"{len(live_matches)} partidos en vivo" if live_matches else "sin partidos en este momento"
    except:
        wc_info = "Mundial 2026 en curso"
    
    script = f"""Buenos días. Bienvenido al NEO Briefing de {date_str}.

Hoy en el mundo de la inteligencia artificial:
{news_text}

En el Mundial 2026, {wc_info}.

Para hoy, te dejo este prompt: imagina que eres un estratega de negocio con acceso a inteligencia artificial. Describe cómo automatizarías una tarea que consumes cada día. No pienses en la tecnología, piensa en el resultado.

Gracias por escuchar. Nos vemos mañana con más información. Que tengas un gran día."""
    
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    # Save script
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    log(f"  podcast script written ({len(script)} chars)")
    
    # Generate audio with edge-tts
    audio_path = AUDIO_FILE
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    # Use edge-tts via subprocess
    cmd = [
        sys.executable, "-m", "edge_tts",
        "--text", script,
        "--voice", "es-ES-AlvaroNeural",
        "--rate", "-5%",
        "--write-media", audio_path,
    ]
    
    log(f"  generating audio with edge-tts...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        log(f"  edge-tts error: {result.stderr[:200]}")
        return None, script, "—"
    
    if os.path.exists(audio_path):
        size = os.path.getsize(audio_path)
        log(f"  audio generated: {size/1024:.0f}KB")
        duration = estimate_duration(script)
        return audio_path, script, duration
    return None, script, "—"

def estimate_duration(text):
    """Rough estimate: ~150 words/min in Spanish."""
    words = len(text.split())
    mins = max(1, round(words / 150))
    secs = round(words / 150 * 60)
    return f"{mins}:{secs % 60:02d} min"

# ─── 6. PROMPT ───────────────────────────────────────────────
def get_prompt():
    prompts = [
        "Eres un estratega de negocio con acceso a cualquier herramienta de IA. Describe paso a paso cómo eliminarías una tarea repetitiva que consumes cada día. No te centres en la tecnología — céntrate en el resultado final.",
        "Actúa como un consultor de productividad personal. Analiza tu rutina matutina y sugiere tres automatizaciones con IA que podrían ahorrarte 30 minutos cada día.",
        "Imagina que tienes un asistente AI que puede leer todos tus correos, calendario y notas. Pídele que te prepare un resumen ejecutivo de tu día antes de que empiece.",
        "Eres un copywriter experto que usa IA. Describe cómo generarías 30 días de contenido para redes sociales a partir de un solo post del blog usando prompts en cadena.",
    ]
    return prompts[datetime.now().day % len(prompts)]

# ─── 7. QUOTE ────────────────────────────────────────────────
def get_quote():
    quotes = [
        "La mejor manera de predecir el futuro es crearlo. — Peter Drucker",
        "No se trata de tener tiempo, se trata de tener prioridades. — Stephen Covey",
        "La inteligencia artificial no reemplazará a los humanos, pero los humanos con IA reemplazarán a los que no la usen.",
        "La automatización no es perder el control, es ganar libertad.",
        "El mayor riesgo es no correr ningún riesgo. — Mark Zuckerberg",
        "La tecnología es solo una herramienta. La gente usa herramientas para mejorar sus vidas. — Tim Cook",
        "No sobrevive la especie más fuerte, sino la que mejor se adapta al cambio. — Charles Darwin",
    ]
    return quotes[datetime.now().day % len(quotes)]

# ─── 8. ASSEMBLE ─────────────────────────────────────────────
def assemble(params):
    """Read template, replace placeholders, write output."""
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()
    
    for key, value in params.items():
        html = html.replace("{{" + key + "}}", str(value))
    
    # Ensure output directory
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"  HTML written: {OUTPUT}")
    
    # Also copy to root if needed for GitHub Pages
    root_index = os.path.join(REPO_DIR, "briefing", "index.html")
    with open(root_index, "w", encoding="utf-8") as f:
        f.write(html)

# ─── 9. DEPLOY ───────────────────────────────────────────────
def deploy():
    """Commit and push to GitHub Pages."""
    log("  deploying...")
    
    # Git add
    subprocess.run(["git", "-C", REPO_DIR, "add", "briefing/"], capture_output=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"daily briefing {datetime.now().strftime('%Y-%m-%d %H:%M')}"], capture_output=True)
    
    # Push
    result = subprocess.run(["git", "-C", REPO_DIR, "push"], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        log("  deployed to neolabs.es/briefing/")
        return True
    else:
        error = result.stderr[:200] if result.stderr else "unknown"
        log(f"  deploy error: {error}")
        return False

# ─── MAIN ─────────────────────────────────────────────────────
def main():
    log("=== NEO DAILY BRIEFING ===")
    today = date.today()
    date_str = today.strftime("%d de %B de %Y")
    date_short = today.strftime("%d.%m.%Y")
    day_name = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][today.weekday()]
    week_num = today.isocalendar()[1]
    
    log("1. Fetching weather...")
    weather = get_weather()
    
    log("2. Fetching World Cup...")
    wc_html = get_world_cup()
    
    log("3. Fetching AI news...")
    news_html = get_ai_news()
    
    log("4. Fetching YouTube...")
    yt_html = get_youtube_videos()
    
    log("5. Generating prompt...")
    prompt = get_prompt()
    
    log("6. Generating quote...")
    quote = get_quote()
    
    log("7. Generating podcast...")
    result = generate_podcast([], date_str)
    if result and result[0]:
        audio_path, script, duration = result
        # Make path relative for HTML
        audio_url = "./podcast.mp3"
        topics = "Noticias AI · Mundial · Productividad"
    else:
        audio_url = ""
        duration = "—"
        topics = "No disponible"
    
    log("8. Assembling HTML...")
    now = datetime.now().strftime("%H:%M")
    
    params = {
        "DATE": date_str,
        "DATE_SHORT": date_short,
        "DAY_NAME": day_name,
        "WEEK_NUM": str(week_num),
        "WEATHER": weather,
        "WORLD_CUP": wc_html,
        "AI_NEWS": news_html,
        "YOUTUBE_VIDEOS": yt_html,
        "PROMPT": prompt,
        "QUOTE": quote,
        "PODCAST_AUDIO": audio_url if audio_url else "",
        "PODCAST_DURATION": duration,
        "PODCAST_TOPICS": topics,
        "GENERATED_AT": f"{date_str} · {now}",
    }
    
    assemble(params)
    
    log("9. Deploying...")
    deployed = deploy()
    
    log(f"\n✅ Briefing generado: neolabs.es/briefing/")
    if deployed:
        log("✅ Desplegado correctamente")
    else:
        log("⚠️  Deploy manual pendiente (git push)")
    
    return deployed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
