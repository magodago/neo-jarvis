#!/usr/bin/env python3
"""Auto-publish master v2 — API LinkedIn + Medium file."""
import json, os, sys, re, requests
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
DESKTOP = Path("/mnt/c/Users/dorti/Desktop")
ENV = Path.home() / ".hermes" / ".env"
STORAGE = Path.home() / ".hermes" / "linkedin_storage.json"

QUERY_ID = "voyagerContentcreationDashShares.279996efa5064c01775d5aff003d9377"

def load_env():
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip("'\"")

def get_article():
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
        return None, None, None, None, None
    articles.sort(reverse=True)
    _, p = articles[0]
    c = p.read_text(encoding="utf-8")
    title_m = re.search(r'<h1>([^<]+)', c)
    title = title_m.group(1) if title_m else "Article"
    body_m = re.search(r'<div class="article-body">(.*?)</div>', c, re.DOTALL)
    body = body_m.group(1) if body_m else ""
    ex_m = re.search(r'<p class="article-excerpt">([^<]+)', c) or re.search(r'<p>([^<]+)', c)
    excerpt = ex_m.group(1)[:250].strip() if ex_m and ex_m.group(1) else ""
    
    # Get image URL if exists
    img_m = re.search(r'<div class="article-hero"><img src="([^"]+)"', c)
    img_url = img_m.group(1) if img_m else None
    
    # Convert HTML to markdown
    body = re.sub(r'<div class="prompt-box">.*?<div class="prompt-label">Prompt</div><div class="prompt-text">(.*?)</div>.*?</div>', r'\n\n> **Prompt:** \1\n', body, flags=re.DOTALL)
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
    
    url = f"https://magodago.github.io/neo-jarvis/blog/{p.parent.name}/{p.name}"
    return title, url, excerpt, img_url, body

def generate_medium_file(title, url, body, img_url):
    if not DESKTOP.exists():
        print(f"Desktop not found")
        return
    
    date = datetime.now().strftime("%d %B %Y")
    
    img_md = f"![{title}]({img_url})\n\n" if img_url else ""
    
    md = f"""# {title}

*Read the original article on [NEO Labs]({url})*
*Published on {date}*

---

{img_md}{body}

---

**Want premium prompts ready to copy-paste into ChatGPT, Claude, and Gemini?**  
👉 [Marketing Prompt Pack — €9.99](https://payhip.com/b/Q5RYA) (Use code **NEO10** for 10% off)

*Follow [NEO Labs](https://magodago.github.io/neo-jarvis/) for more AI and productivity content.*"""

    safe_title = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower())[:40]
    filename = f"medium-{safe_title}-{datetime.now().strftime('%Y%m%d')}.md"
    filepath = DESKTOP / filename
    filepath.write_text(md, encoding='utf-8')
    print(f"✅ Medium file: {filepath}")

def post_to_linkedin_api(text):
    state = json.loads(Path(STORAGE).read_text())
    cookies_list = state.get("cookies", [])
    li_at = next((c["value"] for c in cookies_list if c["name"] == "li_at"), None)
    jsessionid = next((c["value"] for c in cookies_list if c["name"] == "JSESSIONID"), None)
    
    if not li_at or not jsessionid:
        print("❌ No LinkedIn cookies")
        return False
    
    cookies = {"li_at": li_at, "JSESSIONID": '"' + jsessionid + '"'}
    headers = {
        "User-Agent": "Mozilla/5.0", "Content-Type": "application/json; charset=UTF-8",
        "Csrf-Token": jsessionid, "X-RestLi-Protocol-Version": "2.0.0",
    }
    payload = {
        "variables": {
            "post": {
                "allowedCommentersScope": "ALL",
                "intendedShareLifeCycleState": "PUBLISHED",
                "origin": "FEED",
                "visibilityDataUnion": {"visibilityType": "ANYONE"},
                "commentary": {"text": text, "attributesV2": []}
            }
        },
        "queryId": QUERY_ID,
        "includeWebMetadata": True,
    }
    
    url = f"https://www.linkedin.com/voyager/api/graphql?action=execute&queryId={QUERY_ID}"
    resp = requests.post(url, headers=headers, cookies=cookies, json=payload, timeout=30)
    
    if resp.status_code in (200, 201):
        print("✅ LinkedIn post published!")
        return True
    else:
        print(f"⚠️ LinkedIn error: {resp.status_code}")
        return False

if __name__ == "__main__":
    load_env()
    result = get_article()
    if not result[0]:
        print("No article found")
        sys.exit(1)
    
    title, url, excerpt, img_url, body = result
    
    print(f"Auto-publishing: {title[:50]}...")
    
    # Generate Medium file
    generate_medium_file(title, url, body, img_url)
    
    # Post to LinkedIn
    li_text = f"""{title}

{excerpt}...

Lee el artículo completo: {url}

#IA #InteligenciaArtificial #Productividad #NEO"""
    post_to_linkedin_api(li_text)
    
    print("✅ Auto-publish complete")
