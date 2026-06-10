import json
#!/usr/bin/env python3
"""Daily article generator v2 — SEO-optimized, varied, high-quality content.
Generates one article per day rotating through niches.
"""
import os, subprocess, random, re, sys
from datetime import datetime
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

NICHES = [
    {"slug":"productividad","name":"Productividad","brand":"#d4a853","brand_dark":"#b8922f","brand_light":"#f0d68a","payhip":"EYojF",
     "hero_img":"photo-1497366216548-37526070297c"},
    {"slug":"finanzas","name":"Finanzas","brand":"#66bb6a","brand_dark":"#388e3c","brand_light":"#a5d6a7","payhip":"uP62G",
     "hero_img":"photo-1554224155-8d04cb21cd6c"},
    {"slug":"marketing","name":"Marketing","brand":"#42a5f5","brand_dark":"#1976d2","brand_light":"#90caf9","payhip":"Q5RYA",
     "hero_img":"photo-1557838923-2985c318be48"},
    {"slug":"programacion","name":"Programacion","brand":"#ab47bc","brand_dark":"#7b1fa2","brand_light":"#ce93d8","payhip":"XTEG5",
     "hero_img":"photo-1461749280684-dccba630e2f6"},
    {"slug":"estudiantes","name":"Educacion","brand":"#ffa726","brand_dark":"#ef6c00","brand_light":"#ffcc80","payhip":"M3eqn",
     "hero_img":"photo-1488190211105-8b0e65b80b4e"},
    {"slug":"rrhh","name":"RRHH","brand":"#ec407a","brand_dark":"#c2185b","brand_light":"#f48fb1","payhip":"KragB",
     "hero_img":"photo-1600880292203-757bb62b4baf"},
]

# Known-good Unsplash photo IDs for article hero images
IMAGES = [
    "photo-1555066931-4365d14bab8c","photo-1512314889357-e157c22f938d","photo-1454165804606-c3d57bc86b40",
    "photo-1434030216411-0b793f4b4173","photo-1555421689-d68471e189f2","photo-1450101499163-c8848c66ca85",
    "photo-1552664730-d307ca884978","photo-1551288049-bebda4e38f71","photo-1522071820081-009f0129c71c",
    "photo-1555949963-aa79dcee981c","photo-1552581234-26160f608093","photo-1460925895917-afdab827c52f",
]

ARTICLE_TYPES = [
    {"type":"guia","tag":"Guia",
     "titles":["Guia completa de {} con inteligencia artificial","Los mejores prompts de IA para {}",
               "Todo lo que necesitas saber sobre {} con IA","Estrategia definitiva de {} potenciada con IA"],
     "desc":"Guia detallada sobre {} con prompts de IA probados y refinados."},
    {"type":"tutorial","tag":"Tutorial",
     "titles":["Como {} con IA paso a paso","Guia practica para {} usando inteligencia artificial",
               "Aprende a {} con prompts de IA","Tutorial practico de {} con ChatGPT y Claude"],
     "desc":"Aprende paso a paso como {} con la ayuda de la inteligencia artificial."},
    {"type":"noticia","tag":"Noticia",
     "titles":["Novedades de IA para {}: lo que cambia en 2026","Nueva actualizacion de ChatGPT afecta a {}",
               "Lo ultimo en IA para {} que no puedes ignorar","Breakthrough en IA: nuevo impacto en {}"],
     "desc":"Las ultimas novedades de inteligencia artificial aplicadas a {}."},
    {"type":"comparativa","tag":"Comparativa",
     "titles":["ChatGPT vs Claude vs Gemini: cual es mejor para {}","Comparativa 2026: mejores herramientas para {}"],
     "desc":"Comparamos las principales herramientas de IA para ayudarte a elegir la mejor opcion."},
]

TOPICS = {
    "productividad":["organizar tu agenda","gestionar tu tiempo","priorizar tareas","automatizar informes",
                     "planificar proyectos","gestionar el correo","preparar reuniones","tomar decisiones"],
    "finanzas":["crear un presupuesto","analizar tus gastos","planificar tu jubilacion","optimizar tu fiscalidad",
                "gestionar inversiones","reducir deudas","planificar metas financieras"],
    "marketing":["crear contenido SEO","analizar tu audiencia","automatizar emails","optimizar campanas",
                 "crear embudos de venta","hacer segmentacion","analizar metricas"],
    "programacion":["debuggear codigo","revisar pull requests","escribir tests","documentar APIs",
                    "refactorizar codigo","revisar seguridad","optimizar rendimiento"],
    "estudiantes":["resumir textos academicos","preparar examenes","escribir ensayos","organizar tu estudio",
                   "crear flashcards","hacer presentaciones","gestionar el tiempo de estudio"],
    "rrhh":["seleccionar candidatos","evaluar desempeno","redactar ofertas","planificar formacion",
            "mejorar clima laboral","hacer onboarding","gestionar el talento"],
}

# 5 different fallback article templates for variety when Ollama fails
FALLBACKS = [
    {
        "intro": "Si hay un area donde la IA realmente marca la diferencia es en {topic}. Lo que antes te llevaba horas, ahora puedes hacerlo en minutos con el prompt adecuado.",
        "sections": [
            ("Empieza con un prompt basico", "Eres un experto en {niche}. Necesito ayuda con {topic}. Dame 3 enfoques diferentes, evalua pros y contras de cada uno, y recomiendame el mejor con un plan de accion concreto de 5 pasos."),
            ("Lleva tus resultados al siguiente nivel", "Eres un consultor senior en {niche} con 20 anos de experiencia. Analiza mi situacion actual: [describe]. Identifica los 3 factores criticos, propone soluciones accionables, y establece metricas de exito para cada una."),
            ("Automatiza el proceso completo", "Crea un sistema automatico para {topic} en {niche}. Dame: 1) Los pasos que puedo delegar completamente a la IA, 2) Los puntos donde necesito supervisar, 3) Un prompt que lo unifique todo en una sola ejecucion."),
        ]
    },
    {
        "intro": "La clave del exito con IA no esta en la herramienta que uses, sino en como le pides las cosas. Para {topic}, la diferencia entre un resultado mediocre y uno excelente esta en los detalles del prompt.",
        "sections": [
            ("El prompt que todo profesional necesita", "Eres un asistente virtual especializado en {topic}. Mi objetivo es [describe]. Dame una estrategia completa dividida en: 1) Diagnostico de la situacion actual, 2) Plan de accion con 3 fases, 3) Recursos necesarios, 4) Timeline estimado, 5) Metricas de exito."),
            ("Refina los resultados con contexto adicional", "Teniendo en cuenta mi contexto especifico: [contexto]. Revisa la estrategia anterior y adaptala. Identifica que partes del plan pueden no funcionar en mi caso y sugiereme alternativas personalizadas."),
        ]
    },
    {
        "intro": "Mucha gente cree que usar IA es solo escribir lo primero que se te viene a la mente y esperar un resultado magico. La realidad es que los mejores resultados vienen de prompts bien estructurados. Para {topic}, esta es la formula que funciona.",
        "sections": [
            ("La estructura que siempre funciona", "Eres un experto mundial en {niche} y {topic}. Dame tu metodologia completa: 1) Marco teorico (2 parrafos), 2) Paso a paso practico (5 pasos), 3) Errores comunes y como evitarlos, 4) Ejemplo real aplicado, 5) Conclusion con siguiente paso."),
            ("Personaliza segun tu caso", "Ahora adapta esa metodologia a mi caso concreto: [describe tu situacion]. Que cambiaria? Que mantendria? Dame una version personalizada paso a paso."),
            ("Crea un sistema de seguimiento", "Disena un sistema de seguimiento semanal para {topic}. Indicadores clave, frecuencia de revision, ajustes recomenda-dos segun resultados. Quiero poder evaluar mi progreso en 5 minutos cada semana."),
        ]
    },
]

def pick(seq, day=None):
    if day is not None:
        return seq[day % len(seq)]
    return random.choice(seq)

def generate_via_ollama(niche, topic, article_type):
    """Try to generate content via local Ollama."""
    prompt = f"""Eres un escritor de blogs profesional. Escribe un articulo en español sobre {topic} en el area de {niche['name']}.
Tipo de articulo: {article_type}.
Extension: 500-700 palabras.

ESTRUCTURA REQUERIDA:
- Introduccion (2 parrafos) que enganche y explique por que es importante
- 2-3 secciones con titulos H2, cada una con un prompt practico formateado como PROMPT: seguido del texto del prompt
- Un parrafo de conclusion

REGLAS:
- NO incluyas absolutamente ningun proceso de pensamiento ni razonamiento interno
- Escribe SOLO el cuerpo del articulo (sin HTML, sin titulo, sin prefijos)
- Usa lenguaje claro, directo y util
- Los prompts deben ser practicos, copiables y con [corchetes] para personalizar
- Incluye ejemplos concretos
- Termina con una frase que motive a la accion

Responde UNICAMENTE con el texto del articulo, sin ningun prefijo,sin Thinking,sin explicaciones.

IMPORTANTE: Usa EXACTAMENTE este formato para cada seccion y prompt:
## Titulo de seccion

PROMPT: [texto del prompt]

Asegurate de incluir AL MENOS 2 secciones con su prompt, y que el articulo tenga 500-700 palabras."""
    try:
        resp = subprocess.run(
            ["curl","-s","--max-time","150",
             "http://localhost:11434/api/generate",
             "-d", '{"model":"gemma4","prompt":' + json.dumps(prompt) + ',"stream":false,"options":{"num_predict":4096,"temperature":0.8}}'],
            capture_output=True,text=True,timeout=160
        )
        if resp.returncode == 0 and resp.stdout.strip():
            import json as _j
            data = _j.loads(resp.stdout)
            content = data.get("response","").strip()
            if content:
                for prefix in ["Thinking...","thinking","**Pensamiento:**","**Razonamiento:**","Here's"]:
                    if content.startswith(prefix):
                        content = content[len(prefix):].strip()
                return content
    except: pass
    return None

def build_body(content, fallback, niche, topic):
    """Build article body from Ollama output or fallback."""
    if content:
        lines = content.split("\n")
        html_parts = []
        for line in lines:
            s = line.strip()
            if not s: continue
            if s.startswith("PROMPT:"):
                txt = s[7:].strip()
                html_parts.append(f'<div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text"><strong>{txt[:80]}</strong><br>{txt}</div></div>')
            elif s.startswith("## ") or s.startswith("# "):
                html_parts.append(f'<h2>{s.lstrip("# ")}</h2>')
            else:
                html_parts.append(f"<p>{s}</p>")
        return "\n".join(html_parts)
    else:
        # Use fallback
        fb = pick(fallback)
        intro = fb["intro"].format(topic=topic, niche=niche["name"])
        parts = [f"<p>{intro}</p>"]
        for h, p in fb["sections"]:
            parts.append(f"<h2>{h}</h2>")
            prompt_text = p.format(topic=topic, niche=niche["name"])
            parts.append(f'<div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text"><strong>{prompt_text[:100]}</strong><br>{prompt_text}</div></div>')
        conclusion = pick(["Ponlo en practica esta misma semana y veras la diferencia.","Comienza hoy y repite el proceso cada semana para resultados consistentes.","La practica constante con estos prompts te dara resultados que hablan por si solos."])
        parts.append(f"<p>{conclusion}</p>")
        return "\n".join(parts)

def main():
    day_of_year = datetime.now().timetuple().tm_yday
    
    # Rotate niche and article type deterministically
    niche = NICHES[day_of_year % len(NICHES)]
    art_type = ARTICLE_TYPES[day_of_year % len(ARTICLE_TYPES)]
    
    # Pick topic
    topics_list = TOPICS.get(niche["slug"], ["mejorar tu productividad"])
    topic = topics_list[day_of_year % len(topics_list)]
    
    # Build title, desc, slug
    title_template = art_type["titles"][day_of_year % len(art_type["titles"])]
    title = title_template.format(topic)
    desc = art_type["desc"].format(topic)
    # Truncate desc to 155 chars for SEO
    desc = desc[:155] if len(desc) > 155 else desc
    slug = re.sub(r'[^a-z0-9-]', '', topic.lower().replace(' ', '-'))[:40] + f"-{art_type['type']}"
    date_str = datetime.now().strftime("%-d %B %Y")
    read_time = random.randint(5, 9)
    
    # Generate content
    print(f"Generando: {niche['name']} / {art_type['type']} / {topic}")
    content = generate_via_ollama(niche, topic, art_type["type"])
    body_html = build_body(content, FALLBACKS, niche, topic)
    
    # Build image URL
    hero_img_id = pick(IMAGES, day_of_year)
    hero_img = f"https://images.unsplash.com/{hero_img_id}?w=800&q=85"
    
    # Brand colors
    b = niche
    canonical = f"https://magodago.github.io/neo-jarvis/blog/{b['slug']}/{slug}.html"
    
    # Article template with ALL improvements
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>{title} — NEO Labs</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">
<!-- GoatCounter analytics -->
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
.related-section{{padding:32px 0;border-top:1px solid rgba(255,255,255,.05);margin-top:32px}}
.related-section h3{{font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--brand);margin-bottom:12px}}
.related-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}}
.related-card{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px;transition:all .3s;text-decoration:none;display:block}}
.related-card:hover{{background:rgba(212,168,83,.05);border-color:rgba(212,168,83,.2);transform:translateY(-2px)}}
.related-card .cat{{font-size:.55rem;letter-spacing:1px;text-transform:uppercase;color:var(--brand)}}
.related-card h4{{font-family:var(--font-display);font-size:.78rem;font-weight:600;color:#fff}}
.{{}}related-card p{{font-size:.7rem;color:var(--text-muted);margin-top:2px}}
footer{{background:var(--bg2);border-top:1px solid rgba(255,255,255,.04);padding:36px 24px 20px;text-align:center}}
footer .logo{{font-family:var(--font-display);font-size:1.2rem;font-weight:700;margin-bottom:10px;text-transform:uppercase;color:#fff}}footer .logo span{{color:#d4a853}}
footer .links{{display:flex;gap:18px;justify-content:center;flex-wrap:wrap;margin-bottom:10px}}footer .links a{{color:var(--text-muted);font-size:.78rem}}footer .links a:hover{{color:var(--brand)}}
footer .copy{{font-size:.68rem;color:#6a6558}}
#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,{b['brand_dark']},{b['brand_light']});z-index:9999;transition:width .1s}}
.s-hidden{{display:none}}@media(max-width:768px){{.breadcrumb{{padding-top:80px}}.related-grid{{grid-template-columns:1fr}}}}
</style>
<script type="application/ld+json" class="s-hidden">{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{desc}","datePublished":"{datetime.now().strftime('%Y-%m-%d')}","author":{{"@type":"Person","name":"NEO Labs"}},"publisher":{{"@type":"Organization","name":"NEO Labs"}},"mainEntityOfPage":{{"@type":"WebPage","@id":"{canonical}"}}}}</script>
</head>
<body><div id="progress"></div>
<nav id="nav"><div class="nav-logo">NE<span>O</span></div><ul class="nav-links"><li><a href="../../neo-labs.html">Inicio</a></li><li><a href="../../catalogo.html">Catalogo</a></li><li><a href="../index.html">Blog</a></li></ul></nav>
<div class="wrap">
<div class="breadcrumb"><a href="../../neo-labs.html">Inicio</a> <span>/</span> <a href="../index.html">Blog</a> <span>/</span> <a href="index.html">{b['name']}</a> <span>/</span> <span>{title[:50]}</span></div>
<div class="article-header">
<span class="cat-tag">{art_type['tag']}</span>
<h1>{title}</h1>
<div class="meta"><span>{date_str}</span><span>{read_time} min de lectura</span></div>
</div>
<div class="article-body">
{body_html}
<div class="cta-box"><h3>Pack de {b['name']}</h3><p>10 prompts premium listos para copiar y pegar con ChatGPT, Claude y Gemini. Resultados inmediatos desde el primer uso.</p><a href="https://payhip.com/b/{b['payhip']}" target="_blank" class="btn">Comprar 9.99</a><a href="../../catalogo.html" class="btn btn-outline" style="margin-left:8px;">Ver Catalogo</a></div>
</div>
<div class="related-section"><h3>Sigue leyendo</h3><div class="related-grid">
<a href="../prompts-ia-{b['slug']}-2026.html" class="related-card" style="display:none"><div class="cat">Guia</div><h4>Guias de {b['name']}</h4><p>Contenido destacado del blog.</p></a>
<a href="index.html" class="related-card"><div class="cat">Blog</div><h4>Blog de {b['name']}</h4><p>Todos los articulos del blog.</p></a>
<a href="../../catalogo.html" class="related-card"><div class="cat">Productos</div><h4>Catalogo NEO Labs</h4><p>Packs de prompts y planners.</p></a>
</div></div>
</div>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catalogo</a><a href="../index.html">Blog</a><a href="https://payhip.com/b/98ens">Guia Gratuita</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>
let p=document.getElementById('progress');document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}})
let s=0,n=document.getElementById('nav');document.addEventListener('scroll',()=>{{let t=window.scrollY;if(t>s&&t>70)n.classList.add('hidden');else n.classList.remove('hidden');s=t}})
</script>
</body>
</html>'''
    
    filepath = BLOG / b["slug"] / f"{slug}.html"
    filepath.write_text(html, encoding="utf-8")
    print(f"Articulo escrito: {filepath.name}")
    
    # Git
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
    
    subprocess.run(["git","add",str(filepath)], capture_output=True)
    subprocess.run(["git","commit","-m",f"articulo diario: {topic} ({b['name']})"], capture_output=True)
    r = subprocess.run(["git","push"], capture_output=True, text=True)
    print(f"Publicado! ({r.stdout[:100] if r.stdout else 'ok'})")
    
    # Ping Google
    try:
        article_url = f"https://magodago.github.io/neo-jarvis/blog/{b['slug']}/{slug}.html"
        sm_url = "https://magodago.github.io/neo-jarvis/sitemap.xml"
        subprocess.run(["curl","-s","-o","/dev/null",f"https://www.google.com/ping?sitemap={sm_url}"], timeout=10)
        subprocess.run(["curl","-s","-o","/dev/null",f"https://www.google.com/ping?sitemap={article_url}"], timeout=10)
        print("Google notificado!")
    except:
        print("Ping a Google no disponible")
    
    # Generate podcast for the new article
    try:
        podcast_script = REPO / "podcast_gen.py"
        if podcast_script.exists():
            r = subprocess.run(
                [sys.executable, str(podcast_script), "--article", f"{b['slug']}/{slug}.html"],
                capture_output=True, text=True, timeout=300
            )
            print(f"Podcast: {r.stdout.strip()[-100:] if r.stdout else 'ok'}")
            # Git add podcast files
            subprocess.run(["git","add","podcasts/"], capture_output=True)
    except Exception as e:
        print(f"Podcast error: {e}")

if __name__ == "__main__":
    main()
