#!/usr/bin/env python3
"""
NEO Article Enhancer v2 — Adds podcast player + TOC + FAQ schema + related articles to all blog articles.
Handles both template types (CTA inside body / CTA after body).
"""
import re, json
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
AUDIO_BASE = "https://magodago.github.io/neo-jarvis/podcasts"

# All styling in one block (compact for single </style> insert)
ENHANCE_CSS = """
.podcast-player{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,rgba(212,168,83,.08),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.15);border-radius:14px;padding:14px 18px;margin:24px 0;cursor:pointer;transition:all .3s}.podcast-player:hover{border-color:rgba(212,168,83,.35);background:linear-gradient(135deg,rgba(212,168,83,.12),rgba(5,5,8,.95))}.podcast-icon{font-size:1.6rem;flex-shrink:0}.podcast-info{flex:1}.podcast-label{font-family:var(--font-display,'Syne',sans-serif);font-size:.65rem;letter-spacing:2px;font-weight:700;color:var(--brand,'#d4a853');margin-bottom:2px}.podcast-desc{font-size:.78rem;color:var(--text-muted)}.toc{background:var(--bg3,#11111a);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 20px;margin:24px 0;font-size:.85rem}.toc-title{font-family:var(--font-display,'Syne',sans-serif);font-size:.7rem;letter-spacing:2px;font-weight:700;color:var(--brand,'#d4a853');margin-bottom:8px;text-transform:uppercase}.toc a{display:block;padding:3px 0;color:var(--text-muted);transition:color .2s;font-size:.82rem}.toc a:hover{color:var(--brand)}.toc a:before{content:"▸ ";font-size:.65rem}.faq-section{margin:28px 0}.faq-q{background:var(--bg3,#11111a);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px 18px;margin-bottom:6px}.faq-q summary{font-weight:600;font-size:.88rem;color:#fff;cursor:pointer;display:flex;align-items:center;gap:10px}.faq-q summary::marker{color:var(--brand,'#d4a853')}.faq-q p{font-size:.82rem;color:var(--text-muted);margin-top:8px;line-height:1.6}.related-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:24px 0}.related-card{background:var(--bg3,#11111a);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px;transition:all .3s;text-decoration:none!important}.related-card:hover{border-color:rgba(212,168,83,.25);transform:translateY(-2px)}.related-card .rc-tag{font-size:.6rem;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;color:var(--brand,'#d4a853')}.related-card .rc-title{font-size:.82rem;color:#fff;margin-top:4px;font-weight:500}.related-card .rc-desc{font-size:.72rem;color:var(--text-muted);margin-top:2px}
"""

PODCAST_HTML_TEMPLATE = """<div class="podcast-player" onclick="this.querySelector('audio').play()">
 <div class="podcast-icon">🎙️</div>
 <div class="podcast-info">
  <div class="podcast-label">🎧 ESCUCHAR PODCAST</div>
  <div class="podcast-desc">Versión audio de este artículo — ~3 min</div>
 </div>
 <audio preload="none" style="display:none" controls>
  <source src="{audio_url}" type="audio/mpeg">
 </audio>
</div>"""

def get_article_index(blog_dir: Path) -> dict:
    """Build index of all articles by niche."""
    index = {}
    for niche_dir in sorted(blog_dir.iterdir()):
        if not niche_dir.is_dir():
            continue
        niche = niche_dir.name
        arts = []
        for p in sorted(niche_dir.glob("*.html")):
            if p.stem == "index":
                continue
            html = p.read_text(encoding="utf-8")
            m = re.search(r"<h1>(.*?)</h1>", html)
            title = m.group(1)[:60] if m else p.stem
            index[p.stem] = {"niche": niche, "title": title, "path": p}
    return index

def enhance_article(path: Path, index: dict) -> bool:
    """Add podcast player + TOC + FAQ schema + related articles to one article."""
    html = path.read_text(encoding="utf-8")
    original = html
    slug = path.stem
    
    # Skip index pages
    if slug == "index":
        return False
    
    niche = path.parent.name if path.parent.name != "blog" else "blog"
    
    # 1. Add CSS if not present
    if "podcast-player" not in html:
        html = html.replace("</style>", ENHANCE_CSS + "</style>")
    
    # 2. Add podcast player (before article-body opening tag)
    audio_url = f"{AUDIO_BASE}/{niche}/{slug}.mp3"
    podcast_html = PODCAST_HTML_TEMPLATE.format(audio_url=audio_url)
    if "podcast-player" not in html.replace(ENHANCE_CSS, ""):  # not yet added
        html = html.replace('<div class="article-body">', podcast_html + '\n<div class="article-body">')
    
    # 3. Add Table of Contents (after first paragraph in article-body, if h2s exist)
    if '<div class="toc"' not in html:
        # Find h2 headings
        h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html)
        if h2s:
            # Generate anchors from headings
            toc_links = []
            for h2_text in h2s:
                anchor = re.sub(r'[^a-zA-Z0-9\u00C0-\u024F\s]', '', h2_text)
                anchor = re.sub(r'\s+', '-', anchor.strip().lower())[:40]
                toc_links.append(f'<a href="#{anchor}">{h2_text}</a>')
            
            if toc_links:
                sep = '\n'
                toc_html = f'<div class="toc"><div class="toc-title">📋 Contenido</div>{sep.join(toc_links)}</div>'
                # Add anchor IDs to h2 tags
                for h2_text in h2s:
                    anchor = re.sub(r'[^a-zA-Z0-9\u00C0-\u024F\s]', '', h2_text)
                    anchor = re.sub(r'\s+', '-', anchor.strip().lower())[:40]
                    html = html.replace(
                        f'<h2>{h2_text}</h2>',
                        f'<h2 id="{anchor}">{h2_text}</h2>',
                        1
                    )
                
                # Insert TOC after first paragraph or podcast player
                html = html.replace('<div class="article-body">', '<div class="article-body">' + toc_html, 1)
    
    # 4. JSON-LD FAQ schema (generic, not AI-generated)
    if 'application/ld+json' not in html:
        # Try to find h2s for basic FAQ schema
        h2_texts = re.findall(r'<h2[^>]*>(.*?)</h2>', html)[:3]
        if h2_texts:
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": h2,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Lee nuestro artículo completo sobre {h2.lower()} para obtener una respuesta detallada y prompts prácticos."
                        }
                    } for h2 in h2_texts
                ]
            }
            schema_html = f'<script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False)}</script>\n'
            html = html.replace('</head>', schema_html + '</head>')
    
    # 5. Related articles (before footer or CTA)
    if 'related-row' not in html:
        category_arts = [v for v in index.values() if v["niche"] == niche and v["path"].stem != slug][:3]
        if category_arts:
            cards = "".join(
                f'<a href="{a["path"].name}" class="related-card">'
                f'<div class="rc-tag">{a["niche"].capitalize()}</div>'
                f'<div class="rc-title">{a["title"][:50]}</div></a>'
                for a in category_arts
            )
            related_html = f'<div class="related-row">{cards}</div>'
            html = html.replace('</div>\n<footer', f'{related_html}</div>\n<footer')
            if related_html not in html:  # Try alternative pattern
                html = html.replace('<footer', f'{related_html}</div>\n<footer', 1)
    
    if html != original:
        path.write_text(encoding="utf-8", data=html)
        return True
    return False

def main():
    blog_dir = REPO / "blog"
    index = get_article_index(blog_dir)
    
    # Collect all article files
    articles = []
    for niche_dir in sorted(blog_dir.iterdir()):
        if not niche_dir.is_dir():
            continue
        for p in sorted(niche_dir.glob("*.html")):
            if p.stem != "index":
                articles.append(p)
    for p in (blog_dir).glob("prompts-*.html"):
        articles.append(p)
    
    print(f"📝 Mejorando {len(articles)} artículos...")
    modified = 0
    for p in articles:
        try:
            if enhance_article(p, index):
                modified += 1
                print(f"  ✅ {p.parent.name}/{p.stem}")
        except Exception as e:
            print(f"  ❌ {p.stem}: {e}")
    
    print(f"\n📊 {modified}/{len(articles)} artículos mejorados")

if __name__ == "__main__":
    main()
