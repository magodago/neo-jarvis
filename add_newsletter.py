#!/usr/bin/env python3
"""
NEO Newsletter — añade formulario de suscripción premium a todos los artículos.
Usa FormSubmit.co (gratis, sin servidor, 100 subs/día).
Los emails llegan a formulasia76@gmail.com
"""
import re
from pathlib import Path

REPO = Path.home() / "neo-jarvis"

# Premium newsletter form (gold/black NEO style)
NEWSLETTER_HTML = '''
<div class="newsletter-box">
 <div class="nl-icon">✧</div>
 <div class="nl-title">Recibe los mejores prompts de IA gratis</div>
 <div class="nl-desc">Cada semana, 3 prompts exclusivos + tendencias de IA directo a tu bandeja de entrada. Sin spam, solo valor.</div>
 <form class="nl-form" action="https://formsubmit.co/formulasia76@gmail.com" method="POST">
  <input type="hidden" name="_subject" value="Nuevo suscriptor NEO Labs">
  <input type="hidden" name="_next" value="https://magodago.github.io/neo-jarvis/neo-labs.html">
  <input type="hidden" name="_captcha" value="false">
  <input type="text" name="_honey" style="display:none">
  <input type="email" name="email" placeholder="tu@email.com" required class="nl-input">
  <button type="submit" class="nl-btn">Suscribirme</button>
 </form>
</div>'''

NEWSLETTER_CSS = '''
.newsletter-box{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.2);border-radius:16px;padding:28px 24px;text-align:center;margin:32px 0}.nl-icon{font-size:1.8rem;color:var(--brand,'#d4a853');margin-bottom:4px}.nl-title{font-family:var(--font-display,'Syne',sans-serif);font-size:.95rem;font-weight:700;color:#fff;margin-bottom:4px}.nl-desc{font-size:.8rem;color:var(--text-muted,'#a09888');margin-bottom:16px;max-width:400px;margin-left:auto;margin-right:auto}.nl-form{display:flex;gap:8px;max-width:380px;margin:0 auto;flex-wrap:wrap}.nl-input{flex:1;min-width:180px;padding:10px 16px;border-radius:8px;border:1px solid rgba(212,168,83,.2);background:rgba(5,5,8,.6);color:#fff;font-family:var(--font-body,'Sora',sans-serif);font-size:.82rem;outline:none;transition:border-color .3s}.nl-input:focus{border-color:var(--brand,'#d4a853')}.nl-input::placeholder{color:#6a6558}.nl-btn{padding:10px 20px;border-radius:8px;border:none;background:var(--brand,'#d4a853');color:#050508;font-family:var(--font-display,'Syne',sans-serif);font-size:.75rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .3s}.nl-btn:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(212,168,83,.25)}
'''

def add_newsletter_to_article(path: Path) -> bool:
    """Add newsletter signup form to one article."""
    html = path.read_text(encoding="utf-8")
    original = html
    
    # Skip index pages  
    if path.stem == "index":
        return False
    
    # Add CSS
    if "newsletter-box" not in html:
        html = html.replace("</style>", NEWSLETTER_CSS + "</style>")
    
    # Add form before footer
    if "newsletter-box" not in html.replace(NEWSLETTER_CSS, ""):
        html = html.replace("</div>\n<footer", f"{NEWSLETTER_HTML}</div>\n<footer")
        if NEWSLETTER_HTML not in html:
            # Try alternative pattern (no newline)
            html = html.replace("</div>\n\n<footer", f"{NEWSLETTER_HTML}</div>\n\n<footer")
    
    if html != original:
        path.write_text(encoding="utf-8", data=html)
        return True
    return False

def main():
    articles = []
    blog_dir = REPO / "blog"
    
    for niche_dir in sorted(blog_dir.iterdir()):
        if not niche_dir.is_dir():
            continue
        for p in sorted(niche_dir.glob("*.html")):
            if p.stem != "index":
                articles.append(p)
    
    for p in sorted((blog_dir).glob("prompts-*.html")):
        articles.append(p)
    
    modified = 0
    for p in articles:
        try:
            if add_newsletter_to_article(p):
                modified += 1
                print(f"  ✅ {p.parent.name}/{p.stem}")
        except Exception as e:
            print(f"  ❌ {p.stem}: {e}")
    
    print(f"\n📊 {modified}/{len(articles)} artículos con newsletter")

if __name__ == "__main__":
    main()
