#!/usr/bin/env python3
"""Generate all niche blog index pages at once."""
import os
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

NICHES = [
    {
        "slug": "finanzas",
        "name": "Finanzas",
        "brand": "#66bb6a",
        "brand_light": "#a5d6a7",
        "brand_dark": "#388e3c",
        "hero_img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1400&q=85",
        "desc": "Noticias, guias y recursos sobre finanzas personales con inteligencia artificial. Presupuestos, ahorro, inversiones y planificacion financiera.",
        "hero_desc": "Controla tu dinero, ahorra mas, invierte mejor con la ayuda de la inteligencia artificial.",
        "product_name": "Finanzas",
        "payhip_id": "uP62G",
        "articles": [
            ("10 Prompts de IA para tus Finanzas Personales", "guia", "Controla tu presupuesto y ahorra con prompts de IA.", "../prompts-ia-finanzas-personales.html"),
            ("Como crear un presupuesto automatico con IA", "Tutorial", "Un prompt que analiza tus gastos y crea un plan.", "../prompts-ia-finanzas-personales.html"),
            ("ChatGPT para analizar tus inversiones", "Guia", "Evaluacion de cartera y recomendaciones con IA.", "../prompts-ia-finanzas-personales.html"),
            ("5 Prompts para ahorrar mas cada mes", "Guia", "Estrategias de ahorro automaticas potenciadas con IA.", "../prompts-ia-finanzas-personales.html"),
            ("Claude vs ChatGPT para finanzas", "Comparativa", "Cual IA es mejor para gestionar tu dinero.", "../prompts-ia-finanzas-personales.html"),
            ("Nuevas funciones de IA para banca online", "Noticia", "Los bancos integran IA en sus apps.", "../prompts-ia-finanzas-personales.html"),
        ]
    },
    {
        "slug": "marketing",
        "name": "Marketing",
        "brand": "#42a5f5",
        "brand_light": "#90caf9",
        "brand_dark": "#1976d2",
        "hero_img": "https://images.unsplash.com/photo-1557838923-2985c318be48?w=1400&q=85",
        "desc": "Noticias, guias y recursos sobre marketing digital con inteligencia artificial. SEO, redes sociales, email marketing y copywriting.",
        "hero_desc": "Crea campanas que convierten, contenido que engancha y estrategias que funcionan con IA.",
        "product_name": "Marketing",
        "payhip_id": "Q5RYA",
        "articles": [
            ("15 Prompts de IA para Marketing Digital en 2026", "guia", "SEO, redes, email y copywriting con IA.", "../prompts-ia-marketing-digital.html"),
            ("Como crear una estrategia SEO con IA", "Tutorial", "Keywords, contenido y link building automatizado.", "../prompts-ia-marketing-digital.html"),
            ("ChatGPT para copywriting persuasivo", "Guia", "Escribe textos que venden con un solo prompt.", "../prompts-ia-marketing-digital.html"),
            ("Automatiza tus campanas de email con IA", "Tutorial", "Secuencias que convierten sin esfuerzo manual.", "../prompts-ia-marketing-digital.html"),
            ("Google Ads optimizados con IA", "Guia", "Crea campanas que maximizan tu ROI.", "../prompts-ia-marketing-digital.html"),
            ("Nuevas herramientas de IA para marketers", "Noticia", "Lo ultimo en tecnologia para marketing.", "../prompts-ia-marketing-digital.html"),
        ]
    },
    {
        "slug": "programacion",
        "name": "Programacion",
        "brand": "#ab47bc",
        "brand_light": "#ce93d8",
        "brand_dark": "#7b1fa2",
        "hero_img": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1400&q=85",
        "desc": "Noticias, guias y recursos sobre programacion con inteligencia artificial. Debugging, code review, testing y arquitectura.",
        "hero_desc": "Codifica mejor, mas rapido y con menos errores usando inteligencia artificial como tu senior developer de respaldo.",
        "product_name": "Programacion",
        "payhip_id": "XTEG5",
        "articles": [
            ("12 Prompts de IA para Programar Mejor", "guia", "Debugging, code review y testing con IA.", "../prompts-ia-programacion.html"),
            ("Como debuggear codigo con ChatGPT", "Tutorial", "Encuentra bugs en segundos con el prompt adecuado.", "../prompts-ia-programacion.html"),
            ("Code review automatico con IA", "Guia", "Tu senior developer personal revisa tu codigo.", "../prompts-ia-programacion.html"),
            ("Genera tests automaticos con un prompt", "Tutorial", "Cobertura completa sin escribir una linea.", "../prompts-ia-programacion.html"),
            ("Refactoriza codigo legacy con IA", "Guia", "Transforma codigo antiguo sin romper nada.", "../prompts-ia-programacion.html"),
            ("Claude vs ChatGPT para programar", "Comparativa", "Cual IA genera mejor codigo.", "../prompts-ia-programacion.html"),
        ]
    },
    {
        "slug": "estudiantes",
        "name": "Educacion",
        "brand": "#ffa726",
        "brand_light": "#ffcc80",
        "brand_dark": "#ef6c00",
        "hero_img": "https://images.unsplash.com/photo-1523050854058-8df90110c296?w=1400&q=85",
        "desc": "Noticias, guias y recursos para estudiantes con inteligencia artificial. Resumenes, examenes, ensayos y organizacion del estudio.",
        "hero_desc": "Estudia menos, aprende mas. La IA como tu profesor particular 24/7.",
        "product_name": "Educacion",
        "payhip_id": "M3eqn",
        "articles": [
            ("10 Prompts de IA para Estudiar Mejor", "guia", "Resume textos, prepara examenes y aprende mas rapido.", "../prompts-ia-estudiantes.html"),
            ("Como resumir textos academicos con IA", "Tutorial", "Extrae lo esencial de cualquier texto en segundos.", "../prompts-ia-estudiantes.html"),
            ("Prepara tus examenes con ChatGPT", "Guia", "Preguntas de practica y planes de estudio personalizados.", "../prompts-ia-estudiantes.html"),
            ("Escribe ensayos academicos con IA", "Tutorial", "Estructura, argumentos y citas en minutos.", "../prompts-ia-estudiantes.html"),
            ("Organiza tu semestre con prompts de IA", "Guia", "Plan de estudio, calendario y seguimiento automatico.", "../prompts-ia-estudiantes.html"),
            ("Nuevas herramientas de IA para estudiantes", "Noticia", "Apps y plataformas que cambiaran tu forma de estudiar.", "../prompts-ia-estudiantes.html"),
        ]
    },
    {
        "slug": "rrhh",
        "name": "RRHH",
        "brand": "#ec407a",
        "brand_light": "#f48fb1",
        "brand_dark": "#c2185b",
        "hero_img": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1400&q=85",
        "desc": "Noticias, guias y recursos sobre recursos humanos con inteligencia artificial. Seleccion, evaluacion, onboarding y gestion del talento.",
        "hero_desc": "Optimiza tus procesos de RRHH con IA. Selecciona mejor, reten mas talento.",
        "product_name": "RRHH",
        "payhip_id": "KragB",
        "articles": [
            ("8 Prompts de IA para Recursos Humanos", "guia", "Seleccion, evaluacion y comunicacion interna con IA.", "../prompts-ia-recursos-humanos.html"),
            ("Como seleccionar candidatos con IA", "Tutorial", "Criba curricular y entrevistas asistidas por IA.", "../prompts-ia-recursos-humanos.html"),
            ("Evaluaciones de desempeno con ChatGPT", "Guia", "Feedback constructivo y planes de desarrollo automaticos.", "../prompts-ia-recursos-humanos.html"),
            ("Onboarding automatizado con prompts de IA", "Tutorial", "Los primeros 90 dias de tu nuevo empleado optimizados.", "../prompts-ia-recursos-humanos.html"),
            ("Clima laboral analizado con IA", "Guia", "Encuestas y analisis de satisfaccion automaticos.", "../prompts-ia-recursos-humanos.html"),
            ("Nuevas tendencias de IA en RRHH", "Noticia", "Como la IA esta transformando la gestion del talento.", "../prompts-ia-recursos-humanos.html"),
        ]
    },
]

def gen_index(niche):
    slug = niche["slug"]
    name = niche["name"]
    brand = niche["brand"]
    brand_light = niche["brand_light"]
    brand_dark = niche["brand_dark"]
    hero_img = niche["hero_img"]
    desc = niche["desc"]
    hero_desc = niche["hero_desc"]
    product_name = niche["product_name"]
    payhip_id = niche["payhip_id"]
    
    articles_html = ""
    for i, (title, tag, snippet, url) in enumerate(niche["articles"], 1):
        tag_type = "Guia" if tag in ("guia", "Guia") else tag
        articles_html += f"""
    <a href="{url}" class="article-card reveal">
      <img src="https://images.unsplash.com/photo-{1512314889357}+e157c22f938d?w=400&q=85" alt="">
      <div class="overlay"></div>
      <div class="a-content">
        <span class="a-tag">{tag_type}</span>
        <h3>{title}</h3>
        <p>{snippet}</p>
        <div class="a-meta">Disponible</div>
      </div>
    </a>"""
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog de {name} con IA — NEO Labs</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://magodago.github.io/neo-jarvis/blog/{slug}/">
<meta property="og:title" content="Blog de {name} con IA — NEO Labs">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}:root{{--brand:{brand};--brand-light:{brand_light};--brand-dark:{brand_dark};--bg:#050508;--bg2:#0c0c14;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}}
html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.7}}a{{color:var(--brand);text-decoration:none;transition:all .3s}}a:hover{{color:var(--brand-light)}}
nav{{position:fixed;top:0;left:0;right:0;z-index:1000;padding:14px 40px;display:flex;justify-content:space-between;align-items:center;background:rgba(5,5,8,.9);backdrop-filter:blur(20px);border-bottom:1px solid rgba(212,168,83,.1);transition:transform .35s}}nav.hidden{{transform:translateY(-100%)}}
.nav-logo{{font-family:var(--font-display);font-size:1.3rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#fff}}.nav-logo span{{color:var(--gold,#d4a853)}}
.nav-links{{display:flex;gap:28px;list-style:none;font-size:.82rem;letter-spacing:1.5px;text-transform:uppercase}}
.nav-links a{{color:var(--text-muted);position:relative}}.nav-links a::after{{content:'';position:absolute;bottom:-4px;left:0;width:0;height:1px;background:var(--brand);transition:width .35s}}.nav-links a:hover::after,.nav-links a:hover{{width:100%;color:var(--brand)}}
@media(max-width:768px){{.nav-links{{display:none}};nav{{padding:14px 20px}}}}
.hero{{min-height:70vh;display:flex;align-items:center;justify-content:center;text-align:center;position:relative}}
.hero .bg-img{{position:absolute;inset:0;object-fit:cover;z-index:0}}.hero .bg-overlay{{position:absolute;inset:0;z-index:1;background:linear-gradient(135deg,rgba(5,5,8,.88) 20%,rgba(5,5,8,.5) 60%,rgba(5,5,8,.15))}}
.hero .hero-content{{position:relative;z-index:2;max-width:700px;padding:100px 24px 60px}}
.hero .hero-badge{{display:inline-block;padding:7px 18px;border:1px solid rgba(212,168,83,.3);border-radius:100px;font-size:.65rem;letter-spacing:3px;text-transform:uppercase;color:var(--brand);margin-bottom:24px;backdrop-filter:blur(4px);text-shadow:0 1px 8px rgba(0,0,0,.6)}}
.hero .hero-title{{font-family:var(--font-display);font-size:clamp(1.8rem,4.5vw,3.8rem);font-weight:800;line-height:1.08;letter-spacing:-2px;margin-bottom:12px;color:#fff;text-shadow:0 2px 16px rgba(0,0,0,.5)}}
.hero .hero-title .brand{{color:var(--brand)}}.hero .hero-desc{{font-size:.95rem;color:#f0e8d8;max-width:500px;margin:0 auto;line-height:1.8;text-shadow:0 1px 10px rgba(0,0,0,.5)}}
.strip{{background:linear-gradient(135deg,var(--brand-dark),var(--brand),var(--brand-light));padding:16px 24px;text-align:center}}.strip p{{color:var(--bg);font-family:var(--font-display);font-size:.85rem;font-weight:600}}.strip a{{color:var(--bg);text-decoration:underline;font-weight:700}}
.content{{padding:48px 24px;background:var(--bg2)}}.wrap{{max-width:1100px;margin:0 auto}}
.section-head{{text-align:center;margin-bottom:36px}}.section-head .label{{font-size:.65rem;letter-spacing:4px;text-transform:uppercase;color:var(--brand);margin-bottom:6px}}
.section-head h2{{font-family:var(--font-display);font-size:clamp(1.3rem,2.5vw,1.8rem);font-weight:700;color:#fff;letter-spacing:-.5px}}
.article-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
.article-card{{position:relative;border-radius:14px;overflow:hidden;min-height:240px;text-decoration:none;display:flex;align-items:flex-end}}
.article-card img{{position:absolute;inset:0;object-fit:cover;z-index:0;transition:transform .5s}}
.article-card:hover img{{transform:scale(1.05)}}
.article-card .overlay{{position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,rgba(5,5,8,.92) 15%,rgba(5,5,8,.25) 55%,transparent)}}
.article-card .a-content{{position:relative;z-index:2;padding:24px 20px;width:100%}}
.article-card .a-tag{{display:inline-block;padding:2px 8px;border-radius:100px;font-size:.55rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;background:rgba(212,168,83,.2);color:var(--brand-light);margin-bottom:6px}}
.article-card h3{{font-family:var(--font-display);font-size:.95rem;font-weight:600;color:#fff;margin-bottom:4px;line-height:1.2}}
.article-card p{{font-size:.78rem;color:#c0b8a8;line-height:1.5;margin-bottom:4px}}
.article-card .a-meta{{font-size:.65rem;color:#8a8070}}
.cta-box{{background:linear-gradient(135deg,rgba(212,168,83,.05),rgba(5,5,8,.9));border:1px solid rgba(212,168,83,.18);border-radius:16px;padding:36px 28px;text-align:center;margin:32px 0}}
.cta-box h3{{font-family:var(--font-display);font-size:1.15rem;font-weight:700;color:var(--brand);margin-bottom:6px}}
.cta-box p{{color:var(--text-muted);font-size:.85rem;margin-bottom:18px}}
.btn{{padding:11px 28px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .35s;border:none;cursor:pointer;display:inline-block;background:linear-gradient(135deg,var(--brand-dark),var(--brand),var(--brand-light));color:var(--bg);box-shadow:0 4px 30px rgba(212,168,83,.18)}}
.btn:hover{{transform:translateY(-2px);box-shadow:0 8px 40px rgba(212,168,83,.3)}}
.btn-outline{{border:1px solid var(--brand);color:var(--brand);background:transparent}}.btn-outline:hover{{background:rgba(212,168,83,.1)}}
footer{{background:var(--bg2);border-top:1px solid rgba(255,255,255,.04);padding:40px 24px 24px;text-align:center}}
footer .logo{{font-family:var(--font-display);font-size:1.3rem;font-weight:700;margin-bottom:12px;text-transform:uppercase;color:#fff}}footer .logo span{{color:var(--gold,#d4a853)}}
footer .links{{display:flex;gap:22px;justify-content:center;flex-wrap:wrap;margin-bottom:12px}}footer .links a{{color:var(--text-muted);font-size:.8rem;letter-spacing:1px}}footer .links a:hover{{color:var(--brand)}}
footer .copy{{font-size:.7rem;color:#6a6558}}
.reveal{{opacity:0;transform:translateY(18px);transition:opacity .5s ease,transform .5s ease}}.reveal.visible{{opacity:1;transform:translateY(0)}}
#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,var(--brand),var(--brand-light));z-index:9999;transition:width .1s}}
@media(max-width:768px){{.article-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div id="progress"></div>
<nav id="nav"><div class="nav-logo">NE<span>O</span></div><ul class="nav-links"><li><a href="../../neo-labs.html">Inicio</a></li><li><a href="../../catalogo.html">Catalogo</a></li><li><a href="../index.html">Blog</a></li></ul></nav>
<section class="hero">
<img class="bg-img" src="{hero_img}" alt=""><div class="bg-overlay"></div>
<div class="hero-content reveal"><div class="hero-badge">{name} con IA</div><h1 class="hero-title">Blog de <span class="brand">{name}</span></h1><p class="hero-desc">{hero_desc}</p></div>
</section>
<section class="strip"><p><strong>Gratis:</strong> <a href="https://payhip.com/b/98ens" target="_blank">5 Prompts de IA para Multiplicar tu Productividad</a></p></section>
<section class="content"><div class="wrap">
<div class="section-head"><div class="label">Nuestros articulos</div><h2>Contenido sobre <span style="color:var(--brand)">{name.lower()} con IA</span></h2></div>
<div class="article-grid">{articles_html}
</div>
<div class="cta-box reveal"><h3>Pack de {product_name}</h3><p>10 prompts premium listos para copiar y pegar con ChatGPT, Claude y Gemini.</p><a href="https://payhip.com/b/{payhip_id}" target="_blank" class="btn">Comprar 9.99</a><a href="../../catalogo.html" class="btn btn-outline" style="margin-left:8px">Ver Catalogo</a></div>
</div></section>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catalogo</a><a href="../index.html">Blog</a><a href="https://payhip.com/b/98ens">Guia Gratuita</a></div><p class="copy">&copy; 2026 NEO Labs &mdash; Blog de {name}</p></footer>
<script>
let p=document.getElementById('progress');document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}})
let s=0,n=document.getElementById('nav');document.addEventListener('scroll',()=>{{if(window.scrollY>s&&window.scrollY>70)n.classList.add('hidden');else n.classList.remove('hidden');s=window.scrollY}})
let o=new IntersectionObserver(e=>{{e.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('visible')}})}},{{threshold:.1}})
document.querySelectorAll('.reveal').forEach(e=>o.observe(e))
</script>
</body>
</html>"""
    
    path = BLOG / slug / "index.html"
    path.write_text(html, encoding="utf-8")
    print(f"✓ {slug}/index.html — {name}")

if __name__ == "__main__":
    for niche in NICHES:
        gen_index(niche)
    print("Todos los blogs nicho creados!")
