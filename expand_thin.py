#!/usr/bin/env python3
"""Expand thin articles (21 lines) with full Gemma 4 content."""
import json, subprocess, re, sys
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Thin articles and their topics for Gemma 4
THIN_ARTICLES = [
    ("productividad", "automatiza-bandeja-entrada-prompt", "Automatiza tu bandeja de entrada con prompts de IA", "productividad", "EYojF"),
    ("productividad", "chatgpt-modo-productividad-calendario", "ChatGPT en modo productividad: gestiona tu calendario con IA", "productividad", "EYojF"),
    ("productividad", "reducir-carga-trabajo-50-prompts", "Reduce tu carga de trabajo un 50% con estos prompts de IA", "productividad", "EYojF"),
    ("marketing", "google-ads-optimizados-ia", "Google Ads optimizados con inteligencia artificial", "marketing", "Q5RYA"),
    ("marketing", "herramientas-ia-marketers", "Nuevas herramientas de IA para marketers en 2026", "marketing", "Q5RYA"),
    ("finanzas", "presupuesto-automatico-ia", "Crea tu presupuesto automático mensual con IA", "finanzas", "uP62G"),
    ("rrhh", "seleccionar-candidatos-ia", "Seleccionar candidatos con inteligencia artificial", "rrhh", "KragB"),
    ("rrhh", "onboarding-automatizado-ia", "Onboarding automatizado con IA para nuevos empleados", "rrhh", "KragB"),
    ("rrhh", "nuevas-tendencias-ia-rrhh", "Nuevas tendencias de IA en recursos humanos 2026", "rrhh", "KragB"),
    ("rrhh", "evaluaciones-desempeno-chatgpt", "Evaluaciones de desempeño con ChatGPT", "rrhh", "KragB"),
    ("rrhh", "clima-laboral-analizado-ia", "Clima laboral analizado con inteligencia artificial", "rrhh", "KragB"),
    ("programacion", "debuggear-codigo-chatgpt", "Debuggear código con ChatGPT: guía práctica", "programacion", "XTEG5"),
    ("programacion", "generar-tests-automaticos-prompt", "Generar tests automáticos con un solo prompt", "programacion", "XTEG5"),
    ("programacion", "comparativa-chatgpt-claude-programar", "ChatGPT vs Claude: ¿cuál es mejor para programar?", "programacion", "XTEG5"),
    ("programacion", "code-review-automatico-ia", "Code review automático con inteligencia artificial", "programacion", "XTEG5"),
    ("programacion", "refactorizar-codigo-legacy-ia", "Refactorizar código legacy con ayuda de IA", "programacion", "XTEG5"),
    ("estudiantes", "preparar-examenes-chatgpt", "Preparar exámenes con ChatGPT: técnicas de estudio con IA", "estudiantes", "M3eqn"),
    ("estudiantes", "organizar-semestre-prompts", "Organiza tu semestre universitario con prompts de IA", "estudiantes", "M3eqn"),
    ("estudiantes", "nuevas-herramientas-ia-estudiantes", "Nuevas herramientas de IA para estudiantes en 2026", "estudiantes", "M3eqn"),
    ("estudiantes", "escribir-ensayos-academicos-ia", "Escribir ensayos académicos con inteligencia artificial", "estudiantes", "M3eqn"),
    ("estudiantes", "resumir-textos-academicos-ia", "Resumir textos académicos con IA: técnicas y prompts", "estudiantes", "M3eqn"),
]

NICHE_INFO = {
    "productividad": {"brand": "#d4a853", "brand_dark": "#b8922f", "brand_light": "#f0d68a", "hero": "photo-1497366216548-37526070297c"},
    "finanzas": {"brand": "#66bb6a", "brand_dark": "#388e3c", "brand_light": "#a5d6a7", "hero": "photo-1554224155-8d04cb21cd6c"},
    "marketing": {"brand": "#42a5f5", "brand_dark": "#1976d2", "brand_light": "#90caf9", "hero": "photo-1557838923-2985c318be48"},
    "programacion": {"brand": "#ab47bc", "brand_dark": "#7b1fa2", "brand_light": "#ce93d8", "hero": "photo-1461749280684-dccba630e2f6"},
    "estudiantes": {"brand": "#ffa726", "brand_dark": "#ef6c00", "brand_light": "#ffcc80", "hero": "photo-1488190211105-8b0e65b80b4e"},
    "rrhh": {"brand": "#ec407a", "brand_dark": "#c2185b", "brand_light": "#f48fb1", "hero": "photo-1600880292203-757bb62b4baf"},
}

IMAGES = [
    "photo-1555066931-4365d14bab8c","photo-1512314889357-e157c22f938d","photo-1454165804606-c3d57bc86b40",
    "photo-1434030216411-0b793f4b4173","photo-1555421689-d68471e189f2","photo-1450101499163-c8848c66ca85",
    "photo-1552664730-d307ca884978","photo-1551288049-bebda4e38f71","photo-1522071820081-009f0129c71c",
    "photo-1555949963-aa79dcee981c","photo-1552581234-26160f608093","photo-1460925895917-afdab827c52f",
]

def generate_content(niche, slug, title):
    """Generate full article content using Gemma 4."""
    
    info = NICHE_INFO[niche]
    
    prompt = f"""Eres un redactor SEO experto en español. Vas a escribir un artículo completo de blog.

TÍTULO: {title}
NICHO: {niche}
AUDIENCIA: Hispanohablantes interesados en IA aplicada

ESTRUCTURA EXACTA (genera SOLO el HTML de .article-body):
- <p>Introducción de 2-3 frases que enganche</p>
- <h2>Primer punto importante</h2>
- <p>Explicación detallada de 3-4 frases</p>
- <div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">"prompt útil aquí"</div></div>
- <h2>Segundo punto importante</h2>
- <p>Explicación detallada de 3-4 frases</p>
- <div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">"otro prompt útil"</div></div>
- <h2>Tercer punto importante</h2>
- <p>Explicación detallada de 3-4 frases con ejemplos prácticos</p>
- <div class="prompt-box"><div class="prompt-label">Prompt avanzado</div><div class="prompt-text">"tercer prompt detallado"</div></div>
- <p>Conclusión de 2-3 frases que invite a usar los prompts</p>

REGLAS:
- 400-600 palabras total
- Español correcto con acentos y ñ
- Incluye 3 prompts reales y útiles en prompt-boxes
- Los prompts deben ser accionables, específicos
- Tono: experto pero accesible
- NO incluyas etiquetas html fuera del body
- NO incluyas <!DOCTYPE>, <html>, <head>, <style>, etc
- Solo devuelve el contenido que va dentro de <div class="article-body">"""

    r = subprocess.run(["curl", "-s", OLLAMA_URL, "-d", json.dumps({
        "model": "gemma4",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2048}
    })], capture_output=True, text=True, timeout=180)
    
    data = json.loads(r.stdout)
    return data.get("response", "")

def rebuild_article(niche, slug, title, body_html, brand, payhip):
    """Rebuild the full HTML file with the generated content."""
    filepath = REPO / "blog" / niche / f"{slug}.html"
    info = NICHE_INFO[niche]
    
    # Create a template with full content
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{title} — NEO Labs</title>
<meta name="description" content="Guía práctica sobre {title.lower()}. Aprende paso a paso con prompts de IA probados y consejos expertos.">
<link rel="canonical" href="https://magodago.github.io/neo-jarvis/blog/{niche}/{slug}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="Guía práctica y prompts de IA para {slug.replace('-',' ')}.">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<meta name="google-site-verification" content="c_28XEsyfUVcGVbPpfkhujKtsO_XkyMJRjLwjhitFzQ" />
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--brand:{info["brand"]};--brand-dark:{info["brand_dark"]};--brand-light:{info["brand_light"]};--bg:#050508;--bg2:#0c0c14;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.8}}
a{{color:var(--brand);text-decoration:none;transition:all .3s}}
a:hover{{color:var(--brand-light)}}
img{{max-width:100%;display:block}}
nav{{position:fixed;top:0;left:0;right:0;z-index:1000;padding:14px 40px;display:flex;justify-content:space-between;align-items:center;background:rgba(5,5,8,.9);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.06);transition:transform .35s}}
nav.hidden{{transform:translateY(-100%)}}
.nav-logo{{font-family:var(--font-display);font-size:1.3rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#fff}}
.nav-logo span{{color:var(--brand)}}
.wrap{{max-width:780px;margin:0 auto;padding:0 24px}}
.hero{{padding:100px 0 18px;position:relative}}
.breadcrumb{{font-size:.75rem;color:#6a6558;margin-bottom:8px;padding-top:40px}}
.breadcrumb a{{color:#6a6558}}
.breadcrumb a:hover{{color:var(--brand)}}
.article-header{{margin-bottom:28px}}
.article-header .cat-tag{{display:inline-block;padding:4px 12px;border-radius:100px;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;background:rgba(102,187,106,.15);color:var(--brand);margin-bottom:14px}}
.article-header h1{{font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2.2rem);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:10px}}
.article-header .meta{{font-size:.8rem;color:#6a6558}}
.article-body h2{{font-family:var(--font-display);font-size:1.25rem;font-weight:700;color:#fff;margin:36px 0 10px;scroll-margin-top:80px}}
.article-body h2:before{{content:"#";color:var(--brand);margin-right:8px;opacity:.6}}
.article-body p{{font-size:.92rem;color:var(--text-muted);line-height:1.8;margin-bottom:14px}}
.prompt-box{{background:var(--bg3);border-left:3px solid var(--brand);border-radius:0 10px 10px 0;padding:18px 22px;margin:14px 0 22px}}
.prompt-box .prompt-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--brand);font-weight:600;margin-bottom:4px}}
.prompt-box .prompt-text{{font-size:.85rem;color:#d0c8bc;line-height:1.7;font-style:italic}}
.cta-box{{background:linear-gradient(135deg,rgba(102,187,106,.06),rgba(5,5,8,.9));border:1px solid rgba(102,187,106,.2);border-radius:14px;padding:32px 24px;text-align:center;margin:28px 0}}
.cta-box h3{{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--brand);margin-bottom:6px}}
.cta-box p{{color:var(--text-muted);font-size:.85rem;margin-bottom:16px}}
.btn{{display:inline-block;padding:11px 28px;border-radius:8px;font-family:var(--font-display);font-size:.8rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;background:var(--brand);color:#050508!important;transition:all .3s;border:none;cursor:pointer}}
.btn:hover{{transform:translateY(-1px);box-shadow:0 4px 20px rgba(102,187,106,.3)}}
.podcast-player{{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,rgba(212,168,83,.08),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.15);border-radius:14px;padding:14px 18px;margin:24px 0;cursor:pointer;transition:all .3s}}
.podcast-player:hover{{border-color:rgba(212,168,83,.35);background:linear-gradient(135deg,rgba(212,168,83,.12),rgba(5,5,8,.95))}}
.podcast-icon{{font-size:1.6rem;flex-shrink:0}}
.podcast-info{{flex:1}}
.podcast-label{{font-family:var(--font-display);font-size:.65rem;letter-spacing:2px;font-weight:700;color:var(--brand);margin-bottom:2px}}
.podcast-desc{{font-size:.78rem;color:var(--text-muted)}}
.toc{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 20px;margin:24px 0;font-size:.85rem}}
.toc-title{{font-family:var(--font-display);font-size:.7rem;letter-spacing:2px;font-weight:700;color:var(--brand);margin-bottom:8px;text-transform:uppercase}}
.toc a{{display:block;padding:3px 0;color:var(--text-muted);transition:color .2s;font-size:.82rem}}
.toc a:hover{{color:var(--brand)}}
.toc a:before{{content:"▸ ";font-size:.65rem}}
.faq-section{{margin:28px 0}}
.faq-q{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px 18px;margin-bottom:6px}}
.faq-q summary{{font-weight:600;font-size:.88rem;color:#fff;cursor:pointer;display:flex;align-items:center;gap:10px}}
.faq-q summary::marker{{color:var(--brand)}}
.faq-q p{{font-size:.82rem;color:var(--text-muted);margin-top:8px;line-height:1.6}}
.related-row{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:24px 0}}
.related-card{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px;transition:all .3s;text-decoration:none!important}}
.related-card:hover{{border-color:rgba(212,168,83,.25);transform:translateY(-2px)}}
.related-card .rc-tag{{font-size:.6rem;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;color:var(--brand)}}
.related-card .rc-title{{font-size:.82rem;color:#fff;margin-top:4px;font-weight:500}}
.related-card .rc-desc{{font-size:.72rem;color:var(--text-muted);margin-top:2px}}
footer{{border-top:1px solid rgba(255,255,255,.06);padding:24px 0 40px;margin-top:40px}}
footer .logo{{font-family:var(--font-display);font-size:.9rem;font-weight:700;letter-spacing:3px;color:#fff;margin-bottom:6px}}
footer .logo span{{color:var(--brand)}}
footer .links{{display:flex;gap:20px;margin-bottom:6px}}
footer .links a{{font-size:.75rem;color:#6a6558}}
footer .copy{{font-size:.7rem;color:#4a4538;margin-top:4px}}
</style>
</head>
<body>
<nav id="nav"><a href="../../neo-labs.html" class="nav-logo">NE<span>O</span></a></nav>
<div id="progress"></div>
<div class="wrap">
<div class="breadcrumb"><a href="../../neo-labs.html">Inicio</a> / <a href="index.html">Blog {niche.capitalize()}</a> / <span>{title[:50]}...</span></div>
<div class="article-header">
<span class="cat-tag">Guía</span>
<h1>{title}</h1>
<div class="meta">{datetime.now().strftime('%-d %B %Y')}</div>
</div>
{body_html}
<div class="cta-box"><h3>Pack completo de {niche.capitalize()}</h3><p>Lleva tu productividad al siguiente nivel con prompts premium.</p><a href="https://payhip.com/bundle/{payhip}" target="_blank" class="btn" rel="noopener">Comprar 9,99€</a></div>
</div>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catálogo</a><a href="../index.html">Blog</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>
let p=document.getElementById('progress');
document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}});
let s=0,n=document.getElementById('nav');
document.addEventListener('scroll',()=>{{let t=window.scrollY;if(t>s&&t>70)n.classList.add('hidden');else n.classList.remove('hidden');s=t}});
</script>
<script data-goatcounter="https://neo-jarvis.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<noscript><img src="https://neo-jarvis.goatcounter.com/count?p=/test"></noscript>
</body>
</html>"""
    
    filepath.write_text(html, encoding="utf-8")
    print(f"✅ {niche}/{slug}.html escrito ({len(body_html)} chars body)")

def process_one(niche, slug, title):
    filepath = REPO / "blog" / niche / f"{slug}.html"
    if not filepath.exists():
        print(f"❌ No existe: {filepath}")
        return False
    
    # Check if thin (21 lines or body < 300 chars)
    html = filepath.read_text(encoding="utf-8")
    body_m = re.search(r'<div class="article-body">(.*?)</div>', html, re.DOTALL)
    body_text = ""
    if body_m:
        body_text = re.sub(r'<[^>]+>', ' ', body_m.group(1)).strip()
    
    if len(body_text) > 300:
        print(f"⏭️  Ya tiene contenido: {niche}/{slug} ({len(body_text)} chars)")
        return True
    
    print(f"📝 Expandiendo: {title}...")
    body = generate_content(niche, slug, title)
    if body:
        # Clean up markdown code fences
        body = re.sub(r'```html\s*', '', body)
        body = re.sub(r'```\s*', '', body)
        body = body.strip()
        rebuild_article(niche, slug, title, body, NICHE_INFO[niche]["brand"], NICHE_INFO[niche].get("payhip"))
        return True
    else:
        print(f"❌ Falló generación para {slug}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    
    success = 0
    for niche, slug, title, niche_name, payhip in THIN_ARTICLES:
        if process_one(niche, slug, title):
            success += 1
        else:
            print(f"⚠️  Skipping {slug}")
    
    print(f"\n📊 {success}/{len(THIN_ARTICLES)} artículos expandidos")
