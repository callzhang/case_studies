from playwright.sync_api import sync_playwright
import time
import os
import html2text
from urllib.parse import urljoin

# Configuration
OUTPUT_DIR = "case_studies"
START_URL = "https://www.feishu.cn/customers"
HEADLESS_MODE = True
MAX_CASES = 1000 

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Makers that indicate the END of the header section in markdown.
HEADER_END_MARKERS = [
    "[联系销售](/landing/feishu_contact_sales",
    "[免费试用](https://www.feishu.cn/accounts/page/ug_register",
    "[下载飞书](https://www.feishu.cn/download)",
    "[登录](https://login.feishu.cn/suite/passport/page/login"
]

def clean_filename(title):
    if not title: return "untitled_case"
    return "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip().replace(" ", "_")

def clean_markdown_content(markdown_text):
    """Removes header junk from the start of the markdown content."""
    
    # 1. Look for Header End markers in the first 3000 chars
    search_scope_len = min(len(markdown_text), 3000)
    search_scope = markdown_text[:search_scope_len]
    
    cutoff_index = -1
    for marker in HEADER_END_MARKERS:
        idx = search_scope.rfind(marker)
        if idx != -1:
            line_end = search_scope.find('\n', idx)
            if line_end != -1:
                cutoff_index = max(cutoff_index, line_end + 1)
    
    if cutoff_index != -1:
        return markdown_text[cutoff_index:].strip()
        
    return markdown_text

def get_processed_urls():
    """Scans existing markdown files to find URLs that have already been scraped."""
    processed = set()
    if not os.path.exists(OUTPUT_DIR):
        return processed
        
    print("🔍 Scanning existing files for processed URLs...")
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".md"):
            try:
                with open(os.path.join(OUTPUT_DIR, filename), "r", encoding="utf-8") as f:
                    for _ in range(20): # Scan first 20 lines
                        line = f.readline()
                        if line.startswith("URL:"):
                            url = line.replace("URL:", "").strip()
                            processed.add(url)
                            break
            except Exception:
                pass
    
    print(f"   Found {len(processed)} already processed cases.")
    return processed

def save_case_study(page, url):
    try:
        # print(f"   Processing: {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded") 
        time.sleep(0.5)
        
        full_title = page.title()
        title = full_title
        for suffix in [" - 飞书成功案例", "成功案例 - 飞书", "-飞书官网", " - 飞书", " - Feishu"]:
            title = title.replace(suffix, "")
        
        # Try to remove nav/header elements from DOM before extraction
        try:
            page.evaluate("""() => {
                document.querySelectorAll('header, nav, .header-wrapper, .navigation-wrapper').forEach(el => el.remove());
            }""")
        except:
            pass

        content_loc = page.locator("article")
        if not content_loc.count():
             content_loc = page.locator("main")
        if not content_loc.count():
            content_loc = page.locator(".content-wrapper") 
        if not content_loc.count():
            content_loc = page.locator("body")

        html_content = content_loc.inner_html()
        
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0 
        markdown = h.handle(html_content)
        
        # 1. Clean Header Junk
        markdown = clean_markdown_content(markdown)
        
        # 2. Clean Footer/More Cases
        split_markers = ["## 更多客户案例", "### 更多客户案例", "更多客户案例", "相关推荐"]
        for marker in split_markers:
            if marker in markdown:
                markdown = markdown.split(marker)[0]
                break
        
        safe_name = clean_filename(title)
        filename = os.path.join(OUTPUT_DIR, f"{safe_name}.md")
        
        if len(markdown) < 50:
            print(f"     ⚠️ Content too short ({len(markdown)} chars), skipping save.")
            return

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nURL: {url}\n\n{markdown}")
        
        print(f"     ✅ Saved {safe_name}")
        
    except Exception as e:
        print(f"     ❌ Failed: {e}")

def run_scraper():
    # 1. Load already processed URLs to skip them
    processed_urls = get_processed_urls()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context(
             user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"🌍 Link Discovery Phase @ {START_URL}")
        page.goto(START_URL)
        page.wait_for_load_state("domcontentloaded")
        
        try:
             all_tab = page.get_by_text("全部", exact=True)
             if all_tab.count():
                 all_tab.first.click()
                 time.sleep(1)
        except:
             pass

        while True:
            expand_btn = page.get_by_text("展开全部")
            if expand_btn.count() and expand_btn.first.is_visible():
                print("   🔄 Expanding list...")
                try:
                    expand_btn.first.click()
                    time.sleep(2) 
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)
                except:
                    break
            else:
                break
        
        print("   🔍 Extracting URLs from cards...")
        links = page.locator(".customers-card a[href]").element_handles()
        
        extracted_urls = set()
        for link in links:
            href = link.get_attribute("href")
            if href:
                full_url = urljoin(START_URL, href)
                if "/customers/" in full_url or "/client/" in full_url:
                     # Check against processed list, handling potential slight variations (trailing slash)
                     if full_url not in processed_urls:
                        extracted_urls.add(full_url)
        
        print(f"   📊 Found {len(extracted_urls)} NEW unique case URLs (Skipped {len(processed_urls)}).")
        print(f"🚀 Entering Scraping Phase ({len(extracted_urls)} items)")
        
        for i, url in enumerate(list(extracted_urls)):
            if i >= MAX_CASES: break
            print(f"[{i+1}/{len(extracted_urls)}]", end="")
            save_case_study(page, url)
            time.sleep(0.5)

        print(f"\n✨ Workflow Complete. Check {OUTPUT_DIR}/")
        browser.close()

if __name__ == "__main__":
    run_scraper()
