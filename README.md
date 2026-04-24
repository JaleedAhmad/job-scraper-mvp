# Talent Radar: On-Demand Job Scraper (MVP)

A fully-functional, cache-driven job scraping application built specifically to source candidates on-demand while providing a seamless user experience. This MVP was designed as a rapid client demo, featuring a highly robust backend fallback system to bypass strict datacenter bot protections.

## 🚀 Tech Stack

*   **Backend Engine:** FastAPI (Python)
*   **Scraping Module:** Python Requests & Playwright Sync (Offline Sandbox Parsing)
*   **Anti-Bot API:** ZenRows Premium Residential Proxy network
*   **Data Processing:** Pandas & OpenPyXL
*   **Frontend UI:** HTML5, Vanilla JS (Fetch API), and Bootstrap 5 (Glassmorphism Custom CSS)

## 🏗️ Architecture & Logic Flow

This application is built with a **Cache-First Architecture** to maximize speed and bypass unnecessary web extraction. 

1.  **Incoming Request:** The user hits "Source Candidates" from the Frontend, sending a `GET` request to `/api/jobs` with `category` and `location` parameters.
2.  **Cache Assessment (Pandas):** The FastAPI backend intercepts the request and reads `jobs_cache.csv`. 
    *   **Cache Hit:** If identical data exists and was scraped within 24 hours, it translates the DataFrame into JSON and returns it near-instantly.
    *   **Cache Miss:** If no data exists (or the data is stale), it triggers the Playwright Engine.
3.  **Live Extraction via ZenRows:** To bypass aggressive Cloudflare protections and Just-A-Moment loops on cloud architectures, the scraper hits the **ZenRows API** natively using `requests`. ZenRows utilizes premium residential proxies and manages JS-rendering remotely, returning the fully hydrated DOM.
4.  **Offline Playwright Parsing:** To prevent Indeed's embedded Cross-Origin React rules from breaking the layout, the extracted ZenRows HTML is injected directly into an offline Playwright Sandbox via `page.set_content()`. Playwright instantly parses the DOM entirely offline and retrieves the nested elements reliably.
4.  **Local Persistence:** The newly generated/scraped data is concatenated into the Pandas DataFrame and permanently saved to `jobs_cache.csv`. 
5.  **Export:** Hitting `/api/download` converts the cached DataFrame into a `.xlsx` binary and triggers a native browser download.

## 🔑 Environment Variables

This app relies on the **ZenRows Premium Proxy API** to securely navigate Cloudflare anti-bot systems. You must configure this key for the app to scrape LIVE data successfully.

1.  Sign up at [ZenRows](https://www.zenrows.com/) and grab an API Key.
2.  Create a `.env` file in the root directory:
    ```env
    ZENROWS_KEY=your_api_key_here
    ```
*(Note: As per best practices, `.env` is listed in your `.gitignore` and won't be pushed to the repository).*

## 💻 Local Setup & Execution

1. **Create and Activate a Virtual Environment:**
   *(Cross-platform support ensures this runs anywhere.)*
   
   **Linux / macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Windows (PowerShell/CMD):**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install Core Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Headless Browsers (Critical for Playwright):**
   ```bash
   playwright install chromium
   ```

4. **Boot the FastAPI Server:**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
5. **View App:** Navigate to `http://127.0.0.1:8000` in your browser.

## ☁️ Deployment (Render Free Tier)

This application is bundled directly so the FastAPI backend acts as the HTML web-host. It can be easily deployed as a single Web Service on Render.

1. Connect this GitHub Repository inside Render and select **New Web Service**.
2. **Environment:** `Python 3`
3. **Build Command:** 
   ```bash
   pip install -r requirements.txt && playwright install chromium
   ```
   *(Render natively handles the system graphics dependencies).*
4. **Start Command:** 
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
