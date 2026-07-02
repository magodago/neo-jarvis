#!/usr/bin/env python3
"""Regenerate sitemap.xml for NEO-jarvis."""
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
BASE = "https://magodago.github.io/neo-jarvis"
TODAY = datetime.now().strftime("%Y-%m-%d")

urls = []

# Main pages
urls.append(("index.html", "weekly", 1.0))
urls.append(("neo-labs.html", "weekly", 0.9))
urls.append(("catalogo.html", "weekly", 0.9))

# Blog hub
urls.append(("blog/index.html", "weekly", 0.8))

# Niche indexes
for niche in ["productividad", "finanzas", "marketing", "programacion", "estudiantes", "rrhh"]:
    urls.append((f"blog/{niche}/index.html", "weekly", 0.7))

# Niche articles
for niche in ["productividad", "finanzas", "marketing", "programacion", "estudiantes", "rrhh"]:
    for p in sorted((REPO / "blog" / niche).glob("*.html")):
        if p.stem != "index":
            urls.append((f"blog/{niche}/{p.name}", "monthly", 0.7))

# Standalone product pages
for p in sorted((REPO / "blog").glob("prompts-*.html")):
    urls.append((f"blog/{p.name}", "monthly", 0.7))

# Podcast pages (we could link to them, but they're audio files linked from articles)
# Just ensure they're discoverable via the sitemap

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

seen = set()
for path, freq, priority in urls:
    if path in seen:
        continue
    seen.add(path)
    xml += f'  <url>\n    <loc>{BASE}/{path}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>\n'

xml += '</urlset>\n'

(REPO / "sitemap.xml").write_text(xml)
print(f"Sitemap: {len(seen)} URLs written")
