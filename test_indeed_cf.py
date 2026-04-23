from playwright.sync_api import sync_playwright
import time

def test_scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled', 
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            viewport={"width": 1920, "height": 1080}
        )
        # ONLY block images and media. Allow stylesheets, scripts, fonts!
        context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media"] else route.continue_())
        
        page = context.new_page()
        page.goto('https://www.indeed.com/jobs?q=DevOps', timeout=30000, wait_until="domcontentloaded")
        
        print("Initial Title:", page.title())
        # give it time to solve the cloudflare challenge
        time.sleep(5)
        print("Title after 5s:", page.title())
        print("Beacon count:", page.locator('.job_seen_beacon').count())
        browser.close()

test_scrape()
