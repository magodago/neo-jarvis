#!/usr/bin/env python3
"""Expand remaining thin articles with Gemma 4 - single article mode."""
import json, subprocess, re, sys
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

NICHE_INFO = {
    "productividad": {"brand": "#d4a853", "brand_dark": "#b8922f", "brand_light": "#f0d68a", "hero": "photo-1497366216548-37526070297c"},
    "finanzas": {"brand": "#66bb6a", "brand_dark": "#388e3c", "brand_light": "#a5d6a7", "hero": "photo-1554224155-8d04cb21cd6c"},
    "marketing": {"brand": "#42a5f5", "brand_dark": "#1976d2", "brand_light": "#90caf9", "hero": "photo-1557838923-2985c318be48"},
    "programacion": {"brand": "#ab47bc", "brand_dark": "#7b1fa2", "brand_light": "#ce93d8", "hero": "photo-1461749280684-dccba630e2f6"},
    "estudiantes": {"brand": "#ffa726", "brand_dark": "#ef6c00", "brand_light": "#ffcc80", "hero": "photo-1488190211105-8b0e65b80b4e"},
    "rrhh": {"brand": "#ec407a", "brand_dark": "#c2185b", "brand_light": "#f48fb1", "hero": "photo-1600880292203-757bb62b4baf"},
}

def expand_article(niche, slug, title, payhip):
    filepath = REPO / "blog" / niche / f"{slug}.html"
    info = NICHE_INFO[niche]
    
    print(f"📝 Expandiendo: {title}...")
    
    prompt = f"""Eres un redactor SEO experto en español. Vas a escribir un artículo completo de blog.

TÍTULO: {title}
NICHO: {niche}
AUDIENCIA: Hispanohablantes interesados en IA aplicada

ESTRUCTURA EXACTA (genera SOLO el HTML de .article-body):
- <p>Introducción de 2-3 frases que enganche</p>
- <h2>Primer punto importante</h2>
- <p>Explicación detallada de 3-4 frases</p>
- <div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">"prompt útil aquí"</div></div>
- <h2>Segundo punto importante</h2>
- <p>Explicación detallada de 3-4 frases</p>
- <div class="prompt-box"><div class="prompt-label">Prompt</div><div class="prompt-text">"otro prompt útil"</div></div>
- <h2>Tercer punto importante</h2>
- <p>Explicación detallada de 3-4 frases con ejemplos prácticos</p>
- <div class="prompt-box"><div class="prompt-label">Prompt avanzado</div><div class="prompt-text">"tercer prompt detallado"</div></div>
- <p>Conclusión de 2-3 frases que invite a usar los prompts</p>

REGLAS:
- 400-600 palabras
- Español correcto con acentos y ñ
- 3 prompts reales y útiles
- Tono: experto pero accesible
- Solo devuelve el contenido de .article-body, sin etiquetas html externas"""

    r = subprocess.run(["curl", "-s", OLLAMA_URL, "-d", json.dumps({
        "model": "gemma4", "prompt": prompt, "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2048}
    })], capture_output=True, text=True, timeout=180)
    
    data = json.loads(r.stdout)
    body = data.get("response", "")
    body = re.sub(r'```html\s*', '', body)
    body = re.sub(r'```\s*', '', body)
    body = body.strip()
    
    if len(body) < 200:
        print(f"❌ Contenido demasiado corto ({len(body)} chars): {slug}")
        return False
    
    # Read existing file and replace article-body content
    html = filepath.read_text(encoding="utf-8")
    
    # Replace body
    html = re.sub(
        r'(<div class="article-body">).*?(</div>\s*<div class="cta-box")',
        lambda m: m.group(1) + body + m.group(2),
        html, count=1, flags=re.DOTALL
    )
    
    # Update meta description
    desc = body[:120].replace('"', "'").strip()
    html = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{desc}"',
        html
    )
    
    # Update title if needed
    og_m = re.search(r'<meta property="og:title" content="[^"]*"', html)
    if og_m:
        html = re.sub(
            r'<meta property="og:title" content="[^"]*"',
            f'<meta property="og:title" content="{title}"',
            html
        )
    
    filepath.write_text(html, encoding="utf-8")
    print(f"✅ {niche}/{slug} expandido ({len(body)} chars)")
    return True

if __name__ == "__main__":
    # Expansiones pendientes
    pending = [
        ("rrhh", "evaluaciones-desempeno-chatgpt", "Evaluaciones de desempeño con ChatGPT", "KragB"),
        ("rrhh", "clima-laboral-analizado-ia", "Clima laboral analizado con inteligencia artificial", "KragB"),
        ("programacion", "generar-tests-automaticos-prompt", "Generar tests automáticos con un solo prompt", "XTEG5"),
        ("programacion", "comparativa-chatgpt-claude-programar", "ChatGPT vs Claude: ¿cuál es mejor para programar?", "XTEG5"),
        ("programacion", "code-review-automatico-ia", "Code review automático con inteligencia artificial", "XTEG5"),
        ("programacion", "refactorizar-codigo-legacy-ia", "Refactorizar código legacy con ayuda de IA", "XTEG5"),
        ("estudiantes", "preparar-examenes-chatgpt", "Preparar exámenes con ChatGPT: técnicas de estudio con IA", "M3eqn"),
        ("estudiantes", "organizar-semestre-prompts", "Organiza tu semestre universitario con prompts de IA", "M3eqn"),
        ("estudiantes", "nuevas-herramientas-ia-estudiantes", "Nuevas herramientas de IA para estudiantes en 2026", "M3eqn"),
        ("estudiantes", "escribir-ensayos-academicos-ia", "Escribir ensayos académicos con inteligencia artificial", "M3eqn"),
    ]
    
    ok = 0
    for niche, slug, title, payhip in pending:
        if expand_article(niche, slug, title, payhip):
            ok += 1
        print()
    
    print(f"✅ {ok}/{len(pending)} expandidos")
