#!/usr/bin/env python3
"""
NEO Web Generator v1
Genera una web premium con la paleta de colores del sector.
Uso: python3 generator.py --negocio "Restaurante La Brasa" --sector restaurante --plan basica
"""
import json, os, sys, re, shutil
from datetime import datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Paletas por sector
PALETTES = {
    "restaurante": {"primary":"#DC2626","accent":"#F97316","accent2":"#FCD34D","bg":"#0A0A0A","bg2":"#111111","text":"#FEF3C7","card":"rgba(255,255,255,.04)","name":"Restaurantes"},
    "clinica":     {"primary":"#06B6D4","accent":"#10B981","accent2":"#34D399","bg":"#0F172A","bg2":"#1E293B","text":"#F0F9FF","card":"rgba(255,255,255,.04)","name":"Clínicas"},
    "abogado":     {"primary":"#1E40AF","accent":"#64748B","accent2":"#94A3B8","bg":"#0F172A","bg2":"#1E293B","text":"#F8FAFC","card":"rgba(255,255,255,.04)","name":"Abogados"},
    "taller":      {"primary":"#EA580C","accent":"#6B7280","accent2":"#9CA3AF","bg":"#111827","bg2":"#1F2937","text":"#FAFAFA","card":"rgba(255,255,255,.04)","name":"Talleres"},
    "estetica":    {"primary":"#DB2777","accent":"#D946EF","accent2":"#E879F9","bg":"#1A0A1A","bg2":"#2D1B2E","text":"#FDF2F8","card":"rgba(255,255,255,.05)","name":"Estética"},
    "tecnologia":  {"primary":"#3B82F6","accent":"#8B5CF6","accent2":"#A78BFA","bg":"#070B14","bg2":"#0C1320","text":"#F0F2F5","card":"rgba(255,255,255,.04)","name":"Tecnología"},
}

def generate_web(negocio, sector, plan="basica", telefono="", direccion=""):
    pal = PALETTES.get(sector, PALETTES["tecnologia"])
    slug = re.sub(r'[^a-z0-9]+', '-', negocio.lower()).strip('-')
    
    plan_titles = {"basica": "NEO Básica", "premium": "NEO Premium", "full": "NEO Full"}
    plan_name = plan_titles.get(plan, "NEO Básica")
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{negocio}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --primary:{pal['primary']};--accent:{pal['accent']};--accent2:{pal['accent2']};
  --bg:{pal['bg']};--bg2:{pal['bg2']};--text:{pal['text']};
  --card:{pal['card']};--border:rgba(255,255,255,.06);--radius:16px;
  font-family:'Inter',-apple-system,sans-serif;
}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}}

/* Effects */
.glow-orb{{position:fixed;border-radius:50%;filter:blur(80px);pointer-events:none;z-index:0;animation:orbFloat 25s ease-in-out infinite}}
.go1{{width:500px;height:500px;background:radial-gradient(circle,{pal['primary']}15,transparent);top:-150px;right:-100px}}
.go2{{width:400px;height:400px;background:radial-gradient(circle,{pal['accent']}10,transparent);bottom:10%;left:-100px}}
@keyframes orbFloat{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-30px,30px)}}}}

/* Nav */
.nav{{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;position:fixed;top:0;left:0;right:0;z-index:100;background:rgba({','.join(str(int(pal['bg'][i:i+2],16)) for i in (1,3,5))},.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
.nav-brand{{font-size:.8rem;font-weight:800;letter-spacing:1px}}
.nav-links{{display:flex;gap:24px;list-style:none}}
.nav-links a{{color:var(--text);text-decoration:none;font-size:.82rem;transition:color .2s}}
.nav-links a:hover{{color:var(--primary)}}
.nav-cta{{padding:10px 24px;border-radius:100px;background:var(--primary);color:#fff;text-decoration:none;font-size:.78rem;font-weight:600;transition:all .2s}}
.nav-cta:hover{{transform:scale(1.05)}}

/* Hero */
.hero{{min-height:90vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:100px 20px 60px;position:relative;z-index:1}}
.hero-label{{font-size:.6rem;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:var(--primary);margin-bottom:16px}}
.hero-title{{font-size:clamp(2rem,5vw,3.5rem);font-weight:900;letter-spacing:-1.5px;margin-bottom:12px;line-height:1.1}}
.hero-title span{{color:var(--primary)}}
.hero-sub{{font-size:clamp(.9rem,1.5vw,1.1rem);color:var(--text);opacity:.7;max-width:500px;margin-bottom:8px}}
.hero-btn{{display:inline-block;margin-top:32px;padding:16px 40px;border-radius:100px;font-size:.9rem;font-weight:700;background:var(--primary);color:#fff;border:none;cursor:pointer;text-decoration:none;transition:all .3s}}
.hero-btn:hover{{transform:scale(1.05);box-shadow:0 0 30px {pal['primary']}40}}

/* Sections */
.section{{padding:80px 20px;position:relative;z-index:1}}
.section:nth-child(even){{background:var(--bg2)}}
.section-inner{{max-width:1000px;margin:0 auto}}
.section-tag{{font-size:.55rem;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--primary);margin-bottom:8px}}
.section-title{{font-size:clamp(1.3rem,2.5vw,1.8rem);font-weight:800;margin-bottom:16px}}
.section-text{{font-size:.9rem;color:var(--text);opacity:.7;line-height:1.7;max-width:600px}}

/* Services */
.services-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:24px}}
.service-card{{padding:24px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);text-align:center}}
.service-icon{{font-size:2rem;margin-bottom:12px}}
.service-title{{font-size:.95rem;font-weight:700;margin-bottom:8px}}
.service-desc{{font-size:.8rem;opacity:.6;line-height:1.5}}

/* Contact */
.contact-box{{max-width:500px;margin:24px auto 0;padding:32px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius)}}
.contact-box a{{color:var(--primary);text-decoration:none;font-weight:600}}
.contact-box p{{margin-bottom:8px;font-size:.9rem}}

/* Footer */
.footer{{text-align:center;padding:40px 20px;position:relative;z-index:1}}
.footer::before{{content:'';display:block;width:30px;height:2px;background:var(--primary);margin:0 auto 12px;border-radius:2px}}
.footer-brand{{font-size:.65rem;font-weight:600;opacity:.5;letter-spacing:1px}}
.footer-sub{{font-size:.55rem;opacity:.3;margin-top:4px}}

/* Mobile */
@media(max-width:640px){{.nav-links{{display:none}}}}
</style>
</head>
<body>
<div class="glow-orb go1"></div>
<div class="glow-orb go2"></div>

<nav class="nav">
  <div class="nav-brand">{negocio}</div>
  <ul class="nav-links">
    <li><a href="#servicios">Servicios</a></li>
    <li><a href="#contacto">Contacto</a></li>
  </ul>
  <a href="#contacto" class="nav-cta">Contactar</a>
</nav>

<section class="hero">
  <div class="hero-label">{negocio}</div>
  <h1 class="hero-title">Bienvenido a <span>{negocio}</span></h1>
  <p class="hero-sub">Profesionales comprometidos con ofrecerte el mejor servicio en {pal['name'].lower()}.</p>
  <a href="#contacto" class="hero-btn">Contáctanos</a>
</section>

<section class="section" id="servicios">
  <div class="section-inner">
    <div class="section-tag">Servicios</div>
    <h2 class="section-title">¿Qué ofrecemos?</h2>
    <p class="section-text">En {negocio} nos dedicamos a ofrecer soluciones de calidad adaptadas a las necesidades de cada cliente.</p>
    <div class="services-grid">
      <div class="service-card"><div class="service-icon">⭐</div><div class="service-title">Calidad</div><div class="service-desc">Servicio profesional con los más altos estándares de calidad.</div></div>
      <div class="service-card"><div class="service-icon">🤝</div><div class="service-title">Confianza</div><div class="service-desc">Más de 10 años de experiencia avalan nuestro trabajo.</div></div>
      <div class="service-card"><div class="service-icon">📍</div><div class="service-title">Cercanía</div><div class="service-desc">Atención personalizada y cercana a nuestros clientes.</div></div>
    </div>
  </div>
</section>

<section class="section" id="contacto">
  <div class="section-inner">
    <div class="section-tag">Contacto</div>
    <h2 class="section-title">Háblanos</h2>
    <p class="section-text">Estaremos encantados de atenderte. Puedes llamarnos, escribirnos o visitarnos.</p>
    <div class="contact-box">
      {f'<p>📍 {direccion}</p>' if direccion else ''}
      {f'<p>📞 <a href="tel:{telefono}">{telefono}</a></p>' if telefono else ''}
      <p>✉️ <a href="mailto:info@{slug}.com">info@{slug}.com</a></p>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="footer-brand">{negocio}</div>
  <div class="footer-sub">© {datetime.now().year} · Diseñado por NEO Labs</div>
</footer>
</body>
</html>"""
    return html

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NEO Web Generator")
    parser.add_argument("--negocio", "-n", required=True, help="Nombre del negocio")
    parser.add_argument("--sector", "-s", default="tecnologia", choices=list(PALETTES.keys()), help="Sector")
    parser.add_argument("--plan", "-p", default="basica", choices=["basica","premium","full"], help="Plan")
    parser.add_argument("--telefono", "-t", default="", help="Teléfono")
    parser.add_argument("--direccion", "-d", default="", help="Dirección")
    parser.add_argument("--output", "-o", help="Ruta de salida (opcional)")
    args = parser.parse_args()
    
    html = generate_web(args.negocio, args.sector, args.plan, args.telefono, args.direccion)
    
    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
    else:
        slug = re.sub(r'[^a-z0-9]+', '-', args.negocio.lower()).strip('-')
        os.makedirs(OUT_DIR, exist_ok=True)
        args.output = os.path.join(OUT_DIR, f"{slug}.html")
    
    with open(args.output, "w") as f:
        f.write(html)
    
    pal = PALETTES[args.sector]
    print(f"✅ Web generada: {args.output}")
    print(f"   Negocio: {args.negocio}")
    print(f"   Sector: {args.sector} ({pal['name']})")
    print(f"   Colores: primario {pal['primary']}, acento {pal['accent']}")
    print(f"   Plan: {args.plan}")

if __name__ == "__main__":
    main()
