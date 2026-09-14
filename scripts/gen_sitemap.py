#!/usr/bin/env python3
"""Regenerate sitemap.xml for NEO-jarvis.

Reglas (aprendidas a golpes):
- El dominio real es https://neo.neolabs.me. NUNCA magodago.github.io:
  si el sitemap apunta a github.io, el dominio custom pierde la indexación.
- Solo ficheros versionados en git: los ficheros locales sin publicar daban 404
  en el sitemap (67 URLs muertas sobre 291).
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
if len(sys.argv) > 1:
    REPO = Path(sys.argv[1])
BASE = "https://neo.neolabs.me"
TODAY = datetime.now().strftime("%Y-%m-%d")

tracked = subprocess.run(["git", "ls-files", "*.html"], cwd=str(REPO),
                         capture_output=True, text=True).stdout.split()
if not tracked:
    raise SystemExit(f"Sin ficheros versionados en {REPO} — abortando para no vaciar el sitemap")


def priority(rel):
    if rel in ("index.html", "catalogo.html", "neo-labs.html"):
        return "1.0"
    if rel.startswith("landing/"):
        return "0.9"
    if rel.endswith("index.html"):
        return "0.8"
    return "0.7"


def freq(rel):
    return "weekly" if rel.endswith("index.html") or rel in ("catalogo.html", "neo-labs.html") else "monthly"


xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
seen = []
for rel in sorted(tracked):
    if rel in seen:
        continue
    seen.append(rel)
    xml += (f'  <url>\n    <loc>{BASE}/{rel}</loc>\n'
            f'    <lastmod>{TODAY}</lastmod>\n'
            f'    <changefreq>{freq(rel)}</changefreq>\n'
            f'    <priority>{priority(rel)}</priority>\n  </url>\n')
xml += '</urlset>\n'

(REPO / "sitemap.xml").write_text(xml, encoding="utf-8")
print(f"Sitemap: {len(seen)} URLs en {BASE}")
