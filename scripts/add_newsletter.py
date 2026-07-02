#!/usr/bin/env python3
"""Añade formulario de email a todos los artículos del blog."""
import re
from pathlib import Path

BLOG = Path.home() / "neo-jarvis" / "blog"

NL_CSS = ".nl-box{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.2);border-radius:16px;padding:28px 24px;text-align:center;margin:32px 0}.nl-box .nl-icon{font-size:1.8rem;color:var(--brand);margin-bottom:4px}.nl-box .nl-title{font-family:var(--font-display);font-size:.95rem;font-weight:700;color:#fff;margin-bottom:4px}.nl-box .nl-desc{font-size:.8rem;color:var(--text-muted);margin-bottom:16px;max-width:400px;margin-left:auto;margin-right:auto}.nl-form{display:flex;gap:8px;max-width:380px;margin:0 auto;flex-wrap:wrap}.nl-input{flex:1;min-width:180px;padding:10px 16px;border-radius:8px;border:1px solid rgba(212,168,83,.2);background:rgba(5,5,8,.6);color:#fff;font-size:.82rem;outline:none;transition:border-color .3s;font-family:var(--font-body)}.nl-input:focus{border-color:var(--brand)}.nl-input::placeholder{color:#6a6558}.nl-btn{padding:10px 20px;border-radius:8px;border:none;background:var(--brand);color:var(--bg);font-family:var(--font-display);font-size:.75rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .3s}.nl-btn:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(212,168,83,.25)}"

NL_HTML = """<div class="nl-box"><div class="nl-icon">&#10026;</div><div class="nl-title">Recibe contenido como este cada semana</div><div class="nl-desc">Prompts exclusivos, tutoriales y tendencias de IA directo a tu correo. Sin spam, solo valor.</div><form class="nl-form" action="https://formsubmit.co/formulasia76@gmail.com" method="POST" onsubmit="fetch('https://909f85f8c7219d8f-95-63-166-157.serveousercontent.com/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:this.email.value})}).catch(()=>{});"><input type="hidden" name="_subject" value="Nuevo suscriptor NEO Labs"><input type="hidden" name="_next" value="https://magodago.github.io/neo-jarvis/neo-labs.html"><input type="hidden" name="_captcha" value="false"><input type="text" name="_honey" style="display:none"><input type="email" name="email" placeholder="tu@email.com" required class="nl-input"><button type="submit" class="nl-btn">Suscribirme</button></form></div>"""

def add_newsletter(filepath: Path) -> bool:
    content = filepath.read_text(encoding="utf-8")
    
    # Skip if already has newsletter
    if 'nl-box' in content or 'newsletter-box' in content:
        return False
    
    # 1. Add CSS before </style>
    if 'nl-box' not in content:
        content = content.replace('</style>', f'{NL_CSS}</style>', 1)
    
    # 2. Add HTML before closing </div> of article-body
    # Pattern: find </div> (closing article-body) followed by related-section or other elements
    # The structure is: <div class="article-body">...body...</div> <div class="related-section">
    pattern = r'(</div>\s*\n\s*<div class="related-section")'
    replacement = f'{NL_HTML}\\1'
    
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content == content:
        return False
    
    filepath.write_text(new_content, encoding="utf-8")
    return True

# Process all article HTML files
total = 0
for nd in sorted(BLOG.iterdir()):
    if not nd.is_dir() or nd.name.startswith("."):
        continue
    for f in sorted(nd.glob("*.html")):
        if f.name == "index.html":
            continue
        if add_newsletter(f):
            total += 1
            print(f"✅ {nd.name}/{f.name}")
        else:
            pass  # already has it

print(f"\nTotal actualizados con newsletter: {total}")
