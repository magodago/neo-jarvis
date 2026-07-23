#!/usr/bin/env python3
"""
NEO Daily Briefing Generator v3
Briefing diario premium.
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

CHANNELS = [
    ("DotCSV", "UCOTko-zmnQTcOxSRdg5_uOQ"),
    ("Xavier Mitjana", "UCeu3sN4T72Fka1rhQFR447A"),
    ("Jon Hernández", "UCl5-lvQyfILb-l2abPk4Ntg"),
    ("DotCSV Lab", "UCy5znSnfMsDwaLlROnZ7Qbg"),
    ("Ringa Tech", "UCm9QZ70KuIVShztZ7HmE4NQ"),
    ("Victor Robles", "UCv85NiROLKddHa0fBATwTzw"),
]

# ─── SPANISH COUNTRY NAMES ───────────────────────────────────
# No more PAIS_ES or es() needed (World Cup removed)

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
            else: log(f"  fail: {url[:40]}.. {e}")
    return ""

def strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    return ' '.join(text.split())[:300]

# ─── 1. WEATHER ──────────────────────────────────────────────
def get_weather():
    """Fetch weather in Spanish."""
    wd_es = {
        "Clear": "Despejado", "Sunny": "Soleado", "Partly cloudy": "Parcialmente nublado",
        "Cloudy": "Nublado", "Overcast": "Cubierto", "Mist": "Niebla", "Fog": "Niebla",
        "Light rain": "Lluvia ligera", "Moderate rain": "Lluvia moderada",
        "Heavy rain": "Lluvia fuerte", "Light rain shower": "Chubascos ligeros",
        "Moderate or heavy rain shower": "Chubascos", "Patchy rain possible": "Posible lluvia",
        "Thundery outbreaks possible": "Posibles tormentas", "Light rain with thunder": "Tormenta ligera",
        "Moderate or heavy rain with thunder": "Tormenta fuerte",
    }
    try:
        data = fetch("https://wttr.in/Illescas?format=j1")
        if data:
            d = json.loads(data)
            cc = d['current_condition'][0]
            temp = cc['temp_C']
            desc_en = cc['weatherDesc'][0]['value']
            desc = wd_es.get(desc_en, desc_en)
            hum = cc['humidity']
            return f"{temp}°C · {desc} · Hum {hum}%"
    except: pass
    return "—"


# ─── 2. NEWS ES (solo IA, solo ayer/hoy) ────────────────────
AI_KEYWORDS = ["inteligencia artificial","ia","chatgpt","openai","deepseek","claude","anthropic",
               "gemini","google ai","meta ai","machine learning","aprendizaje automático",
               "neural","red neuronal","llm","modelo de lenguaje","gpt","ai agent",
               "agente","automatización","robótica","algoritmo","open source ai",
               "hugging face","notebooklm","veo","sora","midjourney","stable diffusion",
               "copilot","asistente","prompt","token","entrenar"]

def es_noticia_ia(title, desc):
    text = (title + " " + desc).lower()
    for kw in AI_KEYWORDS:
        if kw in text:
            return True
    return False

def get_ai_news():
    feeds = [
        ("Hipertextual", "https://hipertextual.com/feed"),
        ("WWWhatsnew", "https://wwwhatsnew.com/feed"),
        ("Xataka", "https://www.xataka.com/feed"),
    ]
    items, seen = [], set()
    today = date.today()
    
    for source, url in feeds:
        data = fetch(url)
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for item in root.iter("item"):
                title = item.findtext("title","").strip()
                link = item.findtext("link","").strip()
                desc = strip_html(item.findtext("description",""))
                pubdate_raw = item.findtext("pubDate","")
                
                if not title or not link: continue
                key = title.lower()[:40]
                if key in seen: continue
                seen.add(key)
                
                # Filter by AI keywords
                if not es_noticia_ia(title, desc): continue
                
                # Filter by date (yesterday or today)
                pub_date = None
                if pubdate_raw:
                    try:
                        # RSS date format: "Tue, 30 Jun 2026 12:00:00 GMT"
                        for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z",
                                    "%d %b %Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                            try:
                                pub_date = datetime.strptime(pubdate_raw.strip()[:25], fmt).date()
                                break
                            except: pass
                    except: pass
                
                age_ok = True
                if pub_date:
                    diff = (today - pub_date).days
                    if diff > 1: age_ok = False  # Solo ayer o hoy
                
                if not age_ok: continue
                
                pubdate_short = pubdate_raw[:16] if pubdate_raw else ""
                items.append({"source":source,"title":title,"link":link,"desc":desc[:500],"pubdate":pubdate_short})
                if len(items)>=6: break
            if len(items)>=6: break
        except Exception as e:
            log(f"  rss {source}: {e}")
    
    return items[:6]

def news_to_html(items):
    if not items: return "", []
    html = ""
    for i, item in enumerate(items):
        s = item["desc"].replace('"',"'")
        html += f"""<div class="news-card" onclick="openNewsModal({i})">
  <div class="news-card-img">📰</div>
  <div class="news-card-body">
    <div class="news-card-source">{item['source']}</div>
    <div class="news-card-title">{item['title'][:90]}</div>
    <div class="news-card-time">{item['pubdate']}</div>
  </div>
</div>"""
    return html, [{"source": i["source"],"title": i["title"],"desc": i["desc"][:800],"link": i["link"]} for i in items]

# ─── 3b. GENERAL NEWS (internacional, España) ────────────────
def get_world_news():
    """Fetch top headlines from BBC Mundo and El Pais."""
    feeds = [
        ("BBC Mundo", "https://feeds.bbci.co.uk/mundo/rss.xml"),
        ("El País", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
    ]
    items, seen = [], set()
    today = date.today()
    for source, url in feeds:
        data = fetch(url)
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for item in root.iter("item"):
                title = item.findtext("title","").strip()
                link = item.findtext("link","").strip()
                desc = strip_html(item.findtext("description",""))
                pubdate_raw = item.findtext("pubDate","")
                if not title or not link: continue
                key = title.lower()[:40]
                if key in seen: continue
                seen.add(key)
                pub_date = None
                if pubdate_raw:
                    for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z","%d %b %Y %H:%M:%S"]:
                        try:
                            pub_date = datetime.strptime(pubdate_raw.strip()[:25], fmt).date()
                            break
                        except: pass
                if pub_date and (today - pub_date).days > 2: continue
                # EXCLUDE sports/world-cup content (tournament ended)
                txt = (title + " " + desc).lower()
                if any(w in txt for w in ["mundial", "world cup", "fútbol", "selección española", "partido", "gol de", "liga de", "champions", "real madrid", "fc barcelona", "baloncesto", "tenis", "deporte", "atlético de madrid", "athletic"]):
                    continue
                items.append({"source":source,"title":title,"link":link,"desc":desc[:200]})
                if len(items)>=4: break
            if len(items)>=4: break
        except: pass
    return items[:4]

# ─── 3c. ENTERTAINMENT (cine, series) ────────────────────────
def get_entertainment():
    """Fetch latest movie/series news."""
    feeds = [
        ("Fotogramas", "https://www.fotogramas.es/rss/news.xml"),
        ("20 Minutos", "https://www.20minutos.es/rss/cine/"),
    ]
    items, seen = [], set()
    today = date.today()
    for source, url in feeds:
        data = fetch(url)
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for item in root.iter("item"):
                title = item.findtext("title","").strip()
                link = item.findtext("link","").strip()
                if not title or not link: continue
                key = title.lower()[:40]
                if key in seen: continue
                seen.add(key)
                pubdate_raw = item.findtext("pubDate","")
                pub_date = None
                if pubdate_raw:
                    for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z","%d %b %Y %H:%M:%S"]:
                        try:
                            pub_date = datetime.strptime(pubdate_raw.strip()[:25], fmt).date()
                            break
                        except: pass
                if pub_date and (today - pub_date).days > 3: continue
                txt = title.lower()
                if any(w in txt for w in ["mundial", "fútbol", "liga de", "champions", "real madrid", "fc barcelona"]): continue
                items.append({"source":source,"title":title,"link":link})
                if len(items)>=3: break
            if len(items)>=3: break
        except: pass
    return items[:3]

# ─── 4. YOUTUBE ──────────────────────────────────────────────
def get_youtube_yesterday():
    """Only videos from yesterday, deduplicated by video ID."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    html = ""
    seen = set()
    for name, ch_id in CHANNELS:
        data = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}")
        if not data: continue
        try:
            root = ElementTree.fromstring(data)
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                title = entry.findtext("{http://www.w3.org/2005/Atom}title","")[:80]
                vid = entry.findtext("{http://www.youtube.com/xml/schemas/2015}videoId","")
                pub = entry.findtext("{http://www.w3.org/2005/Atom}published","")[:10]
                if not vid or vid in seen: continue
                seen.add(vid)
                if pub:
                    try:
                        pub_date = datetime.strptime(pub[:10],"%Y-%m-%d").date()
                        if pub_date != yesterday: continue
                    except: continue
                html += f"""<a class="video-card" href="https://youtube.com/watch?v={vid}" target="_blank" rel="noopener">
  <div class="video-thumb"><img src="https://img.youtube.com/vi/{vid}/mqdefault.jpg" alt="" loading="lazy" onerror="this.style.display='none'"></div>
  <div class="video-info">
    <div class="video-title">{title}</div>
    <div class="video-channel">{name}</div>
    <div class="video-date">Ayer</div>
  </div>
</a>"""
        except: pass
    if not html:
        html = '<p style="color:var(--text-muted);font-size:.8rem;padding:12px">Ningún canal publicó video ayer</p>'
    return html

# ─── 5. PODCAST ──────────────────────────────────────────────
def generate_podcast(news_items, date_str, weather="", world_news=None):
    """Generate podcast with actual content using DeepSeek Flash."""
    # Read API key from .env file
    ds_key = ""
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    ds_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    
    # Incluir título + descripción de cada noticia IA
    news_text = ""
    for i in news_items[:3]:
        t = i.get('title','')
        d = i.get('desc','')
        news_text += f"- {t}"
        if d:
            news_text += f": {d[:200]}"
        news_text += "\n"
    
    world_text = ""
    for i in (world_news or [])[:3]:
        t = i.get('title','')
        d = i.get('desc','')
        world_text += f"- {t}"
        if d:
            world_text += f": {d[:200]}"
        world_text += "\n"

    today_dt = datetime.now()
    wd = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"][today_dt.weekday()]
    prompt = f"""Eres la voz del podcast matutino 'Daily Pulse' que habla directamente a David. Genera un guión en español, natural y directo. Máximo 350 palabras.

Hoy es {date_str} ({wd}). Clima: {weather or "temperatura agradable"}.

ESTRUCTURA EXACTA - 3 secciones:

SALUDO (obligatorio, 1 frase): Empieza siempre con "Buenos días David" o "Muy buenos días David" - el tono es cercano, como un amigo.

SECCIÓN 1 - IA (3-4 frases):
Explica las noticias de IA con un breve resumen, no solo el titular. Qué ha pasado y por qué importa.
Noticias y datos:
{news_text if news_text else "últimas novedades en IA"}

|SECCIÓN 2 - ACTUALIDAD (2-3 frases):
Noticias internacionales y de España. Explica cada una con contexto breve.
Datos:
{world_text if world_text else "actualidad internacional"}

|DESPEDIDA (obligatorio, 1 frase): Termina siempre con algo como "Que tengas un gran día, David", "A darle duro hoy, David", "Nos escuchamos mañana, David".

REGLAS: No uses asteriscos, negritas, guiones ni markdown. No digas "en el mundo de la tecnología". Habla como si le contaras esto a David tomando un café. Explica el contexto de cada noticia, no te limites a leer titulares."""

    script = None
    if ds_key:
        try:
            data = json.dumps({
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.7,
            }).encode()
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=data,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {ds_key}"}
            )
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read())
            script = result["choices"][0]["message"]["content"].strip()
            # Strip markdown
            import re as _re
            script = _re.sub(r'\*\*(.+?)\*\*', r'\1', script)
            script = _re.sub(r'\*(.+?)\*', r'\1', script)
            script = _re.sub(r'^#+\s*', '', script, flags=_re.MULTILINE)
            script = _re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', script)
            script = _re.sub(r'_{2,}', '', script)
            script = _re.sub(r'`([^`]+)`', r'\1', script)
            log(f"  script by DeepSeek ({len(script)} chars)")
            
            # Forzar cierre si se cortó antes de la despedida
            despedidas = ["que tengas un gran día", "a darle duro", "nos escuchamos mañana", 
                         "que pases un buen día", "hasta mañana", "un abrazo"]
            if not any(d in script.lower() for d in despedidas):
                script = script.rstrip().rstrip(',').rstrip('.').rstrip('…')
                if not script.endswith('.'):
                    script += '.'
                script += "\n\nQue tengas un gran día, David. Nos escuchamos mañana."
                log(f"  cierre forzado añadido")
        except Exception as e:
            log(f"  DeepSeek error: {e}")
    
    if not script:
        news_fb = ". ".join(i['title'][:50] for i in news_items[:5]) if news_items else "últimas noticias de IA"
        w = f"El clima hoy: {weather}. " if weather else ""
        script = f"Buenos días. {w}{news_fb}. Tip del día: usa un asistente IA para resumir tus correos cada mañana y empieza sin saturación. Nos escuchamos mañana."
    
    os.makedirs(AUDIO_DIR, exist_ok=True)
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f: f.write(script)
    
    if os.path.exists(AUDIO_FILE): os.remove(AUDIO_FILE)
    cmd = [sys.executable, "-m", "edge_tts", "-f", SCRIPT_FILE,
           "-v", "es-ES-AlvaroNeural", "--rate=-5%", "--write-media", AUDIO_FILE]
    log(f"  audio...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        log(f"  audio error: {r.stderr[:200]}")
        return "no-audio","—"
    if os.path.exists(AUDIO_FILE):
        log(f"  audio: {os.path.getsize(AUDIO_FILE)/1024:.0f}KB")
        secs = max(15, round(len(script.split())/150*60))
        return "./podcast.mp3", f"{secs//60:02d}:{secs%60:02d}"
    return "no-audio","—"

# ─── 6. PROMPT ───────────────────────────────────────────────
def get_prompt():
    p = ["Diseña un flujo donde tres agentes AI trabajen en paralelo: uno investiga, otro escribe, otro revisa. Un solo resultado final.",
         "Describe cómo usarías IA para transformar una reunión de 1h en notas, acciones y resumen ejecutivo. Sin escribir nada tú.",
         "Crea un sistema donde cada email que recibes se responde automáticamente con el tono y conocimiento de tu negocio.",
         "Imagina un asistente que conoce tu calendario, correos y proyectos. Cada mañana te da 3 decisiones que debes tomar. Nada más.",
         "Diseña un pipeline donde una idea en voz se convierte en tweet, hilo, artículo y video. Todo automático, todo con IA."]
    return p[datetime.now().day % len(p)]

def get_quote():
    q = ["La mejor manera de predecir el futuro es crearlo.",
         "No se trata de tener tiempo, se trata de tener prioridades.",
         "La IA no reemplazará a los humanos, pero los humanos con IA reemplazarán a los que no la usen.",
         "La automatización no es perder el control, es ganar libertad."]
    return q[datetime.now().day % len(q)]

# ─── 7. ASSEMBLE ─────────────────────────────────────────────
def assemble(params):
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()
    for k,v in params.items():
        html = html.replace("{{"+k+"}}", str(v))
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"  HTML: {len(html)} bytes")

def deploy():
    log("  deploying...")
    subprocess.run(["git","-C",REPO_DIR,"add","briefing/"], capture_output=True)
    subprocess.run(["git","-C",REPO_DIR,"commit","-m",f"briefing {datetime.now().strftime('%Y-%m-%d')}"], capture_output=True)
    # Intentar push con timeout más largo + reintento
    for attempt in range(2):
        try:
            r = subprocess.run(["git","-C",REPO_DIR,"push"], capture_output=True,text=True,timeout=60)
            if r.returncode==0: return True
            log(f"  push attempt {attempt+1}: {r.stderr[:100]}")
        except subprocess.TimeoutExpired:
            log(f"  push attempt {attempt+1}: timeout")
    return False

# ─── MAIN ─────────────────────────────────────────────────────
def main():
    log("=== NEO DAILY BRIEFING v3 ===")
    today = date.today()
    date_str = today.strftime("%d de %B de %Y")
    date_short = today.strftime("%d.%m.%Y")
    day_name = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"][today.weekday()]
    week_num = today.isocalendar()[1]
    
    log("1. Weather..."); weather = get_weather()
    log("2. News..."); news_items = get_ai_news()
    news_html, news_data = news_to_html(news_items)
    log("4. YouTube..."); yt = get_youtube_yesterday()
    log("5. Prompt/Quote..."); prompt = get_prompt(); quote = get_quote()
    log("6. World news..."); w_news = get_world_news()
    log("6. World news..."); w_news = get_world_news()
    log("7. Podcast..."); audio_url, duration = generate_podcast(news_items, date_str, weather, w_news)
    
    params = {
        "DATE": date_str,
        "DATE_SHORT": date_short,
        "WEEKDAY": day_name,
        "WEEK": str(week_num),
        "WEATHER": weather,
        "HERO_IMG": "https://images.unsplash.com/photo-1604079628040-94301bb21b91?w=1400&q=80",
        "QUOTE": quote,
        "PODCAST_DURATION": duration,
        "NEWS_CONTENT": news_html,
        "NEWS_DATA": json.dumps(news_data, ensure_ascii=False),
        "VIDEOS_CONTENT": yt,
        "PROMPT": prompt,
        "TIME": datetime.now().strftime("%H:%M"),
    }
    
    log("9. Assembly..."); assemble(params)
    log("10. Deploy..."); ok = deploy()
    log(f"\n✅ https://magodago.github.io/neo-jarvis/briefing/")
    return ok

if __name__ == "__main__":
    main()
