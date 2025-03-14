import os
import requests
from bs4 import BeautifulSoup
import time

# 1️⃣ Step 1: Retrieve all news article links from "https://www.nfl.com/news/all-news"
base_url = "https://www.nfl.com"
news_page = "/news/all-news"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Set the save path
save_path = r"C:\rutgers\Data mining\project\nfl_news_articles.txt"

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Send request to fetch the news page
response = requests.get(base_url + news_page, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <a> tags within class="d3-l-col__col-12"
    news_links = soup.find_all("a", class_="d3-o-media-object d3-o-media-object--horizontal d3-o-content-tray__text-thumb nfl-o-cta--whole-area")

    article_urls = []
    for link in news_links:
        href = link.get("href")
        if href:
            full_url = base_url + href  # Construct the full article URL
            article_urls.append(full_url)

    print(f"Found {len(article_urls)} articles.")  # Display the number of articles found
else:
    print("Failed to retrieve the news page. Status Code:", response.status_code)
    exit()

# 2️⃣ Step 2: Scrape the content of each news article
def scrape_article(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate div elements with class="d3-l-col__col-8" that contain `nfl-c-article__container`
        article_sections = soup.find_all("div", class_="d3-l-col__col-8")

        full_article_text = []  # Store the article content

        for section in article_sections:
            # Find all div elements with class="nfl-c-article__container"
            article_containers = section.find_all("div", class_="nfl-c-article__container")

            for container in article_containers:
                # Extract all <p> tag content
                paragraphs = [p.text.strip() for p in container.find_all("p")]
                full_article_text.extend(paragraphs)

        # Merge and clean up the extracted text
        article_content = "\n\n".join(full_article_text)
        return article_content
    else:
        print(f"Failed to retrieve article: {url}")
        return None

# 3️⃣ Step 3: Download all news articles
all_articles = {}
for idx, url in enumerate(article_urls):
    print(f"Scraping article {idx+1}/{len(article_urls)}: {url}")
    article_text = scrape_article(url)
    if article_text:
        all_articles[url] = article_text

    time.sleep(1)  # Prevent excessive requests from being blocked

# 4️⃣ Step 4: Save the articles to `C:\rutgers\Data mining\project\nfl_news_articles.txt`
with open(save_path, "w", encoding="utf-8") as f:
    for url, content in all_articles.items():
        f.write(f"URL: {url}\n")
        f.write(content + "\n\n" + "="*80 + "\n\n")

print(f"All articles have been saved to {save_path}")
