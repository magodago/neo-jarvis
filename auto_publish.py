#!/usr/bin/env python3
"""Auto-publish master: generates Medium file + posts to LinkedIn."""
import os, sys, subprocess, re
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
DESKTOP = Path("/mnt/c/Users/dorti/Desktop")
ENV = Path.home() / ".hermes" / ".env"

def load_env():
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip("'\"")

def get_article_content():
    """Get latest article as Medium-ready markdown."""
    articles = []
    blog = REPO / "blog"
    for nd in blog.iterdir():
        if not nd.is_dir() or nd.name.startswith("."):
            continue
        for f in nd.glob("*.html"):
            if f.name == "index.html":
                continue
            articles.append((f.stat().st_mtime, f))
    if not articles:
        return None, None
    articles.sort(reverse=True)
    _, p = articles[0]
    c = p.read_text(encoding="utf-8")
    
    title = (re.search(r'<h1>([^<]+)', c) or [None, "NEO Labs Article"]).group(1)
    body = (re.search(r'<div class="article-body">(.*?)</div>', c, re.DOTALL) or [None, ""]).group(1) or ""
    
    # Convert HTML to markdown
    body = re.sub(r'<div class="prompt-box">.*?<div class="prompt-label">Prompt</div><div class="prompt-text">(.*?)</div>.*?</div>', r'\n\n> **Prompt:** \1\n', body, flags=re.DOTALL)
    body = re.sub(r'<h2>([^<]+)</h2>', r'\n\n## \1\n', body)
    body = re.sub(r'<strong>([^<]+)</strong>', r'**\1**', body)
    body = re.sub(r'<p>', '\n\n', body)
    body = re.sub(r'</p>', '\n', body)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'<ul>', '\n', body)
    body = re.sub(r'</ul>', '\n', body)
    body = re.sub(r'<li>', '- ', body)
    body = re.sub(r'</li>', '\n', body)
    body = body.replace('&quot;', '"').replace('&amp;', '&')
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\n{4,}', '\n\n', body)
    body = re.sub(r'Pack de.*?Ver Catálogo.*', '', body)
    body = body.strip()
    
    canonical = f"https://magodago.github.io/neo-jarvis/blog/{p.parent.name}/{p.name}"
    
    date = datetime.now().strftime("%d %B %Y")
    
    md = f"""# {title}

*Read the original article on [NEO Labs]({canonical})*
*Published on {date}*

---

{body}

---

**Want premium prompts ready to copy-paste into ChatGPT, Claude, and Gemini?**  
👉 [Marketing Prompt Pack — €9.99](https://payhip.com/b/Q5RYA) (Use code **NEO10** for 10% off)

*Follow [NEO Labs](https://magodago.github.io/neo-jarvis/) for more AI and productivity content.*
"""
    return title, md

def generate_medium_file(title, md):
    """Save Medium-ready markdown to desktop."""
    if not DESKTOP.exists():
        print(f"Desktop not found at {DESKTOP}")
        return
    
    safe_title = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower())[:40]
    filename = f"medium-{safe_title}-{datetime.now().strftime('%Y%m%d')}.md"
    filepath = DESKTOP / filename
    
    filepath.write_text(md, encoding='utf-8')
    print(f"✅ Medium file: {filepath}")

def post_to_linkedin():
    """Run LinkedIn poster."""
    script = REPO / "linkedin_poster.py"
    if not script.exists():
        print("linkedin_poster.py not found")
        return
    
    env = os.environ.copy()
    env["DISPLAY"] = ":99"
    
    try:
        r = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=120,
            env=env
        )
        print(r.stdout[-500:] if r.stdout else "")
        if r.returncode == 0:
            print("✅ LinkedIn: OK")
        else:
            print(f"⚠️ LinkedIn: exit {r.returncode}")
    except Exception as e:
        print(f"LinkedIn error: {e}")

if __name__ == "__main__":
    title, md = get_article_content()
    if not title:
        print("No article found")
        sys.exit(1)
    
    print(f"Auto-publishing: {title[:50]}...")
    
    generate_medium_file(title, md)
    post_to_linkedin()
    
    print("✅ Auto-publish complete")
