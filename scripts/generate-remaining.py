#!/usr/bin/env python3
"""Generate remaining placeholder articles for all niches."""
from pathlib import Path
BLOG = Path.home() / "neo-jarvis" / "blog"

# Template-based articles for remaining placeholders
BATCH = [
    # Marketing (2 more)
    {"slug":"marketing","file":"google-ads-optimizados-ia","tag":"Guia","title":"Google Ads optimizados con IA","desc":"Crea campanas de Google Ads que maximizan tu ROI con prompts de IA. Optimiza pujas, keywords y anuncios.","prompts":[
        ("Estructura de campana","Eres un experto en Google Ads. Para mi negocio de [sector] con presupuesto de [cantidad]: 1) Estructura de campana recomendada, 2) 10 keywords con match type, 3) 3 anuncios de texto con diferentes enfoques, 4) Estrategia de puja inicial, 5) Metricas clave para monitorizar."),
        ("Optimizacion de campana","Eres un media buyer senior. Esta campana de Google Ads tiene estos datos: [metricas]. Analiza: 1) Que keywords estan dando mejor ROI, 2) Anuncios con peor rendimiento y por que, 3) Ajustes de puja recomendados, 4) Nuevas keywords para aniadir, 5) Presupuesto optimo por campana."),
    ],"payhip":"Q5RYA"},
    {"slug":"marketing","file":"herramientas-ia-marketers","tag":"Noticia","title":"Nuevas herramientas de IA para marketers","desc":"Lo ultimo en herramientas de IA para marketing digital. Analisis, automatizacion y optimizacion.","prompts":[],"payhip":"Q5RYA"},

    # Programacion (4 more)
    {"slug":"programacion","file":"code-review-automatico-ia","tag":"Guia","title":"Code review automatico con IA","desc":"Tu senior developer personal revisa tu codigo. Aprende a usar prompts de IA para code review efectivo.","prompts":[
        ("Revision de codigo","Eres un senior developer haciendo code review. Revisa este codigo: [PEGA CODIGO]. Evalua: 1) Posibles bugs, 2) Code smells, 3) Problemas de rendimiento, 4) Seguridad, 5) Mejores practicas. Prioriza cada issue y sugiere correccion con codigo."),
        ("Mejora de calidad","Eres un arquitecto de software. Revisa la estructura de este codigo: [PEGA CODIGO]. Sugiere mejoras de: 1) Arquitectura, 2) Legibilidad, 3) Mantenibilidad, 4) Testing, 5) Documentacion. Dame el codigo refactorizado."),
    ],"payhip":"XTEG5"},
    {"slug":"programacion","file":"generar-tests-automaticos-prompt","tag":"Tutorial","title":"Genera tests automaticos con un prompt","desc":"Cubre tu codigo con tests sin escribir una linea. Prompts de IA para generar tests unitarios y de integracion.","prompts":[
        ("Tests unitarios","Eres un QA engineer. Genera tests para este codigo: [PEGA CODIGO]. Incluye: tests unitarios con cobertura de casos normal, borde y error. Usa [framework de tests]. Dame el codigo completo de tests."),
    ],"payhip":"XTEG5"},
    {"slug":"programacion","file":"refactorizar-codigo-legacy-ia","tag":"Guia","title":"Refactoriza codigo legacy con IA","desc":"Transforma codigo antiguo sin romper nada. Prompts de IA para refactorizar codigo legacy de forma segura.","prompts":[],"payhip":"XTEG5"},
    {"slug":"programacion","file":"comparativa-chatgpt-claude-programar","tag":"Comparativa","title":"Claude vs ChatGPT para programar","desc":"Comparamos la calidad de codigo generado por Claude y ChatGPT en multiples lenguajes y escenarios.","prompts":[],"payhip":"XTEG5"},

    # Estudiantes (4 more)
    {"slug":"estudiantes","file":"preparar-examenes-chatgpt","tag":"Guia","title":"Prepara tus examenes con ChatGPT","desc":"Preguntas de practica, planes de estudio y simulacros de examen generados por IA para aprobar con mejores notas.","prompts":[
        ("Simulacro de examen","Eres un profesor de [materia]. Genera un examen de practica sobre [tema] con: 10 preguntas tipo test, 5 preguntas de desarrollo, 2 problemas practicos. Incluye solucion detallada y criterios de evaluacion. Nivel: [universitario/bachillerato]."),
        ("Plan de estudio","Eres un tutor academico. Mi examen de [materia] es en [fecha]. Temario: [lista]. Horas disponibles: [X]h/semana. Crea un plan de estudio dia a dia que priorice los temas mas importantes y deje tiempo para repaso final."),
    ],"payhip":"M3eqn"},
    {"slug":"estudiantes","file":"escribir-ensayos-academicos-ia","tag":"Tutorial","title":"Escribe ensayos academicos con IA","desc":"Estructura, argumentos y citas en minutos. Aprende a usar IA para escribir ensayos academicos de calidad.","prompts":[],"payhip":"M3eqn"},
    {"slug":"estudiantes","file":"organizar-semestre-prompts","tag":"Guia","title":"Organiza tu semestre con prompts de IA","desc":"Plan de estudio, calendario y seguimiento automatico. La IA como tu asistente academico personal.","prompts":[],"payhip":"M3eqn"},
    {"slug":"estudiantes","file":"nuevas-herramientas-ia-estudiantes","tag":"Noticia","title":"Nuevas herramientas de IA para estudiantes","desc":"Apps y plataformas que cambiaran tu forma de estudiar. Las herramientas de IA mas utiles para estudiantes.","prompts":[],"payhip":"M3eqn"},

    # RRHH (4 more)
    {"slug":"rrhh","file":"evaluaciones-desempeno-chatgpt","tag":"Guia","title":"Evaluaciones de desempeno con ChatGPT","desc":"Feedback constructivo y planes de desarrollo automaticos. Mejora tu proceso de evaluacion con IA.","prompts":[],"payhip":"KragB"},
    {"slug":"rrhh","file":"onboarding-automatizado-ia","tag":"Tutorial","title":"Onboarding automatizado con prompts de IA","desc":"Los primeros 90 dias de tu nuevo empleado optimizados con IA. Plan de onboarding automatico.","prompts":[],"payhip":"KragB"},
    {"slug":"rrhh","file":"clima-laboral-analizado-ia","tag":"Guia","title":"Clima laboral analizado con IA","desc":"Encuestas y analisis de satisfaccion automaticos para mejorar el ambiente de trabajo en tu empresa.","prompts":[],"payhip":"KragB"},
    {"slug":"rrhh","file":"nuevas-tendencias-ia-rrhh","tag":"Noticia","title":"Nuevas tendencias de IA en RRHH","desc":"Como la inteligencia artificial esta transformando la gestion del talento y los procesos de recursos humanos.","prompts":[],"payhip":"KragB"},
]

def write_article(a):
    slug = a["slug"]
    file = a["file"]
    tag = a["tag"]
    title = a["title"]
    desc = a["desc"]
    payhip = a["payhip"]
    prompts = a["prompts"]
    
    brand_colors = {
        "marketing": {"b":"#42a5f5","d":"#1976d2","l":"#90caf9"},
        "programacion": {"b":"#ab47bc","d":"#7b1fa2","l":"#ce93d8"},
        "estudiantes": {"b":"#ffa726","d":"#ef6c00","l":"#ffcc80"},
        "rrhh": {"b":"#ec407a","d":"#c2185b","l":"#f48fb1"},
    }
    c = brand_colors[slug]
    
    prompts_html = ""
    for label, text in prompts:
        prompts_html += f'<h2>Prompt: {label}</h2><div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text"><strong>Prompt:</strong> {text}</div></div>'
    
    if not prompts_html:
        prompts_html = f"<p>{desc}</p>"
    
    html = f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>{title} — NEO Labs</title><meta name="description" content="{desc}">
<link rel="canonical" href="https://magodago.github.io/neo-jarvis/blog/{slug}/{file}.html"><meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}:root{{--brand:{c['b']};--bg:#050508;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif}}html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--text);font-family:'Sora',sans-serif;overflow-x:hidden;line-height:1.8;touch-action:pan-y}}a{{color:var(--brand);text-decoration:none}}a:hover{{filter:brightness(1.2)}}.wrap{{max-width:780px;margin:0 auto;padding:0 24px}}.breadcrumb{{font-size:.75rem;color:#6a6558;padding-top:100px;margin-bottom:8px}}.article-header{{margin-bottom:32px}}.article-header .cat-tag{{display:inline-block;padding:4px 12px;border-radius:100px;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;background:rgba(102,187,106,.15);color:var(--brand);margin-bottom:14px}}.article-header h1{{font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2.2rem);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:10px}}.article-header .meta{{font-size:.8rem;color:#6a6558}}.article-body h2{{font-family:var(--font-display);font-size:1.25rem;font-weight:700;color:#fff;margin:36px 0 10px}}.article-body p{{font-size:.92rem;color:var(--text-muted);line-height:1.8;margin-bottom:14px}}.prompt-box{{background:var(--bg3);border-left:3px solid var(--brand);border-radius:0 10px 10px 0;padding:18px 22px;margin:14px 0 22px}}.prompt-box .prompt-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--brand);font-weight:600;margin-bottom:4px}}.prompt-box .prompt-text{{font-size:.85rem;color:#d0c8bc;line-height:1.7;font-style:italic}}.cta-box{{background:linear-gradient(135deg,rgba(102,187,106,.06),rgba(5,5,8,.9));border:1px solid rgba(102,187,106,.2);border-radius:14px;padding:32px 24px;text-align:center;margin:28px 0}}.cta-box h3{{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--brand);margin-bottom:6px}}.cta-box p{{color:var(--text-muted);font-size:.85rem;margin-bottom:16px}}.btn{{padding:11px 28px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .35s;border:none;cursor:pointer;display:inline-block;background:linear-gradient(135deg,{c['d']},{c['b']},{c['l']});color:#fff;box-shadow:0 4px 30px rgba(102,187,106,.18)}}.btn:hover{{transform:translateY(-2px)}}footer{{background:#0c0c14;border-top:1px solid rgba(255,255,255,.04);padding:40px 24px 24px;text-align:center}}footer .logo{{font-family:var(--font-display);font-size:1.3rem;font-weight:700;margin-bottom:12px;text-transform:uppercase;color:#fff}}footer .copy{{font-size:.7rem;color:#6a6558}}#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,{c['d']},{c['l']});z-index:9999}}@media(max-width:768px){{.breadcrumb{{padding-top:80px}}}}</style></head>
<body><div id="progress"></div><div class="wrap">
<div class="breadcrumb"><a href="../../neo-labs.html">Inicio</a> / <a href="index.html">Blog {slug.capitalize()}</a> / <span>{title[:40]}</span></div>
<div class="article-header"><span class="cat-tag">{tag}</span><h1>{title}</h1><div class="meta">8 Junio 2026</div></div>
<div class="article-body">
{prompts_html}
<div class="cta-box"><h3>Pack de {slug.capitalize()}</h3><p>10 prompts premium listos para usar.</p><a href="https://payhip.com/b/{payhip}" target="_blank" class="btn">Comprar 9.99</a></div>
</div>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catalogo</a><a href="../index.html">Blog</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>let p=document.getElementById('progress');document.addEventListener('scroll',()=>{{let h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}});let s=0,n=document.getElementById('nav');document.addEventListener('scroll',()=>{{let t=window.scrollY;if(t>s&&t>70)n.classList.add('hidden');else n.classList.remove('hidden');s=t}})</script>
</body>
</html>'''
    
    path = BLOG / slug / f"{file}.html"
    path.write_text(html, encoding="utf-8")
    print(f"  ✓ {slug}/{file}.html — {title}")
    return file

if __name__ == "__main__":
    for a in BATCH:
        write_article(a)
    print(f"\nTotal: {len(BATCH)} articulos generados!")
