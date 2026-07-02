#!/usr/bin/env python3
"""Añade hero images a todos los artículos del blog."""
import re
from pathlib import Path

BLOG = Path.home() / "neo-jarvis" / "blog"

# Unsplash photo IDs for each category
CATEGORY_IMAGES = {
    "productividad": "photo-1506784365847-bbad939e9335",
    "marketing": "photo-1460925895917-afdab827c52f",
    "finanzas": "photo-1554224155-8d04cb21cd6c",
    "programacion": "photo-1461749280684-dccba630e2f6",
    "estudiantes": "photo-1488190211105-8b0e65b80b4e",
    "rrhh": "photo-1600880292203-757bb62b4baf",
}

DEFAULT_IMG = "photo-1497366216548-37526070297c"

def add_image_to_article(filepath: Path, image_id: str):
    content = filepath.read_text(encoding="utf-8")
    
    # Skip if already has image
    if 'article-hero' in content:
        return False
    
    # Find the insertion point: after </div> that closes article-header, before <div class="article-body">
    # Pattern: </div>\n<div class="article-body">
    pattern = r'(</div>\s*\n\s*)(<div class="article-body">)'
    replacement = f'\\1<div class="article-hero"><img src="https://images.unsplash.com/{image_id}?w=780&h=400&fit=crop" alt="" loading="lazy"></div>\n\\2'
    
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content == content:
        return False  # Pattern not found
    
    filepath.write_text(new_content, encoding="utf-8")
    return True

# Process all articles
updated = 0
for nd in sorted(BLOG.iterdir()):
    if not nd.is_dir() or nd.name.startswith("."):
        continue
    
    img_id = CATEGORY_IMAGES.get(nd.name, DEFAULT_IMG)
    
    for f in sorted(nd.glob("*.html")):
        if f.name == "index.html":
            continue
        if add_image_to_article(f, img_id):
            updated += 1
            print(f"✅ {nd.name}/{f.name}")
        else:
            print(f"  Skipped (has image or pattern not found): {nd.name}/{f.name}")

print(f"\nTotal actualizados: {updated}")
