#!/usr/bin/env python3
"""
NEO Daily Briefing Generator v3
Briefing diario premium con mundial completo (resultados, goleadores, clasificación, próximos).
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
PAIS_ES = {
    "Mexico":"México","South Africa":"Sudáfrica","South Korea":"Corea del Sur",
    "Czech Republic":"República Checa","Switzerland":"Suiza","Canada":"Canadá",
    "Bosnia and Herzegovina":"Bosnia","Qatar":"Catar","Brazil":"Brasil",
    "Morocco":"Marruecos","Scotland":"Escocia","Haiti":"Haití",
    "United States":"EE.UU.","Australia":"Australia","Paraguay":"Paraguay",
    "Turkey":"Turquía","Germany":"Alemania","Ivory Coast":"Costa de Marfil",
    "Ecuador":"Ecuador","Curaçao":"Curazao","Netherlands":"Países Bajos",
    "Japan":"Japón","Sweden":"Suecia","Tunisia":"Túnez","Belgium":"Bélgica",
    "Egypt":"Egipto","Iran":"Irán","New Zealand":"Nueva Zelanda",
    "Spain":"España","Cape Verde":"Cabo Verde","Uruguay":"Uruguay",
    "Saudi Arabia":"Arabia Saudí","France":"Francia","Norway":"Noruega",
    "Senegal":"Senegal","Iraq":"Irak","Argentina":"Argentina","Austria":"Austria",
    "Algeria":"Argelia","Jordan":"Jordania","Colombia":"Colombia",
    "Portugal":"Portugal","Democratic Republic of the Congo":"R.D. Congo",
    "Uzbekistan":"Uzbekistán","England":"Inglaterra","Croatia":"Croacia",
    "Ghana":"Ghana","Panama":"Panamá","Italy":"Italia","Poland":"Polonia",
    "Denmark":"Dinamarca","Ukraine":"Ucrania","Wales":"Gales",
    "Serbia":"Serbia","Switzerland":"Suiza","Cameroon":"Camerún",
    "Nigeria":"Nigeria","Mali":"Mali","Togo":"Togo",
}

def es(name):
    return PAIS_ES.get(name, name)

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

def fetch_json(url):
    data = fetch(url)
    if not data: return []
    raw = json.loads(data)
    if isinstance(raw, dict):
        for v in raw.values():
            if isinstance(v, list): return v
    return raw if isinstance(raw, list) else []

def to_es_time(local_date_str):
    """Convert venue local time (US/Mexico) to Spanish time (CEST UTC+2) by adding 6h."""
    if not local_date_str: return ""
    try:
        dt = datetime.strptime(local_date_str, "%m/%d/%Y %H:%M")
        from datetime import timedelta
        dt_es = dt + timedelta(hours=6)
        wd = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"][dt_es.weekday()]
        return f"{wd} {dt_es.day}/{dt_es.month} · {dt_es.strftime('%H:%M')}"
    except:
        return local_date_str

def strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    return ' '.join(text.split())[:300]

def parse_scorers(s):
    """Parse scorer strings like {\"Player 27'\",\"Player 75'\"}"""
    if not s or s == 'null': return []
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
    parts = re.findall(r'"([^"]*)"', s)
    return parts if parts else [s.strip().strip('"')]

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

# ─── 2. WORLD CUP (KNOCKOUT STAGE) ──────────────────────────
ROUND_ES = {"r32":"1/32","r16":"1/16","qf":"Cuartos","sf":"Semifinal","final":"Final","third":"3er Puesto"}

def get_world_cup():
    today = date.today()
    yesterday = today - timedelta(days=1)
    today_str = today.strftime("%m/%d/%Y")
    yesterday_str = yesterday.strftime("%m/%d/%Y")
    current_round = ""

    matches = fetch_json("https://worldcup26.ir/get/games")
    if not matches: return fallback_wc()
    
    # Filter to knockout matches only (skip group stage)
    ko_matches = [m for m in matches if m.get('type') != 'group']
    if not ko_matches: return fallback_wc()
    
    html = ""
    from random import randint as _ri
    _ci = 0
    
    # ── A. YESTERDAY'S RESULTS ──
    ayer = [m for m in ko_matches if m.get('local_date','').startswith(yesterday_str) and m.get('finished','FALSE').upper()=='TRUE']
    # Also include earlier knockout matches that weren't shown yet (completed in last 3 days)
    earlier = [m for m in ko_matches if m.get('finished','FALSE').upper()=='TRUE' and not m.get('local_date','').startswith(yesterday_str) and not m.get('local_date','').startswith(today_str)]
    earlier.sort(key=lambda m: m.get('local_date',''), reverse=True)
    
    if ayer or earlier:
        html += '<div class="section-sub" style="margin-bottom:10px">Resultados</div>'
        
        # Show all recent knockout results (up to 8)
        all_res = sorted(ayer + earlier, key=lambda m: m.get('local_date',''), reverse=True)[:6]
        
        for m in all_res:
            home = es(m.get("home_team_name_en","?"))
            away = es(m.get("away_team_name_en","?"))
            hs = m.get("home_score","0")
            as_ = m.get("away_score","0")
            typ = ROUND_ES.get(m.get("type",""), m.get("type",""))
            h_sc = parse_scorers(m.get("home_scorers",""))
            a_sc = parse_scorers(m.get("away_scorers",""))
            ldate = m.get("local_date","")
            
            # Format date in Spanish time
            dstr = to_es_time(ldate) if ldate else ""
            dstr_short = dstr.split("·")[0].strip() if "·" in dstr else dstr
            
            scorers_html = ""
            if h_sc:
                scorers_html += f'<div style="font-size:.62rem;color:#f97316;margin-top:3px">⚽ {home}: {", ".join(h_sc[:3])}</div>'
            if a_sc:
                scorers_html += f'<div style="font-size:.62rem;color:#f97316">⚽ {away}: {", ".join(a_sc[:3])}</div>'
            
            # Determine winner for bold
            home_won = int(hs) > int(as_) if hs.isdigit() and as_.isdigit() else False
            
            html += f"""
<div class="wc-card" style="--i:{_ci};--float-dur:{_ri(35,55)/10}s">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <div class="wc-status finished">FINAL</div>
    <span style="font-size:.6rem;color:#f97316">{typ} · {dstr_short}</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div style="flex:1"><span style="font-size:.78rem;color:#fff;font-weight:600">{home}</span></div>
    <div style="font-family:Syne;font-size:1.2rem;font-weight:700;color:#fff;margin:0 12px">{hs}–{as_}</div>
    <div style="flex:1;text-align:right"><span style="font-size:.78rem;color:#fff;font-weight:600">{away}</span></div>
  </div>
  {scorers_html}
</div>"""
            _ci += 1
    
    # ── B. TODAY'S MATCHES ──
    hoy = [m for m in ko_matches if m.get('local_date','').startswith(today_str)]
    if hoy:
        html += f'<div class="section-sub" style="margin-top:14px;margin-bottom:10px">Partidos de hoy</div>'
        for m in hoy:
            home = es(m.get("home_team_name_en","?"))
            away = es(m.get("away_team_name_en","?"))
            typ = ROUND_ES.get(m.get("type",""), m.get("type",""))
            ldate = m.get("local_date","")
            hs = m.get("home_score","0")
            as_ = m.get("away_score","0")
            elapsed = m.get("time_elapsed","").lower()
            is_live = bool(re.match(r"^\d+", elapsed))
            
            # Time in Spanish time
            time_str = to_es_time(ldate) if ldate else ""
            time_short = time_str.split("·")[-1].strip() if "·" in time_str else time_str
            
            if is_live:
                status = f'<div class="wc-status live">EN VIVO · {elapsed}</div>'
                score = f'<div style="font-family:Syne;font-size:1.2rem;font-weight:700;color:#fff;margin:0 12px"><span class="live-dot"></span>{hs}–{as_}</div>'
            else:
                status = f'<div class="wc-status pending">{time_short}</div>'
                score = f'<div style="font-family:Syne;font-size:.8rem;font-weight:600;color:var(--muted);margin:0 12px">{typ}</div>'
            
            html += f"""
<div class="wc-card" style="--i:{_ci};--float-dur:{_ri(35,55)/10}s">
  <div class="wc-match">
    <div class="wc-team home"><span class="wc-team-name">{home}</span></div>
    {score}
    <div class="wc-team away"><span class="wc-team-name">{away}</span></div>
  </div>
  {status}
</div>"""
            _ci += 1
    
    # ── C. UPCOMING (next 4, not today) ──
    prox = [m for m in ko_matches if not m.get('local_date','').startswith(today_str) and not m.get('local_date','').startswith(yesterday_str) and m.get('finished','FALSE').upper()!='TRUE' and m.get('home_team_name_en') and m.get('away_team_name_en')]
    prox.sort(key=lambda m: m.get('local_date',''))
    
    if prox:
        html += f'<div class="section-sub" style="margin-top:14px;margin-bottom:10px">Próximos partidos</div>'
        for m in prox[:4]:
            home = es(m.get("home_team_name_en","?"))
            away = es(m.get("away_team_name_en","?"))
            typ = ROUND_ES.get(m.get("type",""), m.get("type",""))
            ldate = m.get("local_date","")
            
            # Date in Spanish time
            dstr = to_es_time(ldate) if ldate else ""
            
            html += f"""
<div class="wc-card" style="--i:{_ci};--float-dur:{_ri(35,55)/10}s">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div style="flex:1"><span style="font-size:.78rem;color:#fff;font-weight:500">{home}</span></div>
    <div style="text-align:center;margin:0 10px">
      <div style="font-family:Syne;font-size:.65rem;font-weight:600;color:#f97316">{typ}</div>
      <div style="font-size:.6rem;color:#f97316">{dstr}</div>
    </div>
    <div style="flex:1;text-align:right"><span style="font-size:.78rem;color:#fff;font-weight:500">{away}</span></div>
  </div>
</div>"""
            _ci += 1
    
    html += f'<a href="https://www.fifa.com/tournaments/mens/worldcup/usa-canada-mexico2026/" class="wc-more" target="_blank" rel="noopener">Ver todos los partidos →</a>'
    return html, current_round

def fallback_wc():
    return '<div class="wc-card" style="--i:0;--float-dur:4s"><p style="color:#f97316;font-size:.8rem">Mundial 2026 · 48 equipos · 16 sedes</p></div>'

# ─── 3. NEWS ES (solo IA, solo ayer/hoy) ────────────────────
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
                items.append({"source":source,"title":title,"link":link,"desc":desc[:200],"pubdate":pubdate_short})
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
    return html, [{"source":i["source"],"title":i["title"],"desc":i["desc"][:500],"link":i["link"]} for i in items]

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
def generate_podcast(news_items, date_str, weather="", world_news=None, entertainment=None):
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
    
    # Collect yesterday's WC results for the script
    results_text = ""
    try:
        matches = fetch_json("https://worldcup26.ir/get/games")
        ko = [m for m in matches if m.get('type') != 'group' and m.get('finished','FALSE').upper()=='TRUE' and m.get('home_team_name_en')]
        ko.sort(key=lambda m: m.get('local_date',''), reverse=True)
        lines = []
        for m in ko[:4]:
            h, a = es(m["home_team_name_en"]), es(m["away_team_name_en"])
            lines.append(f"{h} {m.get('home_score','?')}–{m.get('away_score','?')} {a}")
        if lines: results_text = "Mundial: " + ". ".join(lines) + "."
    except: pass
    
    news_text = ". ".join(i['title'][:60] for i in news_items[:3]) if news_items else ""
    world_text = ". ".join(i['title'][:60] for i in (world_news or [])[:3]) if world_news else ""
    ent_text = ". ".join(i['title'][:60] for i in (entertainment or [])[:3]) if entertainment else ""

    today_dt = datetime.now()
    wd = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"][today_dt.weekday()]
    prompt = f"""Eres la voz del podcast matutino 'Daily Pulse' que habla directamente a David. Genera un guión en español, natural y directo. Máximo 350 palabras.

Hoy es {date_str} ({wd}). Clima: {weather or "temperatura agradable"}.

ESTRUCTURA EXACTA - 4 secciones:

SALUDO (obligatorio, 1 frase): Empieza siempre con "Buenos días David" o "Muy buenos días David" - el tono es cercano, como un amigo.

SECCIÓN 1 - IA EXPRÉS (2-3 frases):
Solo lo relevante de ayer en IA. Nombres concretos (OpenAI, Anthropic, Google, ChatGPT, Claude...).
Datos: {news_text if news_text else "últimas novedades en IA"}

SECCIÓN 2 - EL MUNDO EN 60 SEGUNDOS (2-3 frases):
Noticias internacionales y de España. Titulares concretos.
Datos: {world_text if world_text else "actualidad internacional"}

SECCIÓN 3 - CARTELERA (2-3 frases):
Estrenos de cine y series. Títulos concretos.
Datos: {ent_text if ent_text else "novedades de cine y series"}

SECCIÓN 4 - ARRANQUE (1-2 frases):
Cierre con energía para empezar el día. Una frase corta.

DESPEDIDA (obligatorio, 1 frase): Termina siempre con algo como "Que tengas un gran día, David", "A darle duro hoy, David", "Nos escuchamos mañana, David".

Mundial: {results_text if results_text else "El Mundial 2026 sigue con los octavos de final."}

REGLAS: No uses asteriscos, negritas, guiones ni markdown. No digas "en el mundo de la tecnología" ni "consulta nuestra web". Habla como si le contaras esto a David tomando un café."""

    script = None
    if ds_key:
        try:
            data = json.dumps({
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 350,
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
        except Exception as e:
            log(f"  DeepSeek error: {e}")
    
    if not script:
        news_fb = ". ".join(i['title'][:50] for i in news_items[:5]) if news_items else "últimas noticias de IA"
        w = f"El clima hoy: {weather}. " if weather else ""
        script = f"Buenos días. {w}{news_fb}. {results_text if results_text else 'El Mundial 2026 sigue con los octavos de final.'} Tip del día: usa un asistente IA para resumir tus correos cada mañana y empieza sin saturación. Nos escuchamos mañana."
    
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
    r = subprocess.run(["git","-C",REPO_DIR,"push"], capture_output=True,text=True,timeout=30)
    if r.returncode==0: return True
    log(f"  push: {r.stderr[:200]}")
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
    log("2. World Cup..."); wc_html, wc_round = get_world_cup()
    log("3. News..."); news_items = get_ai_news(); log(f"   {len(news_items)} items, wc round: {wc_round}")
    news_html, news_data = news_to_html(news_items)
    log("4. YouTube..."); yt = get_youtube_yesterday()
    log("5. Prompt/Quote..."); prompt = get_prompt(); quote = get_quote()
    log("6. World news..."); w_news = get_world_news()
    log("7. Entertainment..."); ent = get_entertainment()
    log("8. Podcast..."); audio_url, duration = generate_podcast(news_items, date_str, weather, w_news, ent)
    
    params = {
        "DATE": date_str,
        "DATE_SHORT": date_short,
        "WEEKDAY": day_name,
        "WEEK": str(week_num),
        "WEATHER": weather,
        "HERO_IMG": "https://images.unsplash.com/photo-1604079628040-94301bb21b91?w=1400&q=80",
        "QUOTE": quote,
        "PODCAST_DURATION": duration,
        "WC_ROUND": wc_round or "Eliminatorias",
        "WC_CONTENT": wc_html,
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
