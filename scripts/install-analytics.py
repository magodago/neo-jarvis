#!/usr/bin/env python3
"""Install analytics + GSC verification + sitemap updater across all pages."""
import re
from pathlib import Path

REPO = Path.home() / "neo-jarvis"

# Analytics snippet (GoatCounter - replace 'neo-jarvis' with your code after signup)
ANALYTICS = '''<!-- GoatCounter analytics -->
<script data-goatcounter="https://neo-jarvis.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<noscript><img src="https://neo-jarvis.goatcounter.com/count?p=/test"></noscript>'''

# GSC meta verification tag (replace content with your actual code)
GSC_META = '<meta name="google-site-verification" content="REPLACE_WITH_YOUR_CODE" />'

def inject_before_closing_tag(html, tag, snippet):
    """Inject snippet before closing </tag>."""
    closing = f"</{tag}>"
    if closing in html and snippet not in html:
        html = html.replace(closing, f"{snippet}\n{closing}")
    return html

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    changed = False
    
    # 1. Add GSC meta in <head>
    if '</head>' in html and 'google-site-verification' not in html:
        html = html.replace('</head>', f'  {GSC_META}\n</head>')
        changed = True
        print(f"  ✓ GSC meta: {path.name}")
    
    # 2. Add analytics before </body>
    if '</body>' in html and 'goatcounter' not in html:
        html = html.replace('</body>', f'{ANALYTICS}\n</body>')
        changed = True
        print(f"  ✓ Analytics: {path.name}")
    
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False

def main():
    html_files = list(REPO.rglob("*.html"))
    count = 0
    for f in sorted(html_files):
        # Skip non-content files
        if 'Zone.Identifier' in str(f) or '.git' in str(f):
            continue
        if process_file(f):
            count += 1
    
    print(f"\nTotal archivos modificados: {count} de {len(html_files)}")

if __name__ == "__main__":
    main()
