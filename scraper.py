import time
import urllib.parse
from playwright.sync_api import sync_playwright

def scrape_indeed_jobs(category: str) -> list:
    """
    Scrapes the first page of Indeed for a specific job category.
    Includes memory optimizations for running on tiny instances like Render Free Tier.
    """
    results = []
    
    # URL encode the category for the query string
    query = urllib.parse.quote(category)
    url = f"https://www.indeed.com/jobs?q={query}"

    with sync_playwright() as p:
        # Launch headless browser. 
        # Added flags specifically help prevent crashes in Docker/Render Free Tier environments
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-dev-shm-usage', # Prevent shared memory issues
                '--no-sandbox',            # Bypass OS security model
                '--disable-gpu',           # Not needed for headless UI
                '--disable-extensions'     # Save memory
            ]
        )
        
        # Set a realistic user agent to help minimize bot detection
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Block images and stylesheets to save bandwidth and memory!
        context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "media", "font"] else route.continue_())

        page = context.new_page()
        
        try:
            # Navigate to Indeed. Timeout set to 30s.
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # Wait for job cards to load on Indeed (typically grouped under 'td.resultContent' or '.job_seen_beacon')
            # If Indeed detects a bot, Cloudflare might block this, so we add a timeout.
            page.wait_for_selector(".job_seen_beacon", timeout=10000)
            
            # Fetch all job cards on the page
            job_cards = page.locator(".job_seen_beacon").all()
            
            # Extract data for the first 10-15 results
            for card in job_cards[:15]:
                # Title usually sits inside an h2 -> a
                title_locator = card.locator("h2.jobTitle span").first
                title = title_locator.inner_text().strip() if title_locator.count() > 0 else "Unknown Title"
                
                company_locator = card.locator("[data-testid='company-name']").first
                company = company_locator.inner_text().strip() if company_locator.count() > 0 else "Unknown Company"
                
                location_locator = card.locator("[data-testid='text-location']").first
                location = location_locator.inner_text().strip() if location_locator.count() > 0 else "Unknown Location"
                
                # Get the relative link and absolute it
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
    # Test the scraper locally when running this file directly
    print("Testing scraper locally...")
    jobs = scrape_indeed_jobs("DevOps Engineer")
    for j in jobs:
        print(j)
    print(f"Total found: {len(jobs)}")
