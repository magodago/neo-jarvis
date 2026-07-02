#!/usr/bin/env python3
"""LinkedIn poster v9 — API directa con endpoint real capturado."""
import json, sys, re, requests
from pathlib import Path

STORAGE = Path.home() / ".hermes" / "linkedin_storage.json"

# Query ID from actual LinkedIn API call (stable across sessions?)
QUERY_ID = "voyagerContentcreationDashShares.279996efa5064c01775d5aff003d9377"

def get_cookies():
    state = json.loads(Path(STORAGE).read_text())
    cookies = state.get("cookies", [])
    li_at = next((c["value"] for c in cookies if c["name"] == "li_at"), None)
    jsessionid = next((c["value"] for c in cookies if c["name"] == "JSESSIONID"), None)
    return li_at, jsessionid

def get_latest_article():
    articles = []
    blog = Path.home() / "neo-jarvis" / "blog"
    for nd in blog.iterdir():
        if not nd.is_dir() or nd.name.startswith("."):
            continue
        for f in sorted(nd.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.name == "index.html":
                continue
            articles.append((f.stat().st_mtime, f))
    if not articles:
        return None, None, None
    articles.sort(reverse=True)
    _, p = articles[0]
    c = p.read_text(encoding="utf-8")
    title_m = re.search(r'<h1>([^<]+)', c)
    title = title_m.group(1).strip() if title_m else "Nuevo artículo"
    ex_m = re.search(r'<p class="article-excerpt">([^<]+)', c) or re.search(r'<p>([^<]+)', c)
    excerpt = ex_m.group(1)[:250].strip() if ex_m else ""
    url = f"https://magodago.github.io/neo-jarvis/blog/{p.parent.name}/{p.name}"
    return title, url, excerpt

def post_to_linkedin(post_text):
    li_at, jsessionid = get_cookies()
    if not li_at or not jsessionid:
        print("❌ No cookies. Run linkedin_setup.py first.")
        return False
    
    cookies = {
        "li_at": li_at,
        "JSESSIONID": '"' + jsessionid + '"',
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        "Csrf-Token": jsessionid,
        "X-RestLi-Protocol-Version": "2.0.0",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "x-li-lang": "es_ES",
    }
    
    payload = {
        "variables": {
            "post": {
                "allowedCommentersScope": "ALL",
                "intendedShareLifeCycleState": "PUBLISHED",
                "origin": "FEED",
                "visibilityDataUnion": {
                    "visibilityType": "ANYONE"
                },
                "commentary": {
                    "text": post_text,
                    "attributesV2": []
                }
            }
        },
        "queryId": QUERY_ID,
        "includeWebMetadata": True,
    }
    
    url = "https://www.linkedin.com/voyager/api/graphql?action=execute&queryId=" + QUERY_ID
    
    print("Posting to LinkedIn API...")
    resp = requests.post(url, headers=headers, cookies=cookies, json=payload, timeout=30)
    
    print(f"Status: {resp.status_code}")
    if resp.status_code in (200, 201):
        print("✅ LinkedIn post published!")
        return True
    else:
        print(f"❌ Error: {resp.text[:500]}")
        return False

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "blog"
    
    if mode == "personal":
        post_text = """La inteligencia artificial está transformando la forma en que trabajamos, pero hay una conversación que apenas está empezando: cómo gestionar equipos donde algunos miembros son agentes autónomos.

Llevo meses trabajando con asistentes AI que escriben código, investigan mercados, redactan documentación y publican contenido de forma autónoma. No es el futuro, es el presente. Y plantea preguntas que ningún manual de gestión de proyectos cubre todavía.

Mi conclusión después de estos meses: el rol del gestor de proyectos no desaparece, pero se transforma. Menos supervisión de tareas mecánicas, más definición de objetivos estratégicos.

Los mejores resultados no vienen de sustituir personas por AI, sino de rediseñar los procesos para que humanos y AI hagan lo que cada uno hace mejor."""
    else:
        title, url, excerpt = get_latest_article()
        if not title:
            print("No article today")
            sys.exit(1)
        post_text = f"""{title}

{excerpt}...

Lee el artículo completo: {url}

#IA #InteligenciaArtificial #Productividad #NEO"""
    
    success = post_to_linkedin(post_text)
    sys.exit(0 if success else 1)
