#!/usr/bin/env python3
"""LinkedIn personal post V2 — genera texto + imagen AI y publica ambos."""
import json, os, sys, requests, random, time
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
COMFY_URL = "http://127.0.0.1:8188"
QUERY_ID = "voyagerContentcreationDashShares.279996efa5064c01775d5aff003d9377"

POST_TYPES = ["experiencia", "noticia", "tutorial"]
POST_INDEX_FILE = Path.home() / ".hermes" / "li_post_index.json"

def get_next_post_type():
    """Return post type based on day of week.
    5 noticias + 1 experiencia + 1 tutorial por semana.
    L=noticia, M=noticia, X=alterna, J=noticia, V=noticia, S=alterna, D=noticia"""
    from datetime import datetime
    dow = datetime.now().weekday()  # 0=Monday
    week = datetime.now().isocalendar()[1]  # ISO week number for alternation
    
    # Wednesday (2) and Saturday (5) alternate each week
    if dow == 2:   # Wednesday
        return "experiencia" if week % 2 == 0 else "tutorial"
    elif dow == 5:  # Saturday
        return "tutorial" if week % 2 == 0 else "experiencia"
    else:
        return "noticia"

def generate_post(post_type):
    templates = {
        "experiencia": """Escribe un post corto para LinkedIn sobre una experiencia real trabajando con inteligencia artificial en el día a día. 
Tono: profesional pero cercano, en primera persona.
Tema: un aprendizaje real aplicando IA en tu trabajo (automatización, productividad, toma de decisiones, etc.).
REGLAS:
- Sin emojis, sin hashtags
- Máximo 250 palabras
- Texto plano sin markdown
- Sin firma ni despedida
- Que suene a experiencia auténtica, no a artículo""",

        "noticia": """Escribe un post corto para LinkedIn analizando una noticia reciente del mundo de la IA.
Tono: profesional, analítico, con opinión propia.
Tema: elige una noticia REAL reciente sobre IA (lanzamiento, regulación, avance, polémica) y da tu perspectiva.
REGLAS:
- Sin emojis, sin hashtags
- Máximo 250 palabras
- Texto plano sin markdown
- Sin firma ni despedida
- Menciona el hecho concreto y da tu opinión""",

        "tutorial": """Escribe un post corto para LinkedIn con un mini-tutorial o consejo práctico sobre IA aplicada.
Tono: didáctico, útil, directo.
Tema: un workflow, prompt, herramienta o método que hayas usado y funcione.
REGLAS:
- Sin emojis, sin hashtags
- Máximo 250 palabras
- Texto plano sin markdown
- Sin firma ni despedida
- Que sea replicable por el lector"""
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": templates[post_type]}],
        "temperature": 0.8,
        "max_tokens": 500,
    }

    resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print(f"❌ DeepSeek error: {resp.status_code}")
        return None, None
    
    post_text = resp.json()["choices"][0]["message"]["content"].strip()
    post_text = post_text.strip("'\"")
    
    # Now generate an image theme based on the post
    img_prompt_payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f""""Generate only an image prompt in English for a professional LinkedIn post illustration related to this text. Max 35 words. Describe the SETTING or ENVIRONMENT relevant to the topic (factory floor, server room, office desk, circuit board, data center corridor). NO close-up humans — at most distant silhouettes. Focus on objects, spaces, equipment. Photorealistic, professional. No text on image.\n\nPost text: {post_text[:300]}\n\nImage prompt:"""}],
        "temperature": 0.6,
        "max_tokens": 100,
    }
    resp2 = requests.post(DEEPSEEK_URL, headers=headers, json=img_prompt_payload, timeout=30)
    img_prompt = "Professional LinkedIn illustration, "
    if resp2.status_code == 200:
        img_prompt += resp2.json()["choices"][0]["message"]["content"].strip().strip("'\"")
    else:
        img_prompt += "futuristic office with holographic data displays, clean professional atmosphere"
    
    return post_text, img_prompt

def generate_image(prompt):
    """Generate image via ComfyUI API using RealVisXL V4.0"""
    seed = random.randint(0, 2**31)
    width, height = 1024, 1024
    
    # SDXL txt2img workflow
    workflow = {
        "3": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "RealVisXL_V4.0.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["3", 1]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {
            "text": "(worst quality:1.5), (low quality:1.5), blurry, bad anatomy, extra limbs, extra hands, mutilated hands, missing fingers, deformed, malformed limbs, disfigured, ugly, text, watermark, signature, logo, frame",
            "clip": ["3", 1]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 20, "cfg": 5,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1,
            "model": ["3", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "li_post", "images": ["8", 0]}},
    }
    
    resp = requests.post(f"{COMFY_URL}/prompt", json={"prompt": workflow}, timeout=120)
    if resp.status_code != 200:
        print(f"❌ ComfyUI error: {resp.status_code} - {resp.text[:200]}")
        return None
    
    prompt_id = resp.json()["prompt_id"]
    print(f"  Image generating (prompt_id: {prompt_id})...")
    
    # Wait for completion
    for _ in range(60):
        time.sleep(2)
        hist = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10)
        if hist.status_code == 200:
            data = hist.json().get(prompt_id, {})
            if data.get("status", {}).get("status_str") == "success":
                outputs = data.get("outputs", {})
                for node_id, node_out in outputs.items():
                    for img_data in node_out.get("images", []):
                        img_path = f"/tmp/li_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        img_resp = requests.get(f"{COMFY_URL}/view", params={
                            "filename": img_data["filename"],
                            "subfolder": img_data.get("subfolder", ""),
                            "type": "output"
                        })
                        if img_resp.status_code == 200:
                            Path(img_path).write_bytes(img_resp.content)
                            print(f"  ✅ Image saved: {img_path}")
                            return img_path
                break
        time.sleep(3)
    
    print("❌ Image generation timed out")
    return None

def post_to_linkedin(text, image_path=None):
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
    
    # Build post payload
    post_payload = {
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
    
    # If we have an image, add media
    if image_path and os.path.exists(image_path):
        print("  Attempting image upload to LinkedIn...")
        # LinkedIn Voyager media upload
        try:
            # Step 1: Register media upload
            upload_meta = {
                "mediaUploadType": "IMAGE",
                "fileSize": os.path.getsize(image_path),
            }
            meta_resp = requests.post(
                "https://www.linkedin.com/voyager/api/voyagerMediaUploadMetadata",
                headers=headers, cookies=cookies, json=upload_meta, timeout=15
            )
            if meta_resp.status_code in (200, 201):
                meta_data = meta_resp.json()
                upload_url = meta_data.get("value", {}).get("uploadUrl") or meta_data.get("uploadUrl")
                media_urn = meta_data.get("value", {}).get("mediaArtifact") or meta_data.get("mediaArtifact")
                
                if upload_url and media_urn:
                    # Step 2: Upload image binary
                    with open(image_path, "rb") as f:
                        upload_resp = requests.put(upload_url, data=f, timeout=30)
                    if upload_resp.status_code in (200, 201):
                        # Step 3: Add media to post
                        post_payload["variables"]["post"]["media"] = {
                            "media": media_urn,
                            "status": "READY",
                        }
                        print("  ✅ Image uploaded to LinkedIn")
        except Exception as e:
            print(f"  ⚠️ Image upload failed: {e}")
    
    # Step 4: Post
    url = f"https://www.linkedin.com/voyager/api/graphql?action=execute&queryId={QUERY_ID}"
    resp = requests.post(url, headers=headers, cookies=cookies, json=post_payload, timeout=30)
    
    if resp.status_code in (200, 201):
        print("✅ LinkedIn post published!")
        # Clean up local image
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            print("  Image cleaned up")
        return True
    else:
        print(f"❌ LinkedIn error: {resp.status_code}")
        print(f"   Response: {resp.text[:300]}")
        return False

if __name__ == "__main__":
    print(f"📝 LinkedIn V2 ({datetime.now().strftime('%H:%M')})...")
    
    post_type = get_next_post_type()
    print(f"  Type: {post_type}")
    
    text, img_prompt = generate_post(post_type)
    if not text:
        print("❌ No se pudo generar el texto")
        sys.exit(1)
    
    print(f"  Post: {text[:80]}...")
    print(f"  Image prompt: {img_prompt[:80]}...")
    
    # Generate image
    img_path = generate_image(img_prompt)
    
    # Post to LinkedIn
    success = post_to_linkedin(text, img_path)
    sys.exit(0 if success else 1)
