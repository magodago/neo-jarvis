#!/usr/bin/env python3
"""Daily article generator v3 — high-quality SEO content via DeepSeek."""
import json, os, subprocess, random, re, sys
from html import escape as h_escape
from datetime import datetime
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

# Load DeepSeek API key
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_KEY:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("DEEPSEEK_API_KEY="):
                DEEPSEEK_KEY = line.split("=", 1)[1].strip().strip("'\"")
DEEPSEEK_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1") + "/chat/completions"

NICHES = [
    {"slug":"productividad","name":"Productividad","brand":"#d4a853","brand_dark":"#b8922f","brand_light":"#f0d68a","payhip":"EYojF",
     "hero_img":"photo-1497366216548-37526070297c"},
    {"slug":"finanzas","name":"Finanzas","brand":"#66bb6a","brand_dark":"#388e3c","brand_light":"#a5d6a7","payhip":"uP62G",
     "hero_img":"photo-1554224155-8d04cb21cd6c"},
    {"slug":"marketing","name":"Marketing","brand":"#42a5f5","brand_dark":"#1976d2","brand_light":"#90caf9","payhip":"Q5RYA",
     "hero_img":"photo-1557838923-2985c318be48"},
    {"slug":"programacion","name":"Programación","brand":"#ab47bc","brand_dark":"#7b1fa2","brand_light":"#ce93d8","payhip":"XTEG5",
     "hero_img":"photo-1461749280684-dccba630e2f6"},
    {"slug":"estudiantes","name":"Educación","brand":"#ffa726","brand_dark":"#ef6c00","brand_light":"#ffcc80","payhip":"M3eqn",
     "hero_img":"photo-1488190211105-8b0e65b80b4e"},
    {"slug":"rrhh","name":"RRHH","brand":"#ec407a","brand_dark":"#c2185b","brand_light":"#f48fb1","payhip":"KragB",
     "hero_img":"photo-1600880292203-757bb62b4baf"},
]

IMAGES = [
    "photo-1555066931-4365d14bab8c","photo-1512314889357-e157c22f938d","photo-1454165804606-c3d57bc86b40",
    "photo-1434030216411-0b793f4b4173","photo-1555421689-d68471e189f2","photo-1450101499163-c8848c66ca85",
    "photo-1552664730-d307ca884978","photo-1551288049-bebda4e38f71","photo-1522071820081-009f0129c71c",
    "photo-1555949963-aa79dcee981c","photo-1552581234-26160f608093","photo-1460925895917-afdab827c52f",
]

ARTICLE_TYPES = [
    {"type":"guia","tag":"Guía",
     "titles":["Guía completa de {} con inteligencia artificial","Los mejores prompts de IA para {}",
               "Todo lo que necesitas saber sobre {} con IA","Estrategia definitiva de {} potenciada con IA"],
     "desc":"Guía detallada sobre {} con prompts de IA probados y refinados."},
    {"type":"tutorial","tag":"Tutorial",
     "titles":["Cómo {} con IA paso a paso","Guía práctica para {} usando inteligencia artificial",
               "Aprende a {} con prompts de IA","Tutorial práctico de {} con ChatGPT y Claude"],
     "desc":"Aprende paso a paso cómo {} con la ayuda de la inteligencia artificial."},
    {"type":"noticia","tag":"Noticia",
     "titles":["Novedades de IA para {}: lo que cambia en 2026","Nueva actualización de ChatGPT afecta a {}",
               "Lo último en IA para {} que no puedes ignorar","Breakthrough en IA: nuevo impacto en {}"],
     "desc":"Las últimas novedades de inteligencia artificial aplicadas a {}."},
    {"type":"comparativa","tag":"Comparativa",
     "titles":["ChatGPT vs Claude vs Gemini: cuál es mejor para {}","Comparativa 2026: mejores herramientas para {}"],
     "desc":"Comparamos las principales herramientas de IA para ayudarte a elegir la mejor opción."},
]

TOPICS = {
    "productividad":["organizar tu agenda","gestionar tu tiempo","priorizar tareas","automatizar informes",
                     "planificar proyectos","gestionar el correo","preparar reuniones","tomar decisiones"],
    "finanzas":["crear un presupuesto","analizar tus gastos","planificar tu jubilación","optimizar tu fiscalidad",
                "gestionar inversiones","reducir deudas","planificar metas financieras"],
    "marketing":["crear contenido SEO","analizar tu audiencia","automatizar emails","optimizar campañas",
                 "crear embudos de venta","hacer segmentación","analizar métricas"],
    "programacion":["debuggear código","revisar pull requests","escribir tests","documentar APIs",
                    "refactorizar código","revisar seguridad","optimizar rendimiento"],
    "estudiantes":["resumir textos académicos","preparar exámenes","escribir ensayos","organizar tu estudio",
                   "crear flashcards","hacer presentaciones","gestionar el tiempo de estudio"],
    "rrhh":["seleccionar candidatos","evaluar desempeño","redactar ofertas","planificar formación",
            "mejorar clima laboral","hacer onboarding","gestionar el talento"],
}

def pick(seq, day=None):
    if day is not None:
        return seq[day % len(seq)]
    return random.choice(seq)

def generate_via_deepseek(niche, topic, article_type):
    """Generate high-quality article via DeepSeek API."""
    if not DEEPSEEK_KEY:
        print("ERROR: No DeepSeek API key found")
        return None

    prompt = f"""Eres un escritor de blogs profesional y experto en {niche['name']}. Tu audiencia son profesionales hispanohablantes que buscan contenido útil y bien fundamentado. NO eres una IA — escribes como un humano con experiencia real.

Escribe un artículo sobre: {topic}
Nichos: {niche['name']}
Tipo: {article_type}

REQUISITOS DE CALIDAD (NO NEGOCIABLES):
1. **Longitud**: 900-1200 palabras. Con contenido real, no relleno.
2. **Estructura**: Introducción convincente → 3-4 secciones H2 con contenido sustancial → Conclusión con llamado a la acción.
3. **Cada sección H2 debe incluir un prompt práctico** con esta sintaxis PROMPT: seguido del prompt listo para copiar y pegar.
4. **Investiga mentalmente**: No generalices. Da pasos concretos, herramientas reales, métricas específicas.
5. **Ejemplos prácticos**: Al menos 2 ejemplos concretos aplicados a situaciones reales.
6. **Errores comunes**: Una sección dedicada a errores que comete la gente y cómo evitarlos.
7. **Datos actualizados 2026**: Referencias a versiones actuales de ChatGPT, Claude, Gemini.

REGLAS DE ESTILO:
- Tono profesional pero cercano. Como un consultor que habla con un colega.
- Ortografía correcta del español: á, é, í, ó, ú, ñ, ¿, ¡. OBLIGATORIO.
- Sin markdown. Sin HTML en el contenido. Sin pensamientos internos.
- Sin autoreferencias ("como hemos visto", "como mencioné antes").
- Vocabulario variado. Evita repetir palabras a menos de 3 frases.
- Los prompts deben tener variables entre [corchetes] para personalizar.

Formato de salida (responde SOLO esto, sin prefijos):
## [Título sección]
Contenido de la sección en párrafos.

PROMPT: [texto del prompt práctico]

Sigue esta estructura exacta. Mínimo 3 secciones con prompt."""

    payload = json.dumps({
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": "Eres un escritor de blogs experto. Escribes artículos profundos, prácticos y bien documentados. Tu ortografía es perfecta. Respondes ÚNICAMENTE con el cuerpo del artículo, sin prefijos ni explicaciones."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    })

    try:
        resp = subprocess.run(
            ["curl", "-s", "--max-time", "120",
             DEEPSEEK_URL,
             "-H", "Content-Type: application/json",
             "-H", f"Authorization: Bearer {DEEPSEEK_KEY}",
             "-d", payload],
            capture_output=True, text=True, timeout=130
        )
        if resp.returncode != 0:
            print(f"curl error: {resp.stderr[:200]}")
            return None
        
        data = json.loads(resp.stdout)
        if "choices" not in data:
            print(f"API error: {data.get('error', {}).get('message', str(data)[:200])}")
            return None
        
        content = data["choices"][0]["message"]["content"].strip()
        
        # Strip thinking prefixes
        thinking_prefixes = ["Thinking...", "thinking", "**Pensamiento:**", "**Razonamiento:**", 
                           "Here's", "Claro,", "Por supuesto,"]
        for prefix in thinking_prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # Check minimum length
        word_count = len(content.split())
        if word_count < 400:
            print(f"Article too short ({word_count} words), skipping")
            return None
            
        print(f"Generated {word_count} words via DeepSeek")
        return content
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except subprocess.TimeoutExpired:
        print("DeepSeek timeout")
        return None
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return None

def generate_fallback(niche, topic):
    """Generate a reasonable fallback article when API fails."""
    sections_data = {
        "introduccion": f"Si trabajas con inteligencia artificial, sabes que la calidad del resultado depende casi por completo de la calidad del input. Para {topic}, la diferencia entre un resultado aceptable y uno excepcional está en los detalles del prompt que escribes. En este artículo te voy a mostrar exactamente cómo estructurar tus prompts para obtener resultados profesionales, con ejemplos concretos que puedes usar hoy mismo.",
        "secciones": [
            ("El prompt base que necesitas", f"Para empezar a trabajar en {topic}, necesitas un prompt bien estructurado. La clave está en darle a la IA suficiente contexto sin abrumarla. Este es el prompt base que recomiendo para cualquier profesional:\n\nPROMPT: Eres un consultor experto en {niche['name']} con más de 10 años de experiencia. Necesito tu ayuda para {topic}. Dame 3 enfoques diferentes, evaluando pros y contras de cada uno, y recomiéndame el mejor con un plan de acción concreto de 5 pasos. Incluye métricas para medir el éxito de cada enfoque."),
            ("Cómo refinar los resultados", "El primer resultado rara vez es el definitivo. La clave está en iterar. Una vez que tengas el primer output, usa este prompt para refinarlo:\n\nPROMPT: Revisa el plan anterior. Identifica qué partes pueden no funcionar en mi caso específico, donde mi contexto es: [describe tu situación actual]. Adáptalo a mi realidad, teniendo en cuenta limitaciones de [tiempo/recursos/conocimiento]. Dame alternativas para los puntos más débiles."),
            ("Crea un sistema que funcione solo", "El verdadero poder de la IA no está en usarla una vez, sino en crear sistemas que puedas repetir. Este prompt te ayuda a construir ese sistema:\n\nPROMPT: Diseña un sistema de trabajo semanal para {topic}. Incluye: 1) Qué tareas puedo delegar completamente a la IA, 2) En qué puntos necesito supervisión humana, 3) Un flujo de trabajo con tiempos estimados, 4) Indicadores clave para evaluar resultados. Quiero poder ejecutarlo en menos de 30 minutos cada semana."),
        ],
        "conclusion": f"La clave del éxito con IA para {topic} no está en la herramienta, sino en cómo la usas. Estos prompts son tu punto de partida. Pruébalos, ajústalos, y sobre todo, úsalos de forma consistente. La práctica constante con prompts bien estructurados te dará resultados que hablan por sí solos."
    }
    return sections_data

def build_body(content_or_fallback, niche, topic):
    """Build HTML body from DeepSeek output or fallback."""
    if isinstance(content_or_fallback, dict):
        # Fallback mode
        parts = [f"<p>{content_or_fallback['introduccion']}</p>"]
        for h, p_text in content_or_fallback["secciones"]:
            # Split PROMPT: from text
            prompt_marker = "PROMPT:"
            if prompt_marker in p_text:
                text_part, prompt_part = p_text.split(prompt_marker, 1)
                prompt_part = prompt_part.strip()
            else:
                text_part = p_text
                prompt_part = ""
            
            parts.append(f"<h2>{h}</h2>")
            if text_part.strip():
                for para in text_part.strip().split("\n\n"):
                    para = para.strip()
                    if para:
                        parts.append(f"<p>{para}</p>")
            if prompt_part:
                # Escape HTML
                safe_prompt = h_escape(prompt_part[:200])
                parts.append(f'<div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">{safe_prompt}</div></div>')
        
        parts.append(f"<p>{content_or_fallback['conclusion']}</p>")
        return "\n".join(parts)
    
    # DeepSeek mode
    lines = content_or_fallback.split("\n")
    html_parts = []
    in_prompt = False
    
    for line in lines:
        s = line.strip()
        if not s:
            if in_prompt:
                html_parts.append('</div></div>')
                in_prompt = False
            continue
        
        if s.startswith("PROMPT:"):
            if in_prompt:
                html_parts.append('</div></div>')
            txt = s[7:].strip()
            safe_txt = h_escape(txt)
            html_parts.append(f'<div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">{safe_txt}</div>')
            in_prompt = True
        elif s.startswith("## ") or s.startswith("# "):
            if in_prompt:
                html_parts.append('</div></div>')
                in_prompt = False
            title = s.lstrip("# ").strip()
            html_parts.append(f'<h2>{h_escape(title)}</h2>')
        else:
            if in_prompt:
                # Continuation of prompt text
                safe_txt = h_escape(s)
                html_parts.append(f'<br>{safe_txt}')
            else:
                html_parts.append(f"<p>{h_escape(s)}</p>")
    
    if in_prompt:
        html_parts.append('</div></div>')
    
    return "\n".join(html_parts)

def main():
    day_of_year = datetime.now().timetuple().tm_yday
    
    niche = NICHES[day_of_year % len(NICHES)]
    art_type = ARTICLE_TYPES[day_of_year % len(ARTICLE_TYPES)]
    
    topics_list = TOPICS.get(niche["slug"], ["mejorar tu productividad"])
    topic = topics_list[day_of_year % len(topics_list)]
    
    title_template = art_type["titles"][day_of_year % len(art_type["titles"])]
    title = title_template.format(topic)
    desc = art_type["desc"].format(topic)
    desc = desc[:155] if len(desc) > 155 else desc
    slug = re.sub(r'[^a-z0-9-]', '', topic.lower().replace(' ', '-'))[:40] + f"-{art_type['type']}"
    date_str = datetime.now().strftime("%-d %B %Y")
    read_time = random.randint(5, 9)
    
    print(f"Generando: {niche['name']} / {art_type['type']} / {topic}")
    
    # Try DeepSeek first
    content = generate_via_deepseek(niche, topic, art_type["type"])
    
    # Use fallback if DeepSeek fails
    if content is None:
        print("DeepSeek failed, using fallback")
        fallback_content = generate_fallback(niche, topic)
        body_html = build_body(fallback_content, niche, topic)
    else:
        body_html = build_body(content, niche, topic)
        if body_html is None or len(body_html) < 200:
            print("Generated body too short, using fallback")
            fallback_content = generate_fallback(niche, topic)
            body_html = build_body(fallback_content, niche, topic)
    
    hero_img_id = pick(IMAGES, day_of_year)
    hero_img = f"https://images.unsplash.com/{hero_img_id}?w=800&q=85"
    
    b = niche
    canonical = f"https://magodago.github.io/neo-jarvis/blog/{b['slug']}/{slug}.html"
    
    payhip_url = f"https://payhip.com/b/{b['payhip']}"
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta name="google-site-verification" content="w3_O1vE9YvSH3fIDDeRzIhIQ63TuAPOz5GZxS0E2Kgo" />
<title>{h_escape(title)} — NEO Labs</title>
<meta name="description" content="{h_escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{h_escape(title)}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">
<script data-goatcounter="https://davidformulas.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<noscript><img src="https://davidformulas.goatcounter.com/count?p=/test"></noscript>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}:root{{--brand:{b['brand']};--brand-dark:{b['brand_dark']};--brand-light:{b['brand_light']};--bg:#050508;--bg2:#0c0c14;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}}
html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.8;touch-action:pan-y}}
a{{color:var(--brand);text-decoration:none}}a:hover{{filter:brightness(1.2)}}
.wrap{{max-width:780px;margin:0 auto;padding:0 24px}}
.breadcrumb{{font-size:.75rem;color:#6a6558;padding-top:100px;margin-bottom:8px}}.breadcrumb a{{color:#6a6558}}.breadcrumb a:hover{{color:var(--brand)}}
.article-header{{margin-bottom:32px}}
.article-header .cat-tag{{display:inline-block;padding:4px 12px;border-radius:100px;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;background:rgba(212,168,83,.15);color:var(--brand);margin-bottom:14px}}
.article-header h1{{font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2.2rem);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:10px}}
.article-header .meta{{display:flex;gap:16px;font-size:.8rem;color:#6a6558;flex-wrap:wrap}}
.article-body h2{{font-family:var(--font-display);font-size:1.2rem;font-weight:700;color:#fff;margin:32px 0 10px;letter-spacing:-.3px}}
.article-hero{{margin-bottom:28px;border-radius:14px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,.4)}}
.article-hero img{{width:100%;height:auto;display:block;border-radius:14px;aspect-ratio:1200/630;object-fit:cover}}
.article-body p{{font-size:.92rem;color:var(--text-muted);line-height:1.8;margin-bottom:14px}}
.article-body p strong{{color:var(--text)}}
.article-body ul, .article-body ol{{padding-left:24px;margin-bottom:14px;color:var(--text-muted);font-size:.92rem;line-height:1.8}}
.prompt-box{{background:var(--bg3);border-left:3px solid var(--brand);border-radius:0 10px 10px 0;padding:18px 22px;margin:14px 0 22px}}
.prompt-box .prompt-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--brand);font-weight:600;margin-bottom:4px}}
.prompt-box .prompt-text{{font-size:.85rem;color:#d0c8bc;line-height:1.7;font-style:italic}}
.cta-box{{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.9));border:1px solid rgba(212,168,83,.2);border-radius:14px;padding:32px 24px;text-align:center;margin:28px 0}}
.cta-box h3{{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--brand);margin-bottom:6px}}
.cta-box p{{color:var(--text-muted);font-size:.85rem;margin-bottom:16px}}
.btn{{padding:11px 28px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .35s;border:none;cursor:pointer;display:inline-block;background:linear-gradient(135deg,{b['brand_dark']},{b['brand']},{b['brand_light']});color:var(--bg);box-shadow:0 4px 30px rgba(212,168,83,.18)}}
.btn:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(212,168,83,.3)}}
.btn-outline{{border:1px solid var(--brand);color:var(--brand);background:transparent}}
.btn-outline:hover{{background:rgba(212,168,83,.1)}}
.related-section{{padding:32px 0;border-top:1px solid rgba(255,255,255,.05);margin-top:32px}}
.related-section h3{{font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--brand);margin-bottom:12px}}
.related-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}}
.related-card{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px;transition:all .3s;text-decoration:none;display:block}}
.related-card:hover{{background:rgba(212,168,83,.05);border-color:rgba(212,168,83,.2);transform:translateY(-2px)}}
.related-card .cat{{font-size:.55rem;letter-spacing:1px;text-transform:uppercase;color:var(--brand)}}
.related-card h4{{font-family:var(--font-display);font-size:.78rem;font-weight:600;color:#fff}}
.related-card p{{font-size:.7rem;color:var(--text-muted);margin-top:2px}}
footer{{background:var(--bg2);border-top:1px solid rgba(255,255,255,.04);padding:36px 24px 20px;text-align:center}}
footer .logo{{font-family:var(--font-display);font-size:1.2rem;font-weight:700;margin-bottom:10px;text-transform:uppercase;color:#fff}}footer .logo span{{color:#d4a853}}
footer .links{{display:flex;gap:18px;justify-content:center;flex-wrap:wrap;margin-bottom:10px}}footer .links a{{color:var(--text-muted);font-size:.78rem}}footer .links a:hover{{color:var(--brand)}}
footer .copy{{font-size:.68rem;color:#6a6558}}
#nav{{position:fixed;top:0;left:0;right:0;z-index:9998;background:rgba(5,5,8,.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;justify-content:space-between;padding:12px 28px;transition:transform .35s cubic-bezier(.4,0,.2,1)}}
#nav.hidden{{transform:translateY(-100%)}}
#nav .nav-logo{{font-family:var(--font-display);font-size:1.3rem;font-weight:800;letter-spacing:-1px;color:#fff}}
#nav .nav-logo span{{color:var(--brand)}}
#nav .nav-links{{display:flex;list-style:none;gap:24px;margin:0;padding:0}}
#nav .nav-links li a{{color:var(--text-muted);font-size:.78rem;font-weight:500;letter-spacing:.5px;transition:color .3s;text-decoration:none}}
#nav .nav-links li a:hover{{color:var(--brand)}}
#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,{b['brand_dark']},{b['brand_light']});z-index:9999;transition:width .1s}}
.cta-buttons{{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}}
.s-hidden{{display:none}}@media(max-width:768px){{.breadcrumb{{padding-top:80px}}.related-grid{{grid-template-columns:1fr}}#nav{{padding:12px 16px}}#nav .nav-links{{gap:14px}}#nav .nav-links li a{{font-size:.7rem}}}}
</style>
<script type="application/ld+json" class="s-hidden">{{"@context":"https://schema.org","@type":"Article","headline":"{h_escape(title)}","description":"{h_escape(desc)}","datePublished":"{datetime.now().strftime('%Y-%m-%d')}","author":{{"@type":"Person","name":"NEO Labs"}},"publisher":{{"@type":"Organization","name":"NEO Labs"}},"mainEntityOfPage":{{"@type":"WebPage","@id":"{canonical}"}}}}</script>
</head>
<body><div id="progress"></div>
<nav id="nav"><div class="nav-logo">Ne<span>o</span></div><ul class="nav-links"><li><a href="../../neo-labs.html">Inicio</a></li><li><a href="../../catalogo.html">Catálogo</a></li><li><a href="../index.html">Blog</a></li></ul></nav>
<div class="wrap">
<div class="breadcrumb"><a href="../../neo-labs.html">Inicio</a> <span>/</span> <a href="../index.html">Blog</a> <span>/</span> <a href="index.html">{h_escape(b['name'])}</a> <span>/</span> <span>{h_escape(title[:50])}</span></div>
<div class="article-header">
<span class="cat-tag">{h_escape(art_type['tag'])}</span>
<h1>{h_escape(title)}</h1>
<div class="meta"><span>{date_str}</span><span>{read_time} min de lectura</span></div>
</div>
<div class="article-hero"><img src="https://images.unsplash.com/{b['hero_img']}?w=780&h=400&fit=crop" alt="{h_escape(title)}" loading="lazy"></div>
<div class="article-body">
{body_html}
<div class="cta-box"><h3>Pack de {h_escape(b['name'])}</h3><p>10 prompts premium listos para copiar y pegar con ChatGPT, Claude y Gemini. Resultados inmediatos desde el primer uso.</p><p style="font-size:.75rem;color:#d4a853;margin-bottom:8px">Código <strong>NEO10</strong> = 10% desc</p><div class="cta-buttons"><a href="{payhip_url}" target="_blank" class="btn">Comprar 9.99€</a><a href="../../catalogo.html" class="btn btn-outline">Ver Catálogo</a></div></div>
</div>
<div class="related-section"><h3>Sigue leyendo</h3><div class="related-grid">
<a href="../prompts-ia-{h_escape(b['slug'])}-2026.html" class="related-card" style="display:none"><div class="cat">Guía</div><h4>Guías de {h_escape(b['name'])}</h4><p>Contenido destacado del blog.</p></a>
<a href="index.html" class="related-card"><div class="cat">Blog</div><h4>Blog de {h_escape(b['name'])}</h4><p>Todos los artículos del blog.</p></a>
<a href="../../catalogo.html" class="related-card"><div class="cat">Productos</div><h4>Catálogo NEO Labs</h4><p>Packs de prompts y planners.</p></a>
</div></div>
</div>
<footer><div class="logo">Ne<span>o</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catálogo</a><a href="../index.html">Blog</a><a href="https://payhip.com/bundle/98ens">Guía Gratuita</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>
let p=document.getElementById('progress');document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}})
let s=0,n=document.getElementById('nav');document.addEventListener('scroll',()=>{{let t=window.scrollY;if(t>s&&t>70)n.classList.add('hidden');else n.classList.remove('hidden');s=t}})
</script>
</body>
</html>'''
    
    filepath = BLOG / b["slug"] / f"{slug}.html"
    filepath.write_text(html, encoding="utf-8")
    print(f"Artículo escrito: {filepath.name}")
    
    # Git + sitemap + blog index
    os.chdir(str(REPO))
    
    # Rebuild sitemap
    try:
        sm_path = REPO / "sitemap.xml"
        urls = []
        for f in sorted(REPO.rglob("*.html")):
            if 'Zone.Identifier' in str(f) or '.git' in str(f):
                continue
            rel = f.relative_to(REPO)
            url = f"https://magodago.github.io/neo-jarvis/{rel}"
            urls.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")
        
        sm_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
        sm_path.write_text(sm_content, encoding="utf-8")
        subprocess.run(["git","add",str(sm_path)], capture_output=True)
        print("Sitemap reconstruido!")
    except Exception as e:
        print(f"Error en sitemap: {e}")
    
    # Update blog index
    try:
        subprocess.run([sys.executable, str(REPO / "update_blog_index.py")], timeout=30)
        print("Blog index actualizado!")
    except Exception as e:
        print(f"Error updating blog index: {e}")
    
    subprocess.run(["git","add",str(filepath)], capture_output=True)
    subprocess.run(["git","add",str(BLOG / "index.html")], capture_output=True)
    subprocess.run(["git","commit","-m",f"artículo diario: {topic} ({b['name']})"], capture_output=True)
    r = subprocess.run(["git","push"], capture_output=True, text=True)
    print(f"Publicado! ({r.stdout[:100] if r.stdout else 'ok'})")
    
    # Ping search engines
    for url in [
        f"https://www.google.com/ping?sitemap=https://magodago.github.io/neo-jarvis/sitemap.xml",
        f"https://api.indexnow.org/indexnow?url={filepath.name}&key=indexnow-key"
    ]:
        try:
            subprocess.run(["curl","-s","-o","/dev/null",url], timeout=10)
        except:
            pass
    print("Search engines notified!")

if __name__ == "__main__":
    main()
