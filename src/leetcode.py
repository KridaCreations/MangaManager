import requests
from bs4 import BeautifulSoup
import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Base URL for the ranking page
BASE_URL = "https://leetcode.com/contest/api/ranking/weekly-contest-452/?region=global&pagination=1"

# Enhanced headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://leetcode.com/contest/weekly-contest-447/",
    "DNT": "1",
}

# Optional: Add cookies from browser (inspect incognito session)
COOKIES = {
    # Example: "csrftoken": "your_csrf_token", "LEETCODE_SESSION": "your_session_token"
    # Get from browser: Developer Tools > Application > Cookies
}

def scrape_ranking_page_requests(page=1):
    """Scrape a single page using requests and BeautifulSoup."""
    url = f"{BASE_URL}&page={page}" if page > 1 else BASE_URL
    try:
        session = requests.Session()
        if COOKIES:
            for name, value in COOKIES.items():
                session.cookies.set(name, value)
        
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the ranking table (update class after inspecting page)
        table = soup.find("table")  # Replace with e.g., "table", class_="ranking-table"
        if not table:
            print(f"No table found on page {page} with requests. Page may be JavaScript-rendered.")
            return None
        
        rankings = []
        for row in table.find_all("tr")[1:]:  # Skip header
            cols = row.find_all("td")
            if len(cols) >= 4:  # Adjust based on columns
                rank = cols[0].text.strip()
                username = cols[1].text.strip()
                score = cols[2].text.strip()
                time = cols[3].text.strip()
                rankings.append({
                    "rank": rank,
                    "username": username,
                    "score": score,
                    "time": time
                })
        
        print(f"Scraped {len(rankings)} rankings from page {page} with requests")
        return rankings
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error scraping page {page}: {e}")
        return None
    except Exception as e:
        print(f"Error scraping page {page} with requests: {e}")
        return None

def scrape_ranking_page_selenium(page=1):
    """Scrape a single page using Selenium."""
    url = f"{BASE_URL}&page={page}" if page > 1 else BASE_URL
    try:
        # Set up headless Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-agent={HEADERS['User-Agent']}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Load page
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load
        
        # Parse HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        
        # Find the table
        table = soup.find("table")  # Update class
        if not table:
            print(f"No table found on page {page} with Selenium.")
            return []
        
        rankings = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 4:
                rank = cols[0].text.strip()
                username = cols[1].text.strip()
                score = cols[2].text.strip()
                time = cols[3].text.strip()
                rankings.append({
                    "rank": rank,
                    "username": username,
                    "score": score,
                    "time": time
                })
        
        print(f"Scraped {len(rankings)} rankings from page {page} with Selenium")
        return rankings
    except Exception as e:
        print(f"Error scraping page {page} with Selenium: {e}")
        return []

def scrape_all_rankings(max_pages=5):
    """Scrape rankings across multiple pages."""
    all_rankings = []
    page = 1
    
    while page <= max_pages:
        # Try requests first
        rankings = scrape_ranking_page_requests(page)
        
        # Fallback to Selenium
        if rankings is None:
            print(f"Switching to Selenium for page {page}")
            rankings = scrape_ranking_page_selenium(page)
        
        if not rankings:
            print(f"No more rankings on page {page}. Stopping.")
            break
        
        all_rankings.extend(rankings)
        page += 1
        time.sleep(3)  # Increased delay to avoid rate limiting
    
    return all_rankings

def main():
    # Verify URL accessibility
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print("URL is accessible. Proceeding with scraping.")
    except requests.exceptions.HTTPError as e:
        print(f"Cannot access URL: {e}. Check if the contest page exists or requires login.")
        return
    
    # Scrape rankings
    rankings = scrape_all_rankings(max_pages=5)
    
    # Save to JSON
    if rankings:
        with open("leetcode_rankings.json", "w") as f:
            json.dump(rankings, f, indent=4)
        print(f"Saved {len(rankings)} rankings to leetcode_rankings.json")
    else:
        print("No rankings scraped. Check page structure, use Selenium, or verify URL.")

if __name__ == "__main__":
    main()