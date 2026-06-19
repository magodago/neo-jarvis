#!/usr/bin/env python3
"""LinkedIn personal post — genera y publica contenido de IA profesional."""
import json, os, sys, requests
from pathlib import Path
from datetime import datetime

STORAGE = Path.home() / ".hermes" / "linkedin_storage.json"
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_KEY:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("DEEPSEEK_API_KEY="):
                DEEPSEEK_KEY = line.split("=", 1)[1].strip().strip("'\"")
DEEPSEEK_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1") + "/chat/completions"

QUERY_ID = "voyagerContentcreationDashShares.279996efa5064c01775d5aff003d9377"

def generate_post():
    prompt = """Escribe un post corto para LinkedIn sobre inteligencia artificial aplicada a negocio o productividad. 

REGLAS ESTRICTAS:
- Sin emojis, sin hashtags
- Tono profesional, lenguaje humano natural
- Máximo 250 palabras
- Que suene a experiencia real, no a artículo genérico
- Tema: tendencia actual de IA aplicada al trabajo, gestión de proyectos AI, o reflexión profesional sobre el impacto de la IA
- Sin markdown ni formato — texto plano
- Sin firma ni despedida
- Escrito en primera persona, como alguien que trabaja con IA cada día

Escribe SÓLO el texto del post, nada más."""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 500,
    }

    resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print(f"❌ DeepSeek error: {resp.status_code}")
        return None
    
    post_text = resp.json()["choices"][0]["message"]["content"].strip()
    # Clean up any lingering markdown
    post_text = post_text.strip('"\'')
    return post_text

def post_to_linkedin(text):
    state = json.loads(Path(STORAGE).read_text())
    cookies_list = state.get("cookies", [])
    li_at = next((c["value"] for c in cookies_list if c["name"] == "li_at"), None)
    jsessionid = next((c["value"] for c in cookies_list if c["name"] == "JSESSIONID"), None)
    
    if not li_at or not jsessionid:
        print("❌ No cookies")
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
        print("✅ LinkedIn personal post published!")
        return True
    else:
        print(f"❌ Error: {resp.status_code}")
        return False

if __name__ == "__main__":
    print(f"Generando post personal LinkedIn ({datetime.now().strftime('%H:%M')})...")
    
    text = generate_post()
    if not text:
        print("❌ No se pudo generar el texto")
        sys.exit(1)
    
    print(f"Post: {text[:80]}...")
    success = post_to_linkedin(text)
    sys.exit(0 if success else 1)
