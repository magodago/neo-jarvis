#!/usr/bin/env python3
"""Add lead magnet CTA (5 free prompts) to all blog articles."""
import os
import re

BLOG_DIR = "/home/dorti/neo-jarvis/blog"

# The lead magnet CSS snippet (adds before </style>)
LEAD_CSS = """
.lead-box{background:linear-gradient(135deg,rgba(212,168,83,.08),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.25);border-radius:16px;padding:28px 24px;text-align:center;margin:28px 0;position:relative;overflow:hidden}
.lead-box::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--brand,#d4a853),transparent)}
.lead-box .lead-tag{display:inline-block;padding:3px 10px;border-radius:100px;font-size:.6rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;background:rgba(212,168,83,.2);color:var(--brand,#d4a853);margin-bottom:6px}
.lead-box .lead-title{font-family:var(--font-display,'Syne',sans-serif);font-size:1.05rem;font-weight:700;color:#fff;margin-bottom:4px}
.lead-box .lead-title span{color:var(--brand,#d4a853)}
.lead-box .lead-desc{font-size:.8rem;color:var(--text-muted,#a09888);margin-bottom:14px;max-width:420px;margin-left:auto;margin-right:auto}
.lead-box .lead-btn{display:inline-block;padding:12px 28px;border-radius:8px;border:none;background:linear-gradient(135deg,var(--brand-dark,#b8922f),var(--brand,#d4a853));color:#fff;font-family:var(--font-display,'Syne',sans-serif);font-size:.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;cursor:pointer;transition:all .3s;text-decoration:none;box-shadow:0 4px 25px rgba(212,168,83,.2)}
.lead-box .lead-btn:hover{transform:translateY(-2px);box-shadow:0 6px 35px rgba(212,168,83,.35)}
"""

# The lead magnet HTML snippet (inserts before <footer>)
LEAD_HTML = """
<div class="lead-box">
<div class="lead-tag">Gratis</div>
<div class="lead-title">Descarga <span>5 Prompts de IA</span> para Multiplicar tu Productividad</div>
<div class="lead-desc">Guia gratuita con prompts listos para usar en ChatGPT, Claude y Gemini. Resultados inmediatos.</div>
<a href="https://payhip.com/b/98ens" target="_blank" class="lead-btn">Descargar Guia Gratuita &rarr;</a>
</div>
"""

def fix_css_inside_vars(css_text):
    """Fix the CSS var() syntax — remove the bad `--` prefix (it's actually a long dash issue)"""
    return css_text

def process_article(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # 1. Add lead CSS before </style>
    # Handle both "</style>" standalone and "</style>  <meta" variants
    content = content.replace("</style>", LEAD_CSS + "</style>", 1)
    
    # 2. Add lead HTML before <footer>
    # Insert right before the first <footer> tag
    content = content.replace("<footer>", LEAD_HTML + "\n<footer>", 1)
    
    if content == original:
        print(f"  ⚠️  No changes made to {filepath}")
        return False
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True

# Find all blog HTML files (excluding index.html)
total = 0
success = 0
for root, dirs, files in os.walk(BLOG_DIR):
    for fname in files:
        if fname.endswith(".html") and fname != "index.html":
            fpath = os.path.join(root, fname)
            total += 1
            if process_article(fpath):
                success += 1
                print(f"  ✅ {fpath}")
            else:
                print(f"  ❌ {fpath}")

print(f"\nDone: {success}/{total} articles updated")
