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

BASE_URL = "https://www.nfl.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}
LINKS_PATH = "dat/nfl_news_links_2025_to_2018.json"
LOG_PATH = "dat/link_scraper_log.txt"
CHECKPOINT_PATH = "dat/link_scraper_checkpoint.txt"

BATCH_SIZE = 100
link_batch = []

# === Phase 1: Collect all article links and dates ===
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_date(text):
    try:
        return datetime.strptime(text.strip(), "%b %d, %Y")
    except:
        return None

def log_message(message):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_existing_links():
    if os.path.exists(LINKS_PATH):
        with open(LINKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_checkpoint(last_url):
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        f.write(last_url)

def flush_batch():
    global link_batch
    if not link_batch:
        return
    if os.path.exists(LINKS_PATH):
        with open(LINKS_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.extend(link_batch)
    with open(LINKS_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    print(f"💾 Flushed {len(link_batch)} links to file.")
    log_message(f"💾 Flushed {len(link_batch)} links to file.")
    link_batch = []

def collect_article_links(start_year=2025, end_year=2018):
    global link_batch
    driver = setup_driver()
    driver.get("https://www.nfl.com/news/all-news")
    print("📄 Scrolling and collecting links...")
    log_message(f"\n=== Scraping started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    seen = set()
    existing = load_existing_links()
    for item in existing:
        seen.add(item["url"])

    last_checkpoint = load_checkpoint()
    checkpoint_found = last_checkpoint is None
    done = False

    while not done:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        blocks = soup.find_all("div", class_="d3-l-col__col-12")
        print(f"🔍 Loaded: {len(blocks)} blocks")

        for block in blocks:
            a_tag = block.find("a", href=True)
            date_tag = block.find("p", class_="d3-o-media-object__date")
            if not a_tag or not date_tag:
                continue

            href = a_tag.get("href")
            full_url = BASE_URL + href

            if not href or full_url in seen:
                continue

            if not checkpoint_found:
                if href == last_checkpoint:
                    checkpoint_found = True
                continue

            date_obj = parse_date(date_tag.text)
            if not date_obj:
                continue
            year = date_obj.year
            if year < end_year:
                done = True
                break
            elif year > start_year:
                continue

            seen.add(full_url)
            new_entry = {"url": full_url, "date": date_obj.strftime("%Y-%m-%d")}
            link_batch.append(new_entry)
            log_message(f"🆕 {date_obj.strftime('%Y-%m-%d')} | {full_url}")
            save_checkpoint(href)

            if len(link_batch) >= BATCH_SIZE:
                flush_batch()

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
                log_message(f"⚠️ Scroll ended due to: {e}")
                break

    driver.quit()
    flush_batch()
    print(f"✅ Finished run. Total seen: {len(seen)}")
    log_message(f"✅ Finished run. Total seen: {len(seen)}")

if __name__ == "__main__":
    os.makedirs("dat", exist_ok=True)
    collect_article_links(2025, 2018)
