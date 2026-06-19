#!/usr/bin/env python3
"""Auto-publish today's article to Medium via browser automation."""
import os, sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("MEDIUM_EMAIL", "")
PASSWORD = os.environ.get("MEDIUM_PASSWORD", "")

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"

def get_latest_article():
    """Get most recent blog article as Medium-ready markdown."""
    articles = []
    for niche_dir in BLOG.iterdir():
        if not niche_dir.is_dir() or niche_dir.name.startswith("."):
            continue
        for f in niche_dir.glob("*.html"):
            if f.name == "index.html":
                continue
            articles.append((f.stat().st_mtime, f))
    if not articles:
        return None, None
    articles.sort(reverse=True)
    _, article_path = articles[0]
    
    content = article_path.read_text(encoding="utf-8")
    title_m = re.search(r'<h1>([^<]+)', content)
    title = title_m.group(1) if title_m else "NEO Labs Article"
    
    body_match = re.search(r'<div class="article-body">(.*?)</div>', content, re.DOTALL)
    body_html = body_match.group(1) if body_match else ""
    
    # Convert to clean markdown
    body = body_html
    body = re.sub(r'<div class="prompt-box">.*?<div class="prompt-label">Prompt</div><div class="prompt-text">(.*?)</div>.*?</div>',
                  r'\n\n> **Prompt:** \1\n', body, flags=re.DOTALL)
    body = re.sub(r'<h2>([^<]+)</h2>', r'\n\n## \1\n', body)
    body = re.sub(r'<strong>([^<]+)</strong>', r'**\1**', body)
    body = re.sub(r'<p>', '\n\n', body)
    body = re.sub(r'</p>', '\n', body)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'<ul>', '\n', body)
    body = re.sub(r'</ul>', '\n', body)
    body = re.sub(r'<li>', '- ', body)
    body = re.sub(r'</li>', '\n', body)
    body = body.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\n{4,}', '\n\n', body)
    body = body.strip()
    body = re.sub(r'Pack de.*?Ver Catálogo.*', '', body)
    
    canonical = f"https://magodago.github.io/neo-jarvis/blog/{article_path.parent.name}/{article_path.name}"
    
    markdown = f"""# {title}

*Read the original article on [NEO Labs]({canonical})*

---

{body}

---

**Want premium prompts ready to copy-paste into ChatGPT, Claude, and Gemini?**  
👉 [Marketing Prompt Pack — €9.99](https://payhip.com/b/Q5RYA) (Use code **NEO10** for 10% off)

*Follow [NEO Labs](https://magodago.github.io/neo-jarvis/) for more AI and productivity content.*
"""
    return title, markdown

def post_to_medium(title, markdown):
    print(f"Posting to Medium: {title[:60]}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            print("1. Opening Medium sign in...")
            page.goto('https://medium.com/m/signin', wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            
            print("2. Clicking 'Sign in with email'...")
            email_btn = page.get_by_text("Sign in with email", exact=True)
            email_btn.click()
            page.wait_for_timeout(2000)
            
            print("3. Entering email...")
            email_input = page.locator('input[type="email"]')
            email_input.wait_for(timeout=10000)
            email_input.fill(EMAIL)
            
            print("4. Clicking Continue...")
            continue_btn = page.get_by_text("Continue", exact=True)
            continue_btn.click()
            page.wait_for_timeout(2000)
            
            print("5. Entering password...")
            pass_input = page.locator('input[type="password"]')
            pass_input.wait_for(timeout=10000)
            pass_input.fill(PASSWORD)
            page.wait_for_timeout(500)
            
            print("6. Clicking Sign in...")
            signin_btn = page.get_by_text("Sign in", exact=True)
            signin_btn.click()
            
            print("7. Waiting for login...")
            page.wait_for_timeout(5000)
            
            print("8. Opening new story...")
            page.goto('https://medium.com/new-story', wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)
            
            print("9. Writing title...")
            # Click on the editor to focus
            page.locator('[data-testid="editor"]').first.click()
            page.wait_for_timeout(500)
            
            # Type title
            page.keyboard.type(title, delay=15)
            page.wait_for_timeout(1000)
            
            print("10. Writing content...")
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            # Paste content in chunks
            content = markdown[len(title) + 1:]
            page.keyboard.type(content, delay=2)
            
            page.wait_for_timeout(2000)
            
            print("11. Publishing...")
            publish_btn = page.locator('button:has-text("Publish")')
            publish_btn.first.click()
            page.wait_for_timeout(2000)
            
            # Check for "Publish now" confirmation
            try:
                publish_now = page.get_by_text("Publish now", exact=True)
                if publish_now.count() > 0:
                    publish_now.click()
                    page.wait_for_timeout(2000)
            except:
                pass
            
            print("✅ Article published to Medium!")
            print(f"   URL: {page.url}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="/tmp/medium_error2.png")
            print("Screenshot saved")
        finally:
            browser.close()

if __name__ == "__main__":
    title, markdown = get_latest_article()
    if not title:
        print("No article found")
        sys.exit(1)
    print(f"Article: {title}")
    post_to_medium(title, markdown)
