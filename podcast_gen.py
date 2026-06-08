#!/usr/bin/env python3
"""
NEO Podcast Generator — Gemma 4 + edge-tts
Generates Spanish podcast conversations from article content.
100% local, 0€.
"""
import asyncio, json, subprocess, re, os, sys, argparse
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "neo-jarvis"
AUDIO_DIR = REPO / "podcasts"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Edge-TTS voices for Spanish (Spain)
HOST_VOICE = "es-ES-ElviraNeural"      # Female host
EXPERT_VOICE = "es-ES-AlvaroNeural"     # Male expert

SYSTEM_PROMPT = """Eres un guionista de podcasts. Genera una conversación entre dos personas:
- ANA (presentadora): entusiasta, cercana, hace preguntas
- CARLOS (experto): responde con claridad, da ejemplos prácticos

Reglas:
- Idioma: español neutro, natural, conversacional
- NO uses marcadores tipo [RISAS], [MÚSICA]
- Formato: "ANA: texto" / "CARLOS: texto" en líneas separadas
- Entre 6 y 10 intervenciones en total
- Cada intervención: 2-4 frases
- La conversación debe sonar real, no leer un artículo
- Al final, Carlos da un consejo práctico y Ana resume
- NO menciones que eres una IA o que esto es generado
- NO uses emojis ni asteriscos para formato"""

async def generate_script(article_text: str, title: str, niche: str) -> str:
    """Generate podcast script using Gemma 4."""
    
    prompt = f"""Título del artículo: {title}
Tema: {niche}

Contenido del artículo:
{article_text[:3000]}

Genera una conversación de podcast en español entre Ana (presentadora) y Carlos (experto) sobre este tema.
Formato: "ANA: texto" / "CARLOS: texto" """
    
    payload = {
        "model": "gemma4",
        "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 2048
        }
    }
    
    r = subprocess.run(
        ["curl", "-s", OLLAMA_URL, "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=120
    )
    result = json.loads(r.stdout)
    return result.get("response", "")

def parse_script(raw: str):
    """Parse script into list of (speaker, text) tuples."""
    lines = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        m = re.match(r"^(ANA|CARLOS):\s*(.+)", line)
        if m:
            speaker = m.group(1)
            text = m.group(2).strip()
            # Map to voice
            voice = HOST_VOICE if speaker == "ANA" else EXPERT_VOICE
            lines.append((voice, text))
    return lines

async def generate_audio(lines: list, output_path: Path):
    """Generate audio from script lines using edge-tts, merge with ffmpeg."""
    import edge_tts
    
    temp_files = []
    for i, (voice, text) in enumerate(lines):
        tmp = Path(f"/tmp/podcast_seg_{i:03d}.mp3")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(tmp))
        temp_files.append(tmp)
    
    # Create concat file for ffmpeg
    concat_file = Path("/tmp/podcast_concat.txt")
    concat_lines = [f"file '{f}'" for f in temp_files]
    concat_file.write_text("\n".join(concat_lines))
    
    # Merge all segments
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy", str(output_path)
    ], capture_output=True, check=True)
    
    # Cleanup temp files
    for f in temp_files:
        f.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)

def extract_article_text(html_path: Path) -> tuple:
    """Extract article title and text content from HTML."""
    html = html_path.read_text(encoding="utf-8")
    
    # Title
    m = re.search(r"<h1>(.*?)</h1>", html)
    title = m.group(1) if m else "Artículo"
    
    # Estaba en the .article-body div
    m2 = re.search(r'<div class="article-body">(.*?)</div>\s*<footer', html, re.DOTALL)
    if not m2:
        m2 = re.search(r'<div class="article-body">(.*?)</div>', html, re.DOTALL)
    
    if m2:
        # Strip HTML tags for text
        text = re.sub(r'<[^>]+>', ' ', m2.group(1))
        text = re.sub(r'\s+', ' ', text).strip()
    else:
        text = ""
    
    # Niche from path
    niche = html_path.parent.name if html_path.parent.name != "blog" else "general"
    
    return title, text, niche

async def process_article(html_path: Path, force: bool = False):
    """Generate podcast for an article."""
    slug = html_path.stem
    niche = html_path.parent.name
    audio_path = AUDIO_DIR / niche / f"{slug}.mp3"
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Skip if already exists
    if audio_path.exists() and not force:
        print(f"⏭️  Ya existe: {slug}")
        return audio_path
    
    title, text, niche_name = extract_article_text(html_path)
    
    if not text or len(text) < 100:
        print(f"⚠️  Poco contenido: {slug} ({len(text)} chars)")
        return None
    
    print(f"🎙️  Generando: {title} ({len(text)} chars)")
    
    # Generate script with Gemma 4
    script = await generate_script(text, title, niche_name)
    
    if not script.strip():
        print(f"❌ Script vacío para: {slug}")
        return None
    
    # Parse and generate audio
    lines = parse_script(script)
    
    if len(lines) < 4:
        print(f"⚠️  Muy pocas líneas ({len(lines)}): {slug}")
        return None
    
    await generate_audio(lines, audio_path)
    
    # Save transcript alongside
    transcript_path = AUDIO_DIR / niche / f"{slug}.txt"
    transcript_path.write_text(script)
    
    size_mb = audio_path.stat().st_size / 1024 / 1024
    print(f"✅ {slug}.mp3 ({size_mb:.1f}MB, {len(lines)} intervenciones)")
    return audio_path

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", help="Specific article path (relative to blog/)")
    parser.add_argument("--niche", help="Niche slug (productividad, finanzas, etc)")
    parser.add_argument("--force", action="store_true", help="Regenerate existing podcasts")
    parser.add_argument("--all", action="store_true", help="Process ALL articles")
    args = parser.parse_args()
    
    if args.article:
        paths = [REPO / "blog" / args.article]
    elif args.niche:
        niche_dir = REPO / "blog" / args.niche
        paths = sorted(niche_dir.glob("*.html"))
        paths = [p for p in paths if p.stem != "index"]
    elif args.all:
        paths = []
        for niche_dir in sorted((REPO / "blog").iterdir()):
            if niche_dir.is_dir() and niche_dir.name != "audio":
                for p in niche_dir.glob("*.html"):
                    if p.stem != "index":
                        paths.append(p)
        # Also podcast-level article pages
        for p in (REPO / "blog").glob("prompts-*.html"):
            paths.append(p)
        paths.sort()
    else:
        parser.print_help()
        return
    
    print(f"🎧 Procesando {len(paths)} artículos...")
    results = []
    for p in paths:
        result = await process_article(p, force=args.force)
        results.append(result)
    
    success = sum(1 for r in results if r)
    print(f"\n📊 Resumen: {success}/{len(paths)} podcasts generados")

if __name__ == "__main__":
    asyncio.run(main())
