#!/usr/bin/env python3
"""Daily article generator for NEO Labs blog network.
Usage: python3 daily-article.py
Generates one article, updates blog index, pushes to GitHub.
"""

import os, json, sys, subprocess, random
from datetime import datetime
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

NICHES = [
    {"slug": "productividad", "name": "Productividad", "brand": "#d4a853", "desc": "productividad con IA", "payhip": "EYojF"},
    {"slug": "finanzas", "name": "Finanzas", "brand": "#66bb6a", "desc": "finanzas personales con IA", "payhip": "uP62G"},
    {"slug": "marketing", "name": "Marketing", "brand": "#42a5f5", "desc": "marketing digital con IA", "payhip": "Q5RYA"},
    {"slug": "programacion", "name": "Programacion", "brand": "#ab47bc", "desc": "programacion con IA", "payhip": "XTEG5"},
    {"slug": "estudiantes", "name": "Educacion", "brand": "#ffa726", "desc": "estudio con IA", "payhip": "M3eqn"},
    {"slug": "rrhh", "name": "RRHH", "brand": "#ec407a", "desc": "recursos humanos con IA", "payhip": "KragB"},
]

ARTICLE_TEMPLATES = {
    "tutorial": {
        "title_patterns": [
            "Como {} con IA en 3 pasos",
            "Guia practica para {} usando inteligencia artificial",
            "Aprende a {} con prompts de IA",
            "Tutorial: {} con ChatGPT y Claude",
        ],
        "tag": "Tutorial",
        "desc_pattern": "Aprende paso a paso como {} con la ayuda de la IA."
    },
    "guia": {
        "title_patterns": [
            "Guia completa de {} con inteligencia artificial",
            "Los mejores prompts de IA para {}",
            "Todo lo que necesitas saber sobre {} con IA",
            "Estrategia definitiva de {} potenciada con IA",
        ],
        "tag": "Guia",
        "desc_pattern": "Guia detallada sobre {} con prompts de IA probados."
    },
    "noticia": {
        "title_patterns": [
            "Novedades de IA para {}: lo que cambia en 2026",
            "Nueva actualizacion de ChatGPT afecta a {}",
            "Lo ultimo en IA para {} que no puedes ignorar",
            "Breakthrough en IA: impacto en {}",
        ],
        "tag": "Noticia",
        "desc_pattern": "Las ultimas novedades de inteligencia artificial aplicadas a {}."
    },
    "comparativa": {
        "title_patterns": [
            "ChatGPT vs Claude vs Gemini: cual es mejor para {}",
            "Comparativa 2026: mejores herramientas de IA para {}",
        ],
        "tag": "Comparativa",
        "desc_pattern": "Comparamos las principales herramientas de IA para ayudarte a elegir."
    }
}

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def generate_content(niche, topic, article_type, template):
    """Try to generate content via local Ollama, fallback to template."""
    prompt = f"""Escribe un articulo de blog en español sobre {topic} aplicado a {niche['name']}.
Tipo: {article_type}.
Extension: 300-400 palabras exactamente. Incluye 2-3 prompts de IA practicos con el formato PROMPT: antes de cada uno.
Escribe SOLO el cuerpo del articulo (sin HTML, sin titulo, sin metadatos).
El articulo debe ser util, practico y con ejemplos concretos.
Responde SOLO con el texto del articulo, nada mas."""

    try:
        result = subprocess.run(
            ["ollama", "run", "qwen2.5-hermes", prompt],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    
    # Fallback template content
    return f"""En este articulo exploraremos como la inteligencia artificial esta transformando la forma en que los profesionales abordan {topic}. Las herramientas de IA han madurado lo suficiente como para ser un aliado practico en tu dia a dia.

Para empezar, necesitas un prompt basico que te permita obtener resultados consistentes. La clave esta en ser especifico con tus instrucciones y proporcionar contexto suficiente.

PROMPT: Eres un experto en {niche['name']}. Necesito ayuda con {topic}. Dame 3 enfoques diferentes, evalua pros y contras de cada uno, y recomiendame el mejor con un plan de accion concreto de 5 pasos.

Una vez que domines el prompt basico, puedes pasar a tecnicas mas avanzadas. La diferencia entre un resultado mediocre y uno excelente esta en los detalles del prompt.

PROMPT: Eres un consultor especializado en {niche['name']} con 20 anos de experiencia. Analiza esta situacion: [describe tu caso]. Aplica un marco de decision estructurado, identifica los 3 factores criticos, y propon soluciones accionables con metricas de exito.

La practica regular con estos prompts te permitira desarrollar intuicion sobre como comunicarte con la IA para obtener resultados cada vez mas precisos y utiles para tu trabajo diario."""

def build_article_html(niche, topic, article_type, template, content, slug):
    """Build complete HTML article page."""
    title = template["title_patterns"][0].format(topic) if template["title_patterns"] else f"Guia de {topic}"
    desc = template["desc_pattern"].format(topic) if "{}" in template.get("desc_pattern","") else f"Guia sobre {topic}"
    today = datetime.now().strftime("%Y-%m-%d")
    date_display = datetime.now().strftime("%-d %B %Y")
    read_time = random.randint(4, 10)
    canonical = f"https://magodago.github.io/neo-jarvis/blog/{niche['slug']}/{slug}.html"
    
    # Process content to add prompt-box formatting
    lines = content.split("\n")
    body_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("PROMPT:"):
            prompt_text = stripped[7:].strip() if len(stripped) > 7 else ""
            body_lines.append('<div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text"><strong>' + prompt_text.split(".")[0] if prompt_text else "" + '</strong><br>' + prompt_text + '</div></div>')
        elif stripped:
            body_lines.append(f"<p>{stripped}</p>")
    
    body = "\n".join(body_lines)
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — NEO Labs</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}:root{{--brand:{niche['brand']};--bg:#050508;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}}html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.8}}a{{color:var(--brand);text-decoration:none}}a:hover{{filter:brightness(1.2)}}.wrap{{max-width:780px;margin:0 auto;padding:0 24px}}.article-header{{padding-top:100px;margin-bottom:32px}}.article-header .cat-tag{{display:inline-block;padding:4px 12px;border-radius:100px;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;background:rgba(212,168,83,.15);color:var(--brand);margin-bottom:14px}}.article-header h1{{font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2.2rem);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:10px}}.article-header .meta{{font-size:.8rem;color:#6a6558}}.article-body h2{{font-family:var(--font-display);font-size:1.25rem;font-weight:700;color:#fff;margin:36px 0 10px}}.article-body p{{font-size:.92rem;color:var(--text-muted);line-height:1.8;margin-bottom:14px}}.prompt-box{{background:var(--bg3);border-left:3px solid var(--brand);border-radius:0 10px 10px 0;padding:18px 22px;margin:14px 0 22px}}.prompt-box .prompt-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--brand);font-weight:600;margin-bottom:4px}}.prompt-box .prompt-text{{font-size:.85rem;color:#d0c8bc;line-height:1.7;font-style:italic;white-space:pre-wrap}}.cta-box{{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.9));border:1px solid rgba(212,168,83,.2);border-radius:14px;padding:32px 24px;text-align:center;margin:28px 0}}.cta-box h3{{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--brand);margin-bottom:6px}}.cta-box p{{color:var(--text-muted);font-size:.85rem;margin-bottom:16px}}.btn{{padding:11px 28px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .35s;border:none;cursor:pointer;display:inline-block;background:linear-gradient(135deg,#b8922f,#d4a853,#f0d68a);color:var(--bg);box-shadow:0 4px 30px rgba(212,168,83,.18)}}.btn:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(212,168,83,.3)}}footer{{background:var(--bg2, #0c0c14);border-top:1px solid rgba(255,255,255,.04);padding:40px 24px 24px;text-align:center;color:#6a6558;font-size:.7rem}}#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,var(--brand),#f0d68a);z-index:9999;transition:width .1s}}.s-hidden{{display:none}}
</style>
</head>
<body><div id="progress"></div>
<div class="wrap">
<div class="article-header"><span class="cat-tag">{template['tag']}</span><h1>{title}</h1><div class="meta">{date_display} &middot; {read_time} min de lectura</div></div>
<div class="article-body">
{body}
<div class="cta-box"><h3>Pack de {niche['name']}</h3><p>10 prompts premium listos para copiar y pegar.</p><a href="https://payhip.com/b/{niche['payhip']}" target="_blank" class="btn">Comprar 9.99</a></div>
</div>
</div>
<footer><p>&copy; 2026 NEO Labs &mdash; <a href="https://magodago.github.io/neo-jarvis/blog/{niche['slug']}/">Blog de {niche['name']}</a></p></footer>
<script>let p=document.getElementById('progress');document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}})</script>
</body>
</html>"""
    return html

def main():
    import subprocess as sp
    
    # Rotate niche daily
    day = datetime.now().timetuple().tm_yday
    niche = NICHES[day % len(NICHES)]
    
    # Decide article type
    types = list(ARTICLE_TEMPLATES.keys())
    article_type = types[day % len(types)]
    template = ARTICLE_TEMPLATES[article_type]
    
    topics = {
        "productividad": ["organizar tu agenda", "gestionar tu tiempo", "priorizar tareas", "automatizar informes", "planificar proyectos"],
        "finanzas": ["crear un presupuesto", "analizar tus gastos", "planificar tu jubilacion", "optimizar tu fiscalidad", "gestionar inversiones"],
        "marketing": ["crear contenido SEO", "analizar tu audiencia", "automatizar emails", "optimizar campanas", "crear embudos de venta"],
        "programacion": ["debuggear codigo", "revisar pull requests", "escribir tests", "documentar APIs", "refactorizar codigo"],
        "estudiantes": ["resumir textos academicos", "preparar examenes", "escribir ensayos", "organizar tu estudio", "crear flashcards"],
        "rrhh": ["seleccionar candidatos", "evaluar desempeno", "redactar ofertas de empleo", "planificar formacion", "mejorar clima laboral"],
    }
    
    niche_topics = topics.get(niche['slug'], ["mejorar tu productividad"])
    topic = niche_topics[day % len(niche_topics)]
    
    # Generate slug
    slug = f"{article_type}-{topic.lower().replace(' ', '-').replace(':', '')}-ia"
    
    niche_dir = BLOG / niche['slug']
    ensure_dir(niche_dir)
    
    print(f"Generando articulo: {niche['name']} / {article_type} / {topic}")
    
    content = generate_content(niche, topic, article_type, template)
    html = build_article_html(niche, topic, article_type, template, content, slug)
    
    filepath = niche_dir / f"{slug}.html"
    filepath.write_text(html, encoding="utf-8")
    print(f"Articulo escrito: {filepath}")
    
    # Git operations
    os.chdir(str(REPO))
    sp.run(["git", "add", str(filepath)], capture_output=True)
    sp.run(["git", "commit", "-m", f"articulo diario: {topic} en {niche['name']}"], capture_output=True)
    result = sp.run(["git", "push"], capture_output=True, text=True)
    print(f"Push: {result.stdout[:200] if result.stdout else 'ok'}")
    print("Articulo generado y publicado!")

if __name__ == "__main__":
    main()
