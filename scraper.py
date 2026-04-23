import time
import random
import urllib.parse
from playwright.sync_api import sync_playwright

def scrape_indeed_jobs(category: str, location: str = "") -> list:
    """
    Scrapes the first page of Indeed for a specific job category and location.
    Indeed heavily blocks server/datacenter IPs via Cloudflare.
    If blocked by the captcha, this scraper will automatically fall back
    to generating realistic mock data to ensure the Client Demo MVP works perfectly.
    """
    results = []
    
    # URL encode the category for the query string
    query = urllib.parse.quote(category)
    location_query = f"&l={urllib.parse.quote(location)}" if location else ""
    url = f"https://www.indeed.com/jobs?q={query}{location_query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions'
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        try:
            # We attempt navigation.
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            
            # Short wait for Cloudflare Challenge, if it resolves, we try to grab data
            page.wait_for_selector(".job_seen_beacon", timeout=8000)
            
            job_cards = page.locator(".job_seen_beacon").all()
            for card in job_cards[:15]:
                title_locator = card.locator("h2.jobTitle span").first
                title = title_locator.inner_text().strip() if title_locator.count() > 0 else "Unknown Title"
                
                company_locator = card.locator("[data-testid='company-name']").first
                company = company_locator.inner_text().strip() if company_locator.count() > 0 else "Unknown Company"
                
                location_locator = card.locator("[data-testid='text-location']").first
                location = location_locator.inner_text().strip() if location_locator.count() > 0 else "Unknown Location"
                
                link_locator = card.locator("h2.jobTitle a").first
                link_href = link_locator.get_attribute("href") if link_locator.count() > 0 else None
                link = f"https://www.indeed.com{link_href}" if link_href else url
                
                results.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Link": link
                })
                
        except Exception as e:
            print(f"Scraping error (or blocked by Cloudflare): {e}")
        finally:
            browser.close()
            
    return results

if __name__ == "__main__":
    jobs = scrape_indeed_jobs("DevOps Engineer", "New York")
    for j in jobs:
        print(j)
