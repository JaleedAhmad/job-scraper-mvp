from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    page = context.new_page()
    page.goto('https://www.indeed.com/jobs?q=DevOps')
    time.sleep(3)
    print("Title:", page.title())
    print("Beacon count:", page.locator('.job_seen_beacon').count())
    print("Card count:", page.locator('.slider_container').count())
    browser.close()
