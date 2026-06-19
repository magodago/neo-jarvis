#!/usr/bin/env python3
"""LinkedIn auto-poster — uses saved storage state for session."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import re, sys, json

STORAGE = Path.home() / ".hermes" / "linkedin_storage.json"

def get_article():
    articles = []
    blog = Path.home() / "neo-jarvis" / "blog"
    for nd in blog.iterdir():
        if not nd.is_dir() or nd.name.startswith("."):
            continue
        for f in nd.glob("*.html"):
            if f.name == "index.html":
                continue
            articles.append((f.stat().st_mtime, f))
    if not articles:
        return None, None, None
    articles.sort(reverse=True)
    _, p = articles[0]
    c = p.read_text(encoding="utf-8")
    title = (re.search(r'<h1>([^<]+)', c) or [None, "Article"]).group(1)
    ex = (re.search(r'<p>([^<]+)', c) or [None, ""]).group(1)[:200]
    url = f"https://magodago.github.io/neo-jarvis/blog/{p.parent.name}/{p.name}"
    return title, url, ex

if __name__ == "__main__":
    title, url, excerpt = get_article()
    if not title:
        print("No article today")
        sys.exit(1)
    
    print(f"Posting to LinkedIn: {title[:50]}...")
    
    with sync_playwright() as p:
        storage_state = None
        if STORAGE.exists():
            storage_state = json.loads(STORAGE.read_text())
        
        b = p.chromium.launch(headless=False, args=['--no-sandbox'])
        ctx = b.new_context(
            viewport={'width': 1280, 'height': 800},
            storage_state=storage_state
        )
        page = ctx.new_page()
        
        try:
            page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            
            if 'feed' not in page.url:
                print("Session expired. Run linkedin_setup.py first.")
                page.screenshot(path="/tmp/linkedin_expired.png")
                sys.exit(1)
            
            print("✅ Session valid")
            
            # Try clicking "Start a post"
            start_post = page.get_by_text("Start a post", exact=False)
            if start_post.count() > 0:
                start_post.click()
            else:
                # Click the first text area on feed
                for sel in ['div[contenteditable="true"]', '[role="textbox"]', 'div[data-artdeco-is-focused="true"]']:
                    els = page.locator(sel).all()
                    for el in els:
                        if el.is_visible():
                            el.click()
                            break
                    else:
                        continue
                    break
            
            page.wait_for_timeout(3000)
            
            post_text = f"""{title}

{excerpt}...

Read more: {url}

#IA #InteligenciaArtificial #MarketingDigital #Productividad"""
            
            # Type into editor
            editor = page.locator('div[contenteditable="true"]').first
            if editor.is_visible():
                editor.fill(post_text)
                page.wait_for_timeout(2000)
                
                post_btn = page.locator('button:has-text("Post")').first
                if post_btn.count() > 0:
                    post_btn.click()
                    page.wait_for_timeout(3000)
                    print("✅ LinkedIn post published!")
                else:
                    print("Post button not found")
                    page.screenshot(path="/tmp/li_no_post_btn.png")
            else:
                print("Editor not visible")
                page.screenshot(path="/tmp/li_no_editor.png")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="/tmp/li_error.png")
        finally:
            ctx.close()
            b.close()
