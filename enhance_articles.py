#!/usr/bin/env python3
"""
NEO Article Enhancer — Adds podcast player + FAQ schema + related articles + TOC to all blogs.
"""
import re, json, subprocess
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
AUDIO_BASE = "https://magodago.github.io/neo-jarvis/podcasts"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# HTML snippet: podcast player
PODCAST_HTML = """
<div class="podcast-player" onclick="this.querySelector('audio').play()">
 <div class="podcast-icon">🎙️</div>
 <div class="podcast-info">
  <div class="podcast-label">ESCUCHAR PODCAST</div>
  <div class="podcast-desc">Versión audio de este artículo — 3 min</div>
 </div>
 <audio preload="none" style="display:none" controls>
  <source src="{audio_url}" type="audio/mpeg">
 </audio>
</div>"""

# Player CSS
PLAYER_CSS = """
.podcast-player{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,rgba(212,168,83,.08),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.15);border-radius:14px;padding:14px 18px;margin:24px 0;cursor:pointer;transition:all .3s}.podcast-player:hover{border-color:rgba(212,168,83,.35);background:linear-gradient(135deg,rgba(212,168,83,.12),rgba(5,5,8,.95))}.podcast-icon{font-size:1.6rem;flex-shrink:0}.podcast-info{flex:1}.podcast-label{font-family:var(--font-display,'Syne',sans-serif);font-size:.65rem;letter-spacing:2px;font-weight:700;color:var(--brand,'#d4a853');margin-bottom:2px}.podcast-desc{font-size:.78rem;color:var(--text-muted,'#a09888')}
"""

TOC_CSS = """
.toc{background:var(--bg3,#11111a);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 20px;margin:24px 0;font-size:.85rem}.toc-title{font-family:var(--font-display,'Syne',sans-serif);font-size:.7rem;letter-spacing:2px;font-weight:700;color:var(--brand,'#d4a853');margin-bottom:8px;text-transform:uppercase}.toc a{display:block;padding:3px 0;color:var(--text-muted,'#a09888');transition:color .2s;font-size:.82rem}.toc a:hover{color:var(--brand,'#d4a853')}.toc a:before{content:"▸ ";font-size:.65rem}
"""

FAQ_CSS = """
.faq-section{margin:28px 0}.faq-q{background:var(--bg3,#11111a);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px 18px;margin-bottom:6px}.faq-q summary{font-weight:600;font-size:.88rem;color:#fff;cursor:pointer;display:flex;align-items:center;gap:10px}.faq-q summary::marker{color:var(--brand,'#d4a853')}.faq-q p{font-size:.82rem;color:var(--text-muted,'#a09888');margin-top:8px;line-height:1.6}
"""

RELATED_CSS = """
.related-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:24px 0}.related-card{background:var(--bg3,#11111a);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:14px;transition:all .3s;text-decoration:none!important}.related-card:hover{border-color:rgba(212,168,83,.25);transform:translateY(-2px)}.related-card .rc-tag{font-size:.6rem;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;color:var(--brand,'#d4a853')}.related-card .rc-title{font-size:.82rem;color:#fff;margin-top:4px;font-weight:500}.related-card .rc-desc{font-size:.72rem;color:var(--text-muted,'#a09888');margin-top:2px}
"""

def get_niche_articles(blog_dir: Path) -> dict:
    """Get all articles organized by niche."""
    articles = {}
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
            m2 = re.search(r'<meta name="description" content="([^"]+)"', html)
            desc = m2.group(1)[:100] if m2 else ""
            arts.append({"slug": p.stem, "title": title, "desc": desc, "path": p})
        articles[niche] = arts
    return articles

def add_to_article(path: Path, all_articles: dict):
    """Add podcast player, TOC, FAQ schema, related articles to an article."""
    html = path.read_text(encoding="utf-8")
    original = html
    
    niche = path.parent.name
    slug = path.stem
    
    # 1. Podcast player (before article-body)
    audio_url = f"{AUDIO_BASE}/{niche}/{slug}.mp3"
    if '<div class="podcast-player"' not in html:
        podcast_block = PODCAST_HTML.format(audio_url=audio_url)
        html = html.replace('<div class="article-body">', f'{podcast_block}<div class="article-body">')
    
    # 2. Table of Contents (inside article-body, after first paragraph)
    if '<div class="toc"' not in html:
        # Extract h2s for TOC
        h2s = re.findall(r'<h2[^>]*id="?([^"\s>]+)"?[^>]*>(.*?)</h2>', html)
        if not h2s:
            # Generate from text
            h2_texts = re.findall(r'<h2>(.*?)</h2>', html)
            h2s = [(re.sub(r'[^a-zA-Z0-9\u00C0-\u024F]+', '-', t).strip('-').lower()[:40], t) for t in h2_texts]
        
        if h2s:
            toc_items = "\n".join(f'<a href="#{h2[0]}">{h2[1]}</a>' for h2 in h2s)
            toc = f'<div class="toc"><div class="toc-title">Contenido</div>{toc_items}</div>'
            # Insert after first paragraph in article-body
            html = html.replace('<div class="article-body">', '<div class="article-body">' + toc, 1)
    
    # 3. FAQ Schema (JSON-LD) + visual FAQ
    if 'application/ld+json' not in html and 'faq-section' not in html:
        # Ask Gemma 4 to generate 3 FAQs
        try:
            article_text_match = re.search(r'<div class="article-body">(.*?)</div>\s*<footer', html, re.DOTALL)
            article_text = ""
            if article_text_match:
                article_text = re.sub(r'<[^>]+>', ' ', article_text_match.group(1))
                article_text = re.sub(r'\s+', ' ', article_text).strip()[:2000]
            
            if article_text and len(article_text) > 200:
                prompt = f"""Genera 3 preguntas frecuentes (FAQ) sobre este tema en español. 
Tema: {slug}

Formato JSON exacto (sin markdown):
{{"faqs": [{{"q": "pregunta 1?", "a": "respuesta clara y util de 2-3 frases"}}, ...]}}

Contexto: {article_text[:1500]}"""
                
                r = subprocess.run(["curl", "-s", OLLAMA_URL, "-d", json.dumps({
                    "model": "gemma4", "prompt": prompt, "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 800}
                })], capture_output=True, text=True, timeout=60)
                
                faq_data = json.loads(r.stdout)
                faq_raw = faq_data.get("response", "")
                
                # Try to extract JSON
                m = re.search(r'\{.*"faqs".*\}', faq_raw, re.DOTALL)
                if m:
                    faq_json = json.loads(m.group(0))
                    # Schema
                    schema = {
                        "@context": "https://schema.org",
                        "@type": "FAQPage",
                        "mainEntity": [{"@type": "Question", "name": f["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                            for f in faq_json["faqs"]]
                    }
                    schema_html = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>\n'
                    # Visual FAQ
                    faq_visual = '<div class="faq-section"><h2>Preguntas frecuentes</h2>'
                    for f in faq_json["faqs"]:
                        faq_visual += f'<details class="faq-q"><summary>{f["q"]}</summary><p>{f["a"]}</p></details>'
                    faq_visual += '</div>'
                    
                    html = html.replace('</head>', f'{schema_html}</head>')
                    html = html.replace('</div>\n<footer', f'{faq_visual}</div>\n<footer')
        except Exception as e:
            print(f"⚠️  FAQ error {slug}: {e}")
    
    # 4. Related articles
    if 'related-row' not in html:
        category_arts = all_articles.get(niche, [])
        related = [a for a in category_arts if a["slug"] != slug][:3]
        if related:
            cards = "".join(
                f'<a href="{a["slug"]}.html" class="related-card">'
                f'<div class="rc-tag">{niche.capitalize()}</div>'
                f'<div class="rc-title">{a["title"]}</div>'
                f'<div class="rc-desc">{a["desc"][:80]}</div></a>'
                for a in related
            )
            related_html = f'<div class="related-row">{cards}</div>'
            html = html.replace('</div>\n<footer', f'{related_html}</div>\n<footer')
    
    # 5. Add CSS if not present
    css_to_add = PLAYER_CSS + TOC_CSS + FAQ_CSS + RELATED_CSS
    if 'podcast-player' not in html:
        html = html.replace('</style>', f'{css_to_add}</style>')
    elif 'toc' not in html or 'faq-section' not in html or 'related-row' not in html:
        # Add any missing CSS
        missing = ""
        if 'toc' not in html and 'toc' not in css_to_add.split('}')[0]:
            missing += TOC_CSS
        if 'faq-section' not in html:
            missing += FAQ_CSS
        if 'related-row' not in html:
            missing += RELATED_CSS
        if missing:
            html = html.replace('</style>', f'{missing}</style>')
    
    if html != original:
        path.write_text(encoding="utf-8", data=html)
        return True
    return False

def main():
    blog_dir = REPO / "blog"
    all_articles = get_niche_articles(blog_dir)
    
    # Find all article HTML files
    articles = []
    for niche_dir in sorted(blog_dir.iterdir()):
        if not niche_dir.is_dir():
            continue
        for p in sorted(niche_dir.glob("*.html")):
            if p.stem != "index":
                articles.append(p)
    
    # Also standalone articles in /blog/
    for p in (blog_dir).glob("prompts-*.html"):
        articles.append(p)
    
    print(f"📝 Mejorando {len(articles)} artículos...")
    modified = 0
    for p in articles:
        if add_to_article(p, all_articles):
            modified += 1
            print(f"✅ {p.stem}")
    
    print(f"\n📊 {modified}/{len(articles)} artículos mejorados")

if __name__ == "__main__":
    main()
