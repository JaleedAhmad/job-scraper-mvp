import os
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from scraper import scrape_indeed_jobs

app = FastAPI(title="Job Scraper MVP")

CACHE_FILE = "jobs_cache.csv"

def load_cache() -> pd.DataFrame:
    """Helper to load the CSV cache. Returns an empty DataFrame if it doesn't exist."""
    if os.path.exists(CACHE_FILE):
        return pd.read_csv(CACHE_FILE)
    else:
        # Create an empty dataframe with our expected columns
        return pd.DataFrame(columns=["Title", "Company", "Location", "Link", "Category", "SearchLocation", "ScrapedAt"])

def save_cache(df: pd.DataFrame):
    """Helper to save the dataframe back to the CSV."""
    df.to_csv(CACHE_FILE, index=False)

@app.get("/")
def serve_frontend():
    """Serves the main HTML file."""
    return FileResponse("index.html")

@app.get("/script.js")
def serve_js():
    """Serves the Vanilla JS file."""
    return FileResponse("script.js")

@app.get("/api/jobs")
def get_jobs(category: str, location: str = ""):
    """
    Checks the cache for the requested category & location.
    If cached data is < 24 hours old, return it instantly.
    Otherwise, trigger the Playwright scraper, update the cache, and return.
    """
    df = load_cache()
    
    # 1. Filter cache for the requested category and location
    cached_category = df[(df["Category"] == category) & (df["SearchLocation"] == location)]
    
    if not cached_category.empty:
        # Check if the data is fresh (less than 24 hours old)
        # Assuming ScrapedAt is stored as ISO format string
        last_scraped_str = cached_category.iloc[0]["ScrapedAt"]
        last_scraped = datetime.fromisoformat(last_scraped_str)
        
        hours_diff = (datetime.now() - last_scraped).total_seconds() / 3600
        
        if hours_diff < 24:
            print(f"CACHE HIT: Serving '{category}' from cache (Age: {hours_diff:.2f} hours)")
            # Return records as a list of dictionaries for JSON translation
            return {"source": "cache", "data": cached_category.to_dict(orient="records")}
            
    # 2. Cache Miss or Stale Data -> Scrape live
    print(f"CACHE MISS/STALE: Scraping Indeed live for '{category}' in '{location}'...")
    scraped_data = scrape_indeed_jobs(category, location)
    
    if not scraped_data:
        # If scraper failed or found nothing, return an error or empty list
        return {"source": "live", "data": []}
        
    # Transform scraped list of dicts to a DataFrame
    new_df = pd.DataFrame(scraped_data)
    new_df["Category"] = category
    new_df["SearchLocation"] = location
    new_df["ScrapedAt"] = datetime.now().isoformat()
    
    # Remove old rows for this exact category + location before appending the new ones
    if not df.empty:
        df = df[~((df["Category"] == category) & (df["SearchLocation"] == location))]
        
    # Append the fresh scraped data to the overall cache
    updated_df = pd.concat([df, new_df], ignore_index=True)
    save_cache(updated_df)
    
    return {"source": "live", "data": new_df.to_dict(orient="records")}

@app.get("/api/download")
def download_excel(category: str, location: str = ""):
    """
    Reads the cached CSV, filters by category and location, generates an Excel file,
    and forces a file download in the browser.
    """
    df = load_cache()
    cached_category = df[(df["Category"] == category) & (df["SearchLocation"] == location)]
    
    if cached_category.empty:
        raise HTTPException(status_code=404, detail="No cached data available to download. Please search first.")
        
    excel_filename = f"{category.replace(' ', '_')}_Jobs.xlsx"
    
    # Using Pandas to create an Excel file on the fly
    cached_category.to_excel(excel_filename, index=False, columns=["Title", "Company", "Location", "Link"])
    
    # Determine the response to return the file as an attachment
    return FileResponse(
        path=excel_filename, 
        filename=excel_filename, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        background=None # Ideally, we'd clean up the file afterwards using background tasks, but fine for MVP
    )
