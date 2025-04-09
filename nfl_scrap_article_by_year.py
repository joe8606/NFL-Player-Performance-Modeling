import requests
import json
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

START_YEAR = 2025
END_YEAR = 2018
BASE_URL = "https://www.nfl.com"
LOG_PATH = "dat/scraper_log.txt"
ERROR_LOG_PATH = "dat/error_log.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

MAX_RETRIES = 3
RETRY_DELAY = 2
BATCH_SIZE = 100


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_date(text):
    try:
        return datetime.strptime(text.strip(), "%b %d, %Y")
    except:
        return None

def scrape_article_text(url):
    for attempt in range(MAX_RETRIES):
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code != 200:
                raise Exception(f"HTTP {res.status_code}")
            soup = BeautifulSoup(res.text, "html.parser")
            sections = soup.find_all("div", class_="d3-l-col__col-8")
            paragraphs = []
            for section in sections:
                ps = section.find_all("p")
                paragraphs.extend([p.text.strip() for p in ps if p.text.strip()])
            return "\n\n".join(paragraphs)
        except Exception as e:
            msg = f"⏳ Retry {attempt+1}/{MAX_RETRIES} for {url} due to error: {e}"
            print(msg)
            log_error(msg)
            time.sleep(RETRY_DELAY)
    fail_msg = f"❌ Failed to fetch after {MAX_RETRIES} retries: {url}"
    print(fail_msg)
    log_error(fail_msg)
    return ""

def log_message(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def log_error(message):
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def save_articles_batch(year, articles):
    filename = f"dat/nfl_news_{year}.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_urls = {item["url"] for item in existing}
    else:
        existing = []
        existing_urls = set()

    new_articles = [a for a in articles if a["url"] not in existing_urls]
    if new_articles:
        existing.extend(new_articles)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        for a in new_articles:
            log_message(f"✅ Article saved: {a['url']}")


def fetch_articles_by_year_range(start_year=2025, end_year=2018):
    driver = setup_driver()
    driver.get("https://www.nfl.com/news/all-news")
    print("📄 Starting scroll...")
    log_message(f"\n=== Scraping started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    seen = set()
    done = False
    article_buffer = {}

    while not done:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        blocks = soup.find_all("div", class_="d3-l-col__col-12")
        print(f"🔍 Loaded: {len(blocks)} article blocks")

        for block in blocks:
            a_tag = block.find("a", href=True)
            date_tag = block.find("p", class_="d3-o-media-object__date")
            if not a_tag or not date_tag:
                continue

            href = a_tag.get("href")
            if not href or href in seen:
                continue

            seen.add(href)
            date_obj = parse_date(date_tag.text)
            if not date_obj:
                continue

            year = date_obj.year
            if year < end_year:
                done = True
                break
            elif year > start_year:
                continue

            url = BASE_URL + href
            print(f"📌 {year} | {url}")
            log_message(f"{date_obj.strftime('%Y-%m-%d')} | {url}")
            content = scrape_article_text(url)
            article = {
                "url": url,
                "date": date_obj.strftime("%Y-%m-%d"),
                "content": content
            }

            ystr = str(year)
            if ystr not in article_buffer:
                article_buffer[ystr] = []
            article_buffer[ystr].append(article)

            if len(article_buffer[ystr]) >= BATCH_SIZE:
                save_articles_batch(ystr, article_buffer[ystr])
                article_buffer[ystr] = []

        if not done:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.execute_script("""
                    document.querySelectorAll('div[class*="sticky"], div[class*="overlay"], div[class*="container"]').forEach(el => el.remove());
                """)
                load_more_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Load More')]")
                driver.execute_script("arguments[0].scrollIntoView();", load_more_btn)
                load_more_btn.click()
                time.sleep(1)
            except (NoSuchElementException, ElementClickInterceptedException) as e:
                print(f"⚠️ Scroll ended due to: {e}")
                log_error(f"Scroll stopped due to: {e}")
                break

    # Save remaining articles
    for ystr, batch in article_buffer.items():
        if batch:
            save_articles_batch(ystr, batch)

    driver.quit()

if __name__ == "__main__":
    os.makedirs("dat", exist_ok=True)
    fetch_articles_by_year_range(START_YEAR, END_YEAR)