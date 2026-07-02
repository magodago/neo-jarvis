#!/usr/bin/env python3
"""Fast article content generator - single articles via terminal."""
import json, subprocess, re, sys, os
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

NICHE_INFO = {
    "productividad": {"brand": "#d4a853", "brand_dark": "#b8922f", "brand_light": "#f0d68a"},
    "finanzas": {"brand": "#66bb6a", "brand_dark": "#388e3c", "brand_light": "#a5d6a7"},
    "marketing": {"brand": "#42a5f5", "brand_dark": "#1976d2", "brand_light": "#90caf9"},
    "programacion": {"brand": "#ab47bc", "brand_dark": "#7b1fa2", "brand_light": "#ce93d8"},
    "estudiantes": {"brand": "#ffa726", "brand_dark": "#ef6c00", "brand_light": "#ffcc80"},
    "rrhh": {"brand": "#ec407a", "brand_dark": "#c2185b", "brand_light": "#f48fb1"},
}

def generate_body(niche, title):
    prompt = f"""Eres un redactor SEO experto en español.

TÍTULO: {title}
NICHO: {niche}

Genera SOLO las etiquetas HTML del cuerpo del artículo, sin <!DOCTYPE>, <html>, <head>, <style>.
Incluye:
- <p>Introducción que enganche</p>
- <h2>Primer punto práctico</h2>
- <p>Explicación detallada 3-4 frases</p>
- <div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">"prompt real aquí"</div></div>
- <h2>Segundo punto</h2>
- <p>Explicación + ejemplo</p>
- <div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">"otro prompt"</div></div>
- <h2>Tercer punto práctico</h2>
- <p>Explicación + caso práctico</p>
- <div class="prompt-box"><div class="prompt-label">Prompt avanzado</div><div class="prompt-text">"tercer prompt"</div></div>
- <p>Conclusión práctica</p>

400-600 palabras. Español correcto con acentos y ñ. 3 prompts accionables."""
    
    r = subprocess.run(["curl", "-s", "--max-time", "120", OLLAMA_URL, "-d", json.dumps({
        "model": "gemma4", "prompt": prompt, "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2048}
    })], capture_output=True, text=True)
    
    data = json.loads(r.stdout)
    body = data.get("response", "")
    # Clean markdown fences
    body = re.sub(r'```html?\s*', '', body)
    body = re.sub(r'```\s*', '', body)
    return body.strip()

def update_file(niche, slug, title, body):
    filepath = REPO / "blog" / niche / f"{slug}.html"
    html = filepath.read_text(encoding="utf-8")
    
    # Replace body content
    new_html = re.sub(
        r'(<div class="article-body">).*?(</div>\s*<div class="cta-box")',
        lambda m: m.group(1) + body + m.group(2),
        html, count=1, flags=re.DOTALL
    )
    
    # Update meta description
    desc = body[:120].replace('"', "'").strip()
    new_html = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{desc}"',
        new_html
    )
    
    filepath.write_text(new_html, encoding="utf-8")
    print(f"✅ {niche}/{slug} — {len(body)} chars")

def main():
    articles = [
        ("rrhh", "evaluaciones-desempeno-chatgpt", "Evaluaciones de desempeño con ChatGPT"),
        ("rrhh", "clima-laboral-analizado-ia", "Clima laboral analizado con inteligencia artificial"),
        ("programacion", "comparativa-chatgpt-claude-programar", "ChatGPT vs Claude: ¿cuál es mejor para programar?"),
        ("programacion", "refactorizar-codigo-legacy-ia", "Refactorizar código legacy con ayuda de IA"),
        ("estudiantes", "organizar-semestre-prompts", "Organiza tu semestre universitario con prompts de IA"),
        ("estudiantes", "nuevas-herramientas-ia-estudiantes", "Nuevas herramientas de IA para estudiantes en 2026"),
        ("estudiantes", "escribir-ensayos-academicos-ia", "Escribir ensayos académicos con inteligencia artificial"),
    ]
    
    for niche, slug, title in articles:
        print(f"📝 {niche}/{slug}...")
        body = generate_body(niche, title)
        if len(body) > 200:
            update_file(niche, slug, title, body)
        else:
            print(f"❌ {slug} muy corto ({len(body)} chars), reintentando...")
            body = generate_body(niche, title)
            if len(body) > 200:
                update_file(niche, slug, title, body)
            else:
                print(f"❌ {slug} definitivamente falló ({len(body)} chars)")

if __name__ == "__main__":
    main()
