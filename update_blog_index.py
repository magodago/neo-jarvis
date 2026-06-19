#!/usr/bin/env python3
"""Generate static 'Recent Articles' section for blog/index.html.
Run after daily-article.py to keep the blog index updated with links."""
import re, os
from pathlib import Path

BLOG = Path.home() / "neo-jarvis" / "blog"
INDEX = BLOG / "index.html"

# Niche colors matching existing CSS
NICHE_COLORS = {
    "productividad": ("productividad", "#d4a853"),
    "finanzas": ("finanzas", "#66bb6a"),
    "marketing": ("marketing", "#42a5f5"),
    "programacion": ("programacion", "#ab47bc"),
    "estudiantes": ("educacion", "#ffa726"),
    "rrhh": ("rrhh", "#ec407a"),
}

# Find latest articles
articles = []
for niche_dir in sorted(BLOG.iterdir()):
    if not niche_dir.is_dir() or niche_dir.name.startswith("."):
        continue
    for f in sorted(niche_dir.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.name == "index.html":
            continue
        # Read title
        content = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'<title>([^<]+)', content)
        title = m.group(1).replace(" — NEO Labs", "").strip() if m else f.stem.replace("-", " ").title()
        niche = niche_dir.name
        css_class, color = NICHE_COLORS.get(niche, ("productividad", "#d4a853"))
        
        # Get description
        desc_m = re.search(r'<meta name="description" content="([^"]+)"', content)
        desc = desc_m.group(1)[:120] if desc_m else ""
        
        # Get date from file mtime
        import datetime
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
        date_str = mtime.strftime("%d %B %Y")
        
        articles.append({
            "path": f"{niche}/{f.name}",
            "title": title,
            "desc": desc,
            "niche": niche,
            "css_class": css_class,
            "color": color,
            "date": date_str,
        })

# Build HTML section (take 12 most recent)
RECENT_COUNT = 12
recent = articles[:RECENT_COUNT]

cards_html = []
for a in recent:
    card = f'''    <a href="{a['path']}" class="article-card reveal" data-category="{a['niche']}">
      <span class="cat-tag cat-{a['css_class']}">{a['niche'].title()}</span>
      <h3>{a['title'][:70]}</h3>
      <p>{a['desc'][:100]}</p>
      <div class="meta"><span>{a['date']}</span></div>
      <span class="read-more">Leer &rarr;</span>
    </a>'''
    cards_html.append(card)

section_html = f'''  <!-- === RECENT ARTICLES (static, for SEO) === -->
  <div class="section-head" style="margin-top:48px">
    <div class="label">Articulos Recientes</div>
    <h2>Lo ultimo en <span style="color:var(--gold)">IA y productividad</span></h2>
  </div>
  <div class="article-grid">
{chr(10).join(cards_html)}
  </div>

'''
print(f"Generated {len(recent)} recent article cards")

# Read current index
index_content = INDEX.read_text(encoding="utf-8")

# Check if the RECENT ARTICLES section already exists and replace it
start_marker = "<!-- === RECENT ARTICLES (static, for SEO) === -->"
end_marker = "<!-- GoatCounter analytics -->"

if start_marker in index_content:
    # Replace existing section
    start_idx = index_content.find(start_marker)
    end_idx = index_content.find(end_marker)
    if end_idx == -1:
        end_idx = index_content.rfind("</body>")
    new_content = index_content[:start_idx] + section_html + index_content[end_idx:]
    INDEX.write_text(new_content, encoding="utf-8")
    print(f"Replaced existing recent articles section in {INDEX}")
else:
    # Insert fresh
    insert_pos = index_content.rfind(end_marker)
    if insert_pos == -1:
        insert_pos = index_content.rfind("</body>")
    if insert_pos > 0:
        new_content = index_content[:insert_pos] + section_html + index_content[insert_pos:]
        INDEX.write_text(new_content, encoding="utf-8")
        print(f"Inserted fresh recent articles section in {INDEX}")
    else:
        print("ERROR: Could not find insertion point")
