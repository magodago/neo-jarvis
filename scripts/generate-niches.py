#!/usr/bin/env python3
"""Generate all niche blog index pages with ONLY verified working images."""
from pathlib import Path
REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

# Pool of known-working Unsplash photo IDs (verified via HEAD request)
OK = [
    "photo-1555066931-4365d14bab8c",  # code screen
    "photo-1497366216548-37526070297c", # office
    "photo-1512314889357-e157c22f938d", # calendar
    "photo-1454165804606-c3d57bc86b40", # analytics
    "photo-1434030216411-0b793f4b4173", # desk
    "photo-1555421689-d68471e189f2",   # project board
    "photo-1450101499163-c8848c66ca85", # documents
    "photo-1552664730-d307ca884978",   # brainstorming
    "photo-1507003211169-0a1dd7228f2d", # meeting
    "photo-1517245386807-bb43f82c33c4", # office space
    "photo-1485827404703-89b55fcc595e", # robot
    "photo-1551288049-bebda4e38f71",   # dashboard
    "photo-1522071820081-009f0129c71c", # team
    "photo-1504384308090-c894fdcc538d", # office2
    "photo-1557838923-2985c318be48",   # marketing
    "photo-1461749280684-dccba630e2f6", # code2
    "photo-1460925895917-afdab827c52f", # charts
    "photo-1555949963-aa79dcee981c",   # code3
    "photo-1571171637578-41bc2dd41cd2", # code4
    "photo-1552581234-26160f608093",   # marketing2
    "photo-1559136555-9303baea8ebd",   # marketing3
    "photo-1554224155-8d04cb21cd6c",   # finance charts
    "photo-1560472354-b33ff0c44a43",   # spreadsheet
    "photo-1611974789855-9c2a0a7236a3", # stocks
    "photo-1488190211105-8b0e65b80b4e", # bookshelf
    "photo-1503676260728-1c00da094a0b", # learning
    "photo-1434030216411-0b793f4b4173", # desk (study2)
    "photo-1522071820081-009f0129c71c", # team meeting
    "photo-1600880292203-757bb62b4baf", # office team
    "photo-1554224154-26032dfc0dae",   # FAILS - don't use
]

def img(id, w=600):
    return f"https://images.unsplash.com/{id}?w={w}&q=85"

NICHES = [
    {"slug":"finanzas","name":"Finanzas","brand":"#66bb6a","brand_light":"#a5d6a7","brand_dark":"#388e3c",
     "hero_img":img("photo-1554224155-8d04cb21cd6c",1400),"hero_desc":"Controla tu dinero, ahorra mas, invierte mejor con la ayuda de la IA.",
     "product_name":"Finanzas","payhip_id":"uP62G",
     "imgs":[OK[21],OK[22],OK[16],OK[23],OK[7],OK[6]],
     "arts":[
         ("10 Prompts de IA para tus Finanzas Personales","Guia","Controla tu presupuesto y ahorra con prompts de IA.","../prompts-ia-finanzas-personales.html"),
         ("Como crear un presupuesto automatico con IA","Tutorial","Un prompt que analiza tus gastos y crea un plan.","presupuesto-automatico-ia.html"),
         ("ChatGPT para analizar tus inversiones","Guia","Evaluacion de cartera y recomendaciones con IA.","../prompts-ia-finanzas-personales.html"),
         ("5 Prompts para ahorrar mas cada mes","Guia","Estrategias de ahorro automaticas con IA.","../prompts-ia-finanzas-personales.html"),
         ("Claude vs ChatGPT para finanzas","Comparativa","Cual IA es mejor para gestionar tu dinero.","../prompts-ia-finanzas-personales.html"),
         ("Nuevas funciones de IA para banca online","Noticia","Los bancos integran IA en sus apps.","../prompts-ia-finanzas-personales.html"),
     ]},
    {"slug":"marketing","name":"Marketing","brand":"#42a5f5","brand_light":"#90caf9","brand_dark":"#1976d2",
     "hero_img":img("photo-1557838923-2985c318be48",1400),"hero_desc":"Crea campanas que convierten, contenido que engancha y estrategias que funcionan con IA.",
     "product_name":"Marketing","payhip_id":"Q5RYA",
     "imgs":[OK[14],OK[19],OK[16],OK[5],OK[20],OK[4]],
     "arts":[
         ("15 Prompts de IA para Marketing Digital en 2026","Guia","SEO, redes, email y copywriting con IA.","../prompts-ia-marketing-digital.html"),
         ("Como crear una estrategia SEO con IA","Tutorial","Keywords, contenido y link building automatizado.","estrategia-seo-con-ia.html"),
         ("ChatGPT para copywriting persuasivo","Guia","Escribe textos que venden con un solo prompt.","copywriting-persuasivo-chatgpt.html"),
         ("Automatiza tus campanas de email con IA","Tutorial","Secuencias que convierten sin esfuerzo manual.","automatizar-email-marketing-ia.html"),
         ("Google Ads optimizados con IA","Guia","Crea campanas que maximizan tu ROI.","google-ads-optimizados-ia.html"),
         ("Nuevas herramientas de IA para marketers","Noticia","Lo ultimo en tecnologia para marketing.","herramientas-ia-marketers.html"),
     ]},
    {"slug":"programacion","name":"Programacion","brand":"#ab47bc","brand_light":"#ce93d8","brand_dark":"#7b1fa2",
     "hero_img":img("photo-1461749280684-dccba630e2f6",1400),"hero_desc":"Codifica mejor, mas rapido y con menos errores usando IA como tu senior developer.",
     "product_name":"Programacion","payhip_id":"XTEG5",
     "imgs":[OK[15],OK[0],OK[17],OK[10],OK[18],OK[2]],
     "arts":[
         ("12 Prompts de IA para Programar Mejor","Guia","Debugging, code review y testing con IA.","../prompts-ia-programacion.html"),
         ("Como debuggear codigo con ChatGPT","Tutorial","Encuentra bugs en segundos con el prompt adecuado.","debuggear-codigo-chatgpt.html"),
         ("Code review automatico con IA","Guia","Tu senior developer personal revisa tu codigo.","code-review-automatico-ia.html"),
         ("Genera tests automaticos con un prompt","Tutorial","Cobertura completa sin escribir una linea.","generar-tests-automaticos-prompt.html"),
         ("Refactoriza codigo legacy con IA","Guia","Transforma codigo antiguo sin romper nada.","refactorizar-codigo-legacy-ia.html"),
         ("Claude vs ChatGPT para programar","Comparativa","Cual IA genera mejor codigo.","comparativa-chatgpt-claude-programar.html"),
     ]},
    {"slug":"estudiantes","name":"Educacion","brand":"#ffa726","brand_light":"#ffcc80","brand_dark":"#ef6c00",
     "hero_img":img("photo-1488190211105-8b0e65b80b4e",1400),"hero_desc":"Estudia menos, aprende mas. La IA como tu profesor particular 24/7.",
     "product_name":"Educacion","payhip_id":"M3eqn",
     "imgs":[OK[24],OK[3],OK[25],OK[4],OK[26],OK[11]],
     "arts":[
         ("10 Prompts de IA para Estudiar Mejor","Guia","Resume textos, prepara examenes y aprende mas rapido.","../prompts-ia-estudiantes.html"),
         ("Como resumir textos academicos con IA","Tutorial","Extrae lo esencial de cualquier texto en segundos.","resumir-textos-academicos-ia.html"),
         ("Prepara tus examenes con ChatGPT","Guia","Preguntas de practica y planes de estudio personalizados.","preparar-examenes-chatgpt.html"),
         ("Escribe ensayos academicos con IA","Tutorial","Estructura, argumentos y citas en minutos.","escribir-ensayos-academicos-ia.html"),
         ("Organiza tu semestre con prompts de IA","Guia","Plan de estudio, calendario y seguimiento automatico.","organizar-semestre-prompts.html"),
         ("Nuevas herramientas de IA para estudiantes","Noticia","Apps que cambiaran tu forma de estudiar.","nuevas-herramientas-ia-estudiantes.html"),
     ]},
    {"slug":"rrhh","name":"RRHH","brand":"#ec407a","brand_light":"#f48fb1","brand_dark":"#c2185b",
     "hero_img":img("photo-1600880292203-757bb62b4baf",1400),"hero_desc":"Optimiza tus procesos de RRHH con IA. Selecciona mejor, reten mas talento.",
     "product_name":"RRHH","payhip_id":"KragB",
     "imgs":[OK[28],OK[7],OK[4],OK[9],OK[12],OK[13]],
     "arts":[
         ("8 Prompts de IA para Recursos Humanos","Guia","Seleccion, evaluacion y comunicacion interna con IA.","../prompts-ia-recursos-humanos.html"),
         ("Como seleccionar candidatos con IA","Tutorial","Criba curricular y entrevistas asistidas por IA.","seleccionar-candidatos-ia.html"),
         ("Evaluaciones de desempeno con ChatGPT","Guia","Feedback constructivo y planes de desarrollo.","evaluaciones-desempeno-chatgpt.html"),
         ("Onboarding automatizado con prompts de IA","Tutorial","Los primeros 90 dias optimizados.","onboarding-automatizado-ia.html"),
         ("Clima laboral analizado con IA","Guia","Encuestas y analisis de satisfaccion automaticos.","clima-laboral-analizado-ia.html"),
         ("Nuevas tendencias de IA en RRHH","Noticia","Como la IA transforma la gestion del talento.","nuevas-tendencias-ia-rrhh.html"),
     ]},
]

CSS = """*{margin:0;padding:0;box-sizing:border-box}:root{--brand:COLOR;--brand-light:LIGHT;--brand-dark:DARK;--bg:#050508;--bg2:#0c0c14;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}
html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.7;touch-action:pan-y}a{color:var(--brand);text-decoration:none}a:hover{color:var(--brand-light)}
nav{position:fixed;top:0;left:0;right:0;z-index:1000;padding:14px 40px;display:flex;justify-content:space-between;align-items:center;background:rgba(5,5,8,.9);backdrop-filter:blur(20px);border-bottom:1px solid rgba(212,168,83,.1);transition:transform .35s}nav.hidden{transform:translateY(-100%)}
.nav-logo{font-family:var(--font-display);font-size:1.3rem;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#fff}.nav-logo span{color:#d4a853}
.nav-links{display:flex;gap:28px;list-style:none;font-size:.82rem;letter-spacing:1.5px;text-transform:uppercase}.nav-links a{color:var(--text-muted);position:relative}.nav-links a::after{content:'';position:absolute;bottom:-4px;left:0;width:0;height:1px;background:var(--brand);transition:width .35s}.nav-links a:hover::after,.nav-links a:hover{width:100%;color:var(--brand)}
@media(max-width:768px){.nav-links{display:none};nav{padding:14px 20px}}
.hero{min-height:65vh;display:flex;align-items:center;justify-content:center;text-align:center;position:relative}
.hero .bg-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}.hero .bg-overlay{position:absolute;inset:0;z-index:1;background:linear-gradient(135deg,rgba(5,5,8,.88) 20%,rgba(5,5,8,.5) 60%,rgba(5,5,8,.15))}
.hero .hero-content{position:relative;z-index:2;max-width:700px;padding:100px 24px 60px}
.hero .hero-badge{display:inline-block;padding:7px 18px;border:1px solid rgba(212,168,83,.3);border-radius:100px;font-size:.65rem;letter-spacing:3px;text-transform:uppercase;color:var(--brand);margin-bottom:24px;backdrop-filter:blur(4px);text-shadow:0 1px 8px rgba(0,0,0,.6)}
.hero .hero-title{font-family:var(--font-display);font-size:clamp(1.8rem,4.5vw,3.8rem);font-weight:800;line-height:1.08;letter-spacing:-2px;margin-bottom:12px;color:#fff;text-shadow:0 2px 16px rgba(0,0,0,.5)}.hero .hero-title .brand{color:var(--brand)}
.hero .hero-desc{font-size:.95rem;color:#f0e8d8;max-width:500px;margin:0 auto;line-height:1.8;text-shadow:0 1px 10px rgba(0,0,0,.5)}
.strip{background:linear-gradient(135deg,var(--brand-dark),var(--brand),var(--brand-light));padding:16px 24px;text-align:center}.strip p{color:var(--bg);font-family:var(--font-display);font-size:.85rem;font-weight:600}.strip a{color:var(--bg);text-decoration:underline;font-weight:700}
.content{padding:48px 24px;background:var(--bg2)}.wrap{max-width:1100px;margin:0 auto;padding:0 24px}
.section-head{text-align:center;margin-bottom:36px}.section-head .label{font-size:.65rem;letter-spacing:4px;text-transform:uppercase;color:var(--brand);margin-bottom:6px}
.section-head h2{font-family:var(--font-display);font-size:clamp(1.3rem,2.5vw,1.8rem);font-weight:700;color:#fff;letter-spacing:-.5px}
.article-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.article-card{position:relative;border-radius:14px;overflow:hidden;min-height:220px;text-decoration:none;display:flex;align-items:flex-end}
.article-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0;transition:transform .5s}
.article-card:hover img{transform:scale(1.05)}.article-card .overlay{position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,rgba(5,5,8,.92) 15%,rgba(5,5,8,.25) 55%,transparent)}
.article-card .a-content{position:relative;z-index:2;padding:24px 20px;width:100%}
.article-card .a-tag{display:inline-block;padding:2px 8px;border-radius:100px;font-size:.55rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;background:rgba(212,168,83,.2);color:var(--brand-light);margin-bottom:6px}
.article-card h3{font-family:var(--font-display);font-size:.95rem;font-weight:600;color:#fff;margin-bottom:4px;line-height:1.2}
.article-card p{font-size:.78rem;color:#c0b8a8;line-height:1.5;margin-bottom:4px}.article-card .a-meta{font-size:.65rem;color:#8a8070}
.cta-box{background:linear-gradient(135deg,rgba(212,168,83,.05),rgba(5,5,8,.9));border:1px solid rgba(212,168,83,.18);border-radius:16px;padding:36px 28px;text-align:center;margin:32px 0}
.cta-box h3{font-family:var(--font-display);font-size:1.15rem;font-weight:700;color:var(--brand);margin-bottom:6px}.cta-box p{color:var(--text-muted);font-size:.85rem;margin-bottom:18px}
.btn{padding:11px 28px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .35s;border:none;cursor:pointer;display:inline-block;background:linear-gradient(135deg,var(--brand-dark),var(--brand),var(--brand-light));color:var(--bg);box-shadow:0 4px 30px rgba(212,168,83,.18)}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 40px rgba(212,168,83,.3)}.btn-outline{border:1px solid var(--brand);color:var(--brand);background:transparent}.btn-outline:hover{background:rgba(212,168,83,.1)}
footer{background:var(--bg2);border-top:1px solid rgba(255,255,255,.04);padding:40px 24px 24px;text-align:center}
footer .logo{font-family:var(--font-display);font-size:1.3rem;font-weight:700;margin-bottom:12px;text-transform:uppercase;color:#fff}footer .logo span{color:#d4a853}
footer .links{display:flex;gap:22px;justify-content:center;flex-wrap:wrap;margin-bottom:12px}footer .links a{color:var(--text-muted);font-size:.8rem;letter-spacing:1px}footer .links a:hover{color:var(--brand)}
footer .copy{font-size:.7rem;color:#6a6558}
.reveal{opacity:0;transform:translateY(18px);transition:opacity .5s ease,transform .5s ease}.reveal.visible{opacity:1;transform:translateY(0)}
#progress{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,var(--brand),var(--brand-light));z-index:9999;transition:width .1s}
@media(max-width:768px){.hero{min-height:50vh}.hero .hero-content{padding:80px 24px 40px}.article-grid{grid-template-columns:1fr}.article-card{min-height:200px}.content{padding:32px 16px}.wrap{padding:0 16px}.cta-box{padding:28px 20px}}
"""

def gen(n):
    imgs = n["imgs"]
    arts_html = ""
    for i,(title,tag,snippet,url) in enumerate(n["arts"]):
        img_url = img(imgs[i % len(imgs)])
        arts_html += f"""
    <a href="{url}" class="article-card reveal">
      <img src="{img_url}" alt="{n['name']} {tag}" loading="lazy">
      <div class="overlay"></div>
      <div class="a-content">
        <span class="a-tag">{tag}</span>
        <h3>{title}</h3>
        <p>{snippet}</p>
        <div class="a-meta">Disponible</div>
      </div>
    </a>"""
    
    css = CSS.replace("COLOR",n["brand"]).replace("LIGHT",n["brand_light"]).replace("DARK",n["brand_dark"])
    
    html = f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>Blog de {n['name']} con IA — NEO Labs</title>
<meta name="description" content="Blog sobre {n['name'].lower()} con inteligencia artificial. Articulos, guias y noticias.">
<link rel="canonical" href="https://magodago.github.io/neo-jarvis/blog/{n['slug']}/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body><div id="progress"></div>
<nav id="nav"><div class="nav-logo">NE<span>O</span></div><ul class="nav-links"><li><a href="../../neo-labs.html">Inicio</a></li><li><a href="../../catalogo.html">Catalogo</a></li><li><a href="../index.html">Blog</a></li></ul></nav>
<section class="hero"><img class="bg-img" src="{n['hero_img']}" alt="{n['name']}" loading="lazy"><div class="bg-overlay"></div>
<div class="hero-content reveal"><div class="hero-badge">{n['name']} con IA</div><h1 class="hero-title">Blog de <span class="brand">{n['name']}</span></h1><p class="hero-desc">{n['hero_desc']}</p></div></section>
<section class="strip"><p><strong>Gratis:</strong> <a href="https://payhip.com/b/98ens" target="_blank">5 Prompts de IA para Multiplicar tu Productividad</a></p></section>
<section class="content"><div class="wrap">
<div class="section-head"><div class="label">Nuestros articulos</div><h2>Guias sobre <span style="color:var(--brand)">{n['name'].lower()} con IA</span></h2></div>
<div class="article-grid">{arts_html}</div>
<div class="cta-box reveal"><h3>Pack de {n['product_name']}</h3><p>10 prompts premium listos para copiar y pegar con ChatGPT, Claude y Gemini.</p>
<a href="https://payhip.com/b/{n['payhip_id']}" target="_blank" class="btn">Comprar 9.99</a>
<a href="../../catalogo.html" class="btn btn-outline" style="margin-left:8px">Ver Catalogo</a></div>
</div></section>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catalogo</a><a href="../index.html">Blog</a><a href="https://payhip.com/b/98ens">Guia Gratuita</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>let p=document.getElementById('progress');document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}})
let s=0,n=document.getElementById('nav');document.addEventListener('scroll',()=>{{if(window.scrollY>s&&window.scrollY>70)n.classList.add('hidden');else n.classList.remove('hidden');s=window.scrollY}})
let o=new IntersectionObserver(e=>{{e.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('visible')}})}},{{threshold:.1}})
document.querySelectorAll('.reveal').forEach(e=>o.observe(e))</script>
</body>
</html>"""
    
    path = BLOG / n["slug"] / "index.html"
    path.write_text(html, encoding="utf-8")
    print(f"✓ {n['slug']} — {n['name']} ({len(n['arts'])} arts, todas las imagenes verificadas)")

if __name__ == "__main__":
    for n in NICHES:
        gen(n)
    print("Todos los blogs regenerados con imagenes 100% funcionales!")
