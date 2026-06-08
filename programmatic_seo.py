#!/usr/bin/env python3
"""Programmatic SEO — Genera 500+ páginas desde plantillas + Gemma 4.
Cada página apunta a una keyword long-tail diferente."""

import os, json, subprocess, re, textwrap, time, random
from datetime import datetime
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

NICHES = [
    {"slug":"productividad","name":"Productividad","brand":"#d4a853","brand_dark":"#b8922f","emoji":"⚡","payhip":"EYojF",
     "hero":"photo-1497366216548-37526070297c","desc":"mejora tu eficiencia con prompts de IA"},
    {"slug":"finanzas","name":"Finanzas","brand":"#66bb6a","brand_dark":"#388e3c","emoji":"💰","payhip":"uP62G",
     "hero":"photo-1554224155-8d04cb21cd6c","desc":"gestiona tu dinero con inteligencia artificial"},
    {"slug":"marketing","name":"Marketing","brand":"#42a5f5","brand_dark":"#1976d2","emoji":"📈","payhip":"Q5RYA",
     "hero":"photo-1557838923-2985c318be48","desc":"multiplica tu marketing con prompts de IA"},
    {"slug":"programacion","name":"Programacion","brand":"#ab47bc","brand_dark":"#7b1fa2","emoji":"💻","payhip":"XTEG5",
     "hero":"photo-1461749280684-dccba630e2f6","desc":"programa mejor con asistentes de IA"},
    {"slug":"estudiantes","name":"Estudiantes","brand":"#ffa726","brand_dark":"#ef6c00","emoji":"📚","payhip":"M3eqn",
     "hero":"photo-1488190211105-8b0e65b80b4e","desc":"estudia mas inteligente con ChatGPT"},
    {"slug":"rrhh","name":"RRHH","brand":"#ec407a","brand_dark":"#c2185b","emoji":"👥","payhip":"KragB",
     "hero":"photo-1600880292203-757bb62b4baf","desc":"transforma tu departamento de RRHH con IA"},
]

# Plantillas de contenido por tipo
TEMPLATES = {
    "guia-paso-a-paso": textwrap.dedent("""\
    <h2>{titulo_seccion}</h2>
    <p>{intro}</p>
    <ol>
    {pasos}
    </ol>
    <div class="prompt-box"><div class="prompt-label">Prompt Recomendado</div><div class="prompt-text"><strong>Prompt para {keyword_amigable}:</strong> {prompt}</div></div>
    <div class="tip-box"><div class="tip-label">Consejo Practico</div><p>{tip}</p></div>
    """),
    "lista-promesas": textwrap.dedent("""\
    <h2>{titulo_seccion}</h2>
    <p>{intro}</p>
    <ul>
    {items}
    </ul>
    <div class="prompt-box"><div class="prompt-label">Prompt Recomendado</div><div class="prompt-text"><strong>Prompt para {keyword_amigable}:</strong> {prompt}</div></div>
    """),
    "comparativa": textwrap.dedent("""\
    <h2>{titulo_seccion}</h2>
    <p>{intro}</p>
    {tabla_html}
    <p>{conclusion}</p>
    <div class="prompt-box"><div class="prompt-label">Prompt Recomendado</div><div class="prompt-text"><strong>Prompt para {keyword_amigable}:</strong> {prompt}</div></div>
    """),
}

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[áàäâ]','a',s)
    s = re.sub(r'[éèëê]','e',s)
    s = re.sub(r'[íìïî]','i',s)
    s = re.sub(r'[óòöô]','o',s)
    s = re.sub(r'[úùüû]','u',s)
    s = re.sub(r'[ñ]','n',s)
    s = re.sub(r'[^a-z0-9]+','-',s)
    return s.strip('-')

def call_gemma(prompt, max_tokens=300):
    """Llama a Gemma 4 vía Ollama"""
    payload = json.dumps({
        "model": "gemma4:latest",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.8}
    })
    try:
        r = subprocess.run(["curl","-s","-X","POST","http://localhost:11434/api/generate",
            "-d", payload], capture_output=True, text=True, timeout=60)
        data = json.loads(r.stdout)
        return data.get("response", "").strip()
    except:
        return ""

def generar_contenido_para_keyword(niche, keyword, tipo):
    """Genera contenido único para una keyword usando Gemma 4"""
    keyword_amigable = keyword.replace("-", " ")
    
    prompts_personalizados = {
        "guia-paso-a-paso": f"""Responde SOLO con este formato exacto separado por ||| (sin explicaciones adicionales, sin markdown):

TITULO: Guia completa para {keyword_amigable}
INTRO: [2-3 frases de introduccion, 50-80 palabras]
PASO1:[nombre paso] - [descripcion breve]
PASO2:[nombre paso] - [descripcion breve]
PASO3:[nombre paso] - [descripcion breve]
PASO4:[nombre paso] - [descripcion breve]
PROMPT: [un prompt de ChatGPT listo para copiar, 1-2 frases]
TIP: [un consejo practico, 1 frase]

Formato exacto: TITULO|||INTRO|||PASO1:descripcion|PASO2:descripcion|PASO3:descripcion|PASO4:descripcion|||PROMPT|||TIP""",
        "lista-promesas": f"""Responde SOLO con este formato exacto separado por |||:

TITULO: Los mejores beneficios de {keyword_amigable}
INTRO: [2-3 frases, 50-80 palabras]
ITEM1:[nombre] - [explicacion breve]
ITEM2:[nombre] - [explicacion breve]
ITEM3:[nombre] - [explicacion breve]
ITEM4:[nombre] - [explicacion breve]
ITEM5:[nombre] - [explicacion breve]
PROMPT: [prompt de ChatGPT, 1-2 frases]
TIP: [consejo practico, 1 frase]

Formato: TITULO|||INTRO|||ITEM1:texto|ITEM2:texto|ITEM3:texto|ITEM4:texto|ITEM5:texto|||PROMPT|||TIP""",
        "comparativa": f"""Responde SOLO con este formato exacto separado por |||:

TITULO: Comparativa: mejores opciones para {keyword_amigable}
INTRO: [2-3 frases, 50-80 palabras]
OPCION1:[nombre]|[pros]|[contras]|[precio]
OPCION2:[nombre]|[pros]|[contras]|[precio]
OPCION3:[nombre]|[pros]|[contras]|[precio]
CONCLUSION: [2-3 frases de cierre]
PROMPT: [prompt de ChatGPT, 1-2 frases]
TIP: [consejo practico, 1 frase]

Formato: TITULO|||INTRO|||OPCION1:pros:contras:precio|OPCION2:pros:contras:precio|OPCION3:pros:contras:precio|||CONCLUSION|||PROMPT|||TIP""",
    }
    
    result = call_gemma(prompts_personalizados[tipo], max_tokens=500)
    if not result or "|||" not in result:
        # Fallback a contenido predefinido
        return generar_fallback(niche, keyword, tipo)
    
    try:
        parts = result.split("|||")
        data = {}
        if tipo == "guia-paso-a-paso":
            data["titulo_seccion"] = parts[0].strip()
            data["intro"] = parts[1].strip()
            pasos_raw = parts[2].strip()
            data["pasos"] = "\n".join(f"<li><strong>{p.split(':')[0]}:</strong> {':'.join(p.split(':')[1:])}</li>" for p in pasos_raw.split("|") if ":" in p)
            data["prompt"] = parts[3].strip() if len(parts) > 3 else f"Eres un experto en {keyword_amigable}. Dame consejos practicos y accionables."
            data["tip"] = parts[4].strip() if len(parts) > 4 else f"La clave es la consistencia. Practica {keyword_amigable} a diario."
        elif tipo == "lista-promesas":
            data["titulo_seccion"] = parts[0].strip()
            data["intro"] = parts[1].strip()
            items_raw = parts[2].strip()
            data["items"] = "\n".join(f"<li><strong>{i.split(':')[0]}:</strong> {':'.join(i.split(':')[1:])}</li>" for i in items_raw.split("|") if ":" in i)
            data["prompt"] = parts[3].strip() if len(parts) > 3 else f"Eres un experto en {keyword_amigable}..."
            data["tip"] = parts[4].strip() if len(parts) > 4 else "Empieza con un area y expande desde ahi."
        elif tipo == "comparativa":
            data["titulo_seccion"] = parts[0].strip()
            data["intro"] = parts[1].strip()
            ops = parts[2].strip().split("|")
            rows = ""
            for o in ops:
                if ":" in o:
                    parts_o = o.split(":")
                    name = parts_o[0]
                    pros = parts_o[1] if len(parts_o) > 1 else "-"
                    cons = parts_o[2] if len(parts_o) > 2 else "-"
                    price = parts_o[3] if len(parts_o) > 3 else "-"
                    rows += f"<tr><td><strong>{name}</strong></td><td>{pros}</td><td>{cons}</td><td>{price}</td></tr>\n"
            data["tabla_html"] = f'<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.85rem;margin:14px 0"><tr style="background:var(--bg3);color:var(--gold)"><th>Opcion</th><th>Pros</th><th>Contras</th><th>Precio</th></tr>{rows}</table></div>'
            data["conclusion"] = parts[3].strip() if len(parts) > 3 else "Cada opcion tiene sus ventajas. Elige la que mejor se adapte a ti."
            data["prompt"] = parts[4].strip() if len(parts) > 4 else "..."
        return data
    except:
        return generar_fallback(niche, keyword, tipo)

def generar_fallback(niche, keyword, tipo):
    """Contenido predefinido cuando Gemma falla"""
    kw = keyword.replace("-", " ")
    return {
        "titulo_seccion": f"Como dominar {kw} con inteligencia artificial",
        "intro": f"La inteligencia artificial ha transformado la forma en que abordamos {kw}. Con los prompts adecuados, puedes optimizar tu tiempo y obtener resultados profesionales en minutos. En esta guia practica te mostramos como hacerlo paso a paso.",
        "pasos": "\n".join(f"<li><strong>Paso {i}:</strong> Identifica tu objetivo especifico en {kw} y prepara el contexto necesario.</li>" for i in range(1,5)),
        "prompt": f"Eres un experto en {kw}. Actua como mi mentor y guiame a traves de las mejores practicas. Dame pasos concretos y accionables.",
        "tip": f"La clave del exito en {kw} es la practica constante y la iteracion de tus prompts.",
        "items": "\n".join(f"<li><strong>Beneficio {i}:</strong> Ahorra tiempo y obtienes mejores resultados en {kw}</li>" for i in range(1,6)),
    }

def build_page(niche, keyword, sections, tipo_idx=0):
    """Construye la página HTML completa"""
    kw = keyword.replace("-", " ")
    kw_title = kw.title()
    slug = slugify(keyword)
    today = datetime.now().strftime("%Y-%m-%d")
    
    tipos = ["guia", "tutorial", "consejos", "mejores-practicas", "introduccion", "avanzado"]
    tipo_pag = tipos[tipo_idx % len(tipos)]
    
    seo_title = f"{kw_title} con IA: {random.choice(['Guia Completa', 'Tutorial Practico', 'Mejores Estrategias', 'Todo lo que Necesitas Saber'])}"
    seo_desc = f"Aprende todo sobre {kw} con inteligencia artificial. {random.choice(['Guia practica con prompts incluidos', 'Tutorial paso a paso con ejemplos reales', 'Estrategias probadas para resultados inmediatos'])}."
    
    body_html = f"""
<div class="wrap">
<div class="breadcrumb"><a href="../../neo-labs.html">Inicio</a> <span>/</span> <a href="index.html">Blog {niche['name']}</a> <span>/</span> <span>{kw_title}</span></div>
<div class="article-header">
<span class="cat-tag">{tipo_pag.capitalize()}</span>
<h1>{seo_title}</h1>
<div class="meta"><span>{today}</span><span>NEO Labs</span><span>{random.randint(3,8)} min lectura</span></div>
</div>
<div class="article-body">
<p>La inteligencia artificial esta revolucionando la forma en que abordamos {kw}. Ya sea que estes comenzando o busques avanzar, contar con los prompts adecuados marca la diferencia entre resultados mediocres y resultados profesionales.</p>

<p>En esta guia te mostramos <strong>como usar ChatGPT, Claude y Gemini</strong> para mejorar tus resultados en {kw}. Cada seccion incluye prompts listos para copiar y pegar.</p>

<div class="toc"><div class="toc-title">Contenido</div>
<a href="#seccion1">1. {sections[0].get('titulo_seccion', 'Introduccion')}</a>
<a href="#seccion2">2. {sections[1].get('titulo_seccion', 'Conceptos clave') if len(sections) > 1 else 'Aspectos fundamentales'}</a>
<a href="#seccion3">3. {sections[2].get('titulo_seccion', 'Implementacion') if len(sections) > 2 else 'Puesta en practica'}</a>
</div>

<h2 id="seccion1">{sections[0].get('titulo_seccion', f'Introduccion a {kw}')}</h2>
<p>{sections[0].get('intro', f'Descubre como la IA puede ayudarte con {kw}.')}</p>
"""
    
    if "pasos" in sections[0]:
        body_html += f"<ol>{sections[0]['pasos']}</ol>"
    if "items" in sections[0]:
        body_html += f"<ul>{sections[0]['items']}</ul>"
    if "tabla_html" in sections[0]:
        body_html += sections[0]["tabla_html"]
    if "conclusion" in sections[0]:
        body_html += f"<p>{sections[0]['conclusion']}</p>"
    if "prompt" in sections[0]:
        body_html += f"""<div class="prompt-box"><div class="prompt-label">Prompt Recomendado</div><div class="prompt-text">{sections[0]['prompt']}</div></div>"""
    if "tip" in sections[0]:
        body_html += f"""<div class="tip-box"><div class="tip-label">Consejo</div><p>{sections[0]['tip']}</p></div>"""
    
    # Secciones 2 y 3
    for i in range(1, min(3, len(sections))):
        s = sections[i]
        body_html += f"""
<h2 id="seccion{i+1}">{s.get('titulo_seccion', f'Aspectos avanzados de {kw}')}</h2>
<p>{s.get('intro', f'Profundicemos en {kw} con prompts especificos.')}</p>"""
        if "pasos" in s:
            body_html += f"<ol>{s['pasos']}</ol>"
        if "items" in s:
            body_html += f"<ul>{s['items']}</ul>"
        if "prompt" in s:
            body_html += f"""<div class="prompt-box"><div class="prompt-label">Prompt para {kw}</div><div class="prompt-text">{s['prompt']}</div></div>"""
        if "tip" in s:
            body_html += f"""<div class="tip-box"><div class="tip-label">Consejo</div><p>{s['tip']}</p></div>"""
    
    # CTA
    body_html += f"""
<div class="cta-box">
<h3>Pack de {niche['name']}</h3>
<p>10 prompts premium sobre {kw} listos para usar. Resultados inmediatos.</p>
<a href="https://payhip.com/b/{niche['payhip']}" target="_blank" class="btn btn-primary">Conseguir por 9.99</a>
<a href="../../catalogo.html" class="btn" style="margin-left:8px;border:1px solid var(--gold);color:var(--gold);background:transparent">Ver Catalogo</a>
</div>
"""
    
    # FAQ
    body_html += f"""
<div class="faq-section">
<h3>Preguntas frecuentes sobre {kw}</h3>
<div class="faq-q"><summary>¿Que necesito para empezar con {kw}?</summary><p>Solo necesitas acceso a ChatGPT, Claude o Gemini. Todos nuestros prompts funcionan con cualquier plataforma de IA.</p></div>
<div class="faq-q"><summary>¿Cuanto tiempo se tarda en ver resultados con {kw}?</summary><p>La mayoria de nuestros usuarios ven mejoras significativas desde la primera semana de uso consistente.</p></div>
<div class="faq-q"><summary>¿Los prompts funcionan en espanol?</summary><p>Si, todos nuestros prompts estan disenados y probados en espanol para maximizar resultados.</p></div>
</div>
"""
    
    # Newsletter + footer
    body_html += """
<div class="newsletter-box">
<div class="nl-icon">✧</div>
<div class="nl-title">Recibe los mejores prompts de IA gratis</div>
<div class="nl-desc">Cada semana, 3 prompts exclusivos + tendencias directo a tu bandeja de entrada.</div>
<form class="nl-form" action="https://formsubmit.co/formulasia76@gmail.com" method="POST" onsubmit="fetch('https://909f85f8c7219d8f-95-63-166-157.serveousercontent.com/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:this.email.value})}).catch(()=>{});">
  <input type="hidden" name="_subject" value="Nuevo suscriptor NEO Labs">
  <input type="hidden" name="_next" value="https://magodago.github.io/neo-jarvis/neo-labs.html">
  <input type="hidden" name="_captcha" value="false">
  <input type="text" name="_honey" style="display:none">
  <input type="email" name="email" placeholder="tu@email.com" required class="nl-input">
  <button type="submit" class="nl-btn">Suscribirme</button>
</form>
</div>
</div>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catalogo</a><a href="../index.html">Blog</a><a href="https://payhip.com/b/98ens">Guia Gratuita</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>
let p=document.getElementById('progress');document.addEventListener('scroll',()=>{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'})
let s=0,n=document.getElementById('nav');document.addEventListener('scroll',()=>{let t=window.scrollY;if(t>s&&t>70)n.classList.add('hidden');else n.classList.remove('hidden');s=t})
</script>
<script data-goatcounter="https://davidformulas.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body></html>"""
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{seo_title} — NEO Labs</title>
<meta name="description" content="{seo_desc}">
<link rel="canonical" href="https://magodago.github.io/neo-jarvis/blog/{niche['slug']}/{slug}.html">
<meta property="og:title" content="{seo_title}">
<meta property="og:description" content="{seo_desc[:120]}">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}:root{{--brand:{niche['brand']};--brand-dark:{niche['brand_dark']};--brand-light:{niche['brand']}88;--bg:#050508;--bg2:#0c0c14;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}}
html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.8;touch-action:pan-y}}
a{{color:var(--brand);text-decoration:none}}a:hover{{filter:brightness(1.2)}}
.wrap{{max-width:780px;margin:0 auto;padding:0 24px}}
.breadcrumb{{font-size:.75rem;color:#6a6558;padding-top:90px;margin-bottom:8px}}.breadcrumb a{{color:#6a6558}}.breadcrumb a:hover{{color:var(--brand)}}
.article-header{{margin-bottom:28px}}
.article-header .cat-tag{{display:inline-block;padding:4px 12px;border-radius:100px;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;background:rgba(212,168,83,.15);color:var(--brand);margin-bottom:14px}}
.article-header h1{{font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2.2rem);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:10px}}
.article-header .meta{{display:flex;gap:20px;font-size:.8rem;color:#6a6558;flex-wrap:wrap}}
.article-body h2{{font-family:var(--font-display);font-size:1.25rem;font-weight:700;color:#fff;margin:30px 0 10px;letter-spacing:-.3px}}
.article-body p{{font-size:.92rem;color:var(--text-muted);line-height:1.8;margin-bottom:12px}}
.article-body p strong{{color:var(--text)}}
.article-body ul,.article-body ol{{padding-left:24px;margin-bottom:12px;color:var(--text-muted);font-size:.92rem;line-height:1.8}}
.prompt-box{{background:var(--bg3);border-left:3px solid var(--brand);border-radius:0 10px 10px 0;padding:16px 20px;margin:12px 0 20px}}
.prompt-box .prompt-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--brand);font-weight:600;margin-bottom:3px}}
.prompt-box .prompt-text{{font-size:.85rem;color:#d0c8bc;line-height:1.7;font-style:italic}}
.tip-box{{background:rgba(76,175,80,.06);border-left:3px solid #4caf50;border-radius:0 10px 10px 0;padding:12px 16px;margin:12px 0 20px}}
.tip-box .tip-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:#4caf50;font-weight:600;margin-bottom:2px}}
.tip-box p{{font-size:.85rem;color:#c0d0b8;line-height:1.7;margin:0}}
.cta-box{{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.9));border:1px solid rgba(212,168,83,.2);border-radius:14px;padding:28px 22px;text-align:center;margin:24px 0}}
.cta-box h3{{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--brand);margin-bottom:6px}}
.cta-box p{{color:var(--text-muted);font-size:.82rem;margin-bottom:14px}}
.btn{{padding:10px 24px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .3s;border:none;cursor:pointer;display:inline-block}}
.btn-primary{{background:linear-gradient(135deg,var(--brand-dark),var(--brand));color:#fff;box-shadow:0 4px 30px rgba(0,0,0,.3)}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(0,0,0,.5)}}
.toc{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 20px;margin:20px 0;font-size:.85rem}}
.toc-title{{font-family:var(--font-display);font-size:.7rem;letter-spacing:2px;font-weight:700;color:var(--brand);margin-bottom:8px;text-transform:uppercase}}
.toc a{{display:block;padding:3px 0;color:var(--text-muted);transition:color .2s;font-size:.82rem}}
.toc a:hover{{color:var(--brand)}}.toc a:before{{content:"▸ ";font-size:.65rem}}
.faq-section{{margin:24px 0}}.faq-q{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:12px 16px;margin-bottom:6px}}
.faq-q summary{{font-weight:600;font-size:.88rem;color:#fff;cursor:pointer;display:flex;align-items:center;gap:10px}}
.faq-q summary::marker{{color:var(--brand)}}.faq-q p{{font-size:.82rem;color:var(--text-muted);margin-top:6px;line-height:1.6}}
.newsletter-box{{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.2);border-radius:16px;padding:24px 20px;text-align:center;margin:28px 0}}
.nl-title{{font-family:var(--font-display);font-size:.95rem;font-weight:700;color:#fff;margin-bottom:4px}}
.nl-desc{{font-size:.78rem;color:var(--text-muted);margin-bottom:14px;max-width:380px;margin-left:auto;margin-right:auto}}
.nl-form{{display:flex;gap:8px;max-width:360px;margin:0 auto;flex-wrap:wrap}}
.nl-input{{flex:1;min-width:160px;padding:10px 14px;border-radius:8px;border:1px solid rgba(212,168,83,.2);background:rgba(5,5,8,.6);color:#fff;font-size:.82rem;outline:none}}
.nl-input:focus{{border-color:var(--brand)}}
.nl-btn{{padding:10px 18px;border-radius:8px;border:none;background:var(--brand);color:#050508;font-size:.75rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer}}
footer{{background:var(--bg2);border-top:1px solid rgba(255,255,255,.04);padding:36px 24px 20px;text-align:center}}
footer .logo{{font-family:var(--font-display);font-size:1.3rem;letter-spacing:4px;font-weight:700;margin-bottom:10px;text-transform:uppercase;color:#fff}}
footer .logo span{{color:var(--brand)}}
footer .links{{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:10px}}
footer .links a{{color:var(--text-muted);font-size:.78rem}}
footer .copy{{font-size:.68rem;color:#6a6558}}
#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,var(--brand-dark),var(--brand));z-index:9999;transition:width .1s}}
</style>
<script type="application/ld+json" class="s-hidden">{{"@context":"https://schema.org","@type":"Article","headline":"{seo_title}","description":"{seo_desc[:150]}","datePublished":"{today}","author":{{"@type":"Person","name":"NEO Labs"}},"publisher":{{"@type":"Organization","name":"NEO Labs"}},"mainEntityOfPage":{{"@type":"WebPage","@id":"https://magodago.github.io/neo-jarvis/blog/{niche['slug']}/{slug}.html"}}}}</script>
<meta name="google-site-verification" content="c_28XEsyfUVcGVbPpfkhujKtsO_XkyMJRjLwjhitFzQ" />
</head>
<body>
<div id="progress"></div>
<nav id="nav">
<div class="nav-logo">NE<span>O</span></div>
<ul class="nav-links">
<li><a href="../../neo-labs.html">Inicio</a></li>
<li><a href="../../catalogo.html">Catalogo</a></li>
<li><a href="../index.html">Blog</a></li>
</ul>
</nav>{body_html}"""

def main():
    print("=" * 60)
    print("PROGRAMMATIC SEO GENERATOR v1.0")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    total = 0
    nicho_dir = BLOG / "programacion"
    nicho_dir.mkdir(parents=True, exist_ok=True)
    
    # Nicho piloto: Programacion (80 keywords)
    keywords = [
        "como depurar codigo con chatgpt", "generar codigo python con ia",
        "revisar codigo con inteligencia artificial", "escribir tests automaticos con ia",
        "refactorizar codigo con chatgpt", "documentar codigo con ia",
        "traducir codigo entre lenguajes con ia", "generar sql queries con chatgpt",
        "explicar codigo legacy con ia", "optimizar rendimiento codigo con ia",
        "crear api rest con chatgpt", "generar express routes con ia",
        "escribir scripts bash con ia", "depurar javascript con chatgpt",
        "crear componentes react con ia", "generar html css con chatgpt",
        "escribir dockerfile con ia", "configurar nginx con chatgpt",
        "generar github actions con ia", "escribir documentacion tecnica con ia",
        "crear diagramas de flujo con ia", "generar diagramas uml con chatgpt",
        "analizar logs servidor con ia", "optimizar consultas sql con chatgpt",
        "generar seed data con ia", "crear migraciones base datos con ia",
        "escribir middleware express con ia", "generar modelos mongoose con ia",
        "crear endpoints rest con chatgpt", "escribir crud completo con ia",
        "generar jwt authentication con ia", "implementar oauth con chatgpt",
        "crear webhook con ia", "escribir lambda functions con chatgpt",
        "generar cloudformation templates con ia", "depurar terraform con ia",
        "escribir kubernetes manifests con ia", "crear helm charts con chatgpt",
        "generar ci cd pipeline con ia", "escribir readme profesional con ia",
        "generar changelog con ia", "crear api documentation con chatgpt",
        "escribir unit tests con ia", "generar integration tests con chatgpt",
        "crear mock data con ia", "escribir test cases con chatgpt"
    ]
    
    # Limitar a 40 para la prueba piloto (Programacion)
    batch = keywords[:40]
    
    print(f"\nGenerando {len(batch)} paginas para Programacion...")
    
    for i, kw in enumerate(batch):
        try:
            slug = slugify(kw)
            filepath = nicho_dir / f"{slug}.html"
            if filepath.exists():
                print(f"  ⏭️  {i+1}/{len(batch)} {slug}.html (ya existe)")
                total += 1
                continue
            
            # Generar contenido con Gemma 4 para 3 secciones
            sections = []
            for s_idx in range(3):
                content = generar_contenido_para_keyword(
                    {"slug":"programacion","name":"Programacion","brand":"#ab47bc","brand_dark":"#7b1fa2"},
                    kw, ["guia-paso-a-paso","lista-promesas","comparativa"][s_idx % 3]
                )
                sections.append(content)
                time.sleep(0.5)  # Pequeña pausa entre llamadas
            
            html = build_page(
                {"slug":"programacion","name":"Programacion","brand":"#ab47bc","brand_dark":"#7b1fa2","payhip":"XTEG5"},
                kw, sections, i
            )
            
            with open(filepath, "w") as f:
                f.write(html)
            
            total += 1
            print(f"  ✅ {i+1}/{len(batch)} {slug}.html ({len(html)} bytes)")
            
            if i < len(batch) - 1:
                time.sleep(0.5)  # Rate limit
                
        except Exception as e:
            print(f"  ❌ {kw}: {e}")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"✅ GENERADAS: {total} paginas")
    print(f"📁 {nicho_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
