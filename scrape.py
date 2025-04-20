# NOTE:
# The scrape.py file is intended for informational purposes

# Manual data cleansing was necessary in Excel as there are lot of players that do not have a bio and/or a grade
# The complete, clean dataset is available under data/player_bios.csv


# Dependencies
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up Splinter
service = Service(ChromeDriverManager().install())

# Optional: Add Chrome options
options = webdriver.ChromeOptions()
options.headless = False  # Set to True if you want headless mode
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')


# Initialize Splinter browser with Selenium WebDriver backend
browser = Browser('chrome', service=service, options=options)

# Initialize the lists to hold player names and links

player_link_name_2023 = []
player_links_2023 = []
player_names_2023 = []

for x in range(1, 26):
    url = f'https://www.nfl.com/draft/tracker/prospects/all-positions/all-colleges/all-statuses/2023?page={x}'
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    player_link_name = soup.find_all('a', class_='css-1mchkr3')
    for link in player_link_name:
        player_links_2023.append(link['href'])
    for name in player_link_name:
        player_names_2023.append(name.text)

player_link_name_2024 = []
player_links_2024 = []
player_names_2024 = []

for x in range(1, 25):
    url = f'https://www.nfl.com/draft/tracker/prospects/all-positions/all-colleges/all-statuses/2024?page={x}'
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    player_link_name = soup.find_all('a', class_='css-1mchkr3')
    for link in player_link_name:
        player_links_2024.append(link['href'])
    for name in player_link_name:
        player_names_2024.append(name.text)

player_link_name_2025 = []
player_links_2025 = []
player_names_2025 = []

for x in range(1, 23):
    url = f'https://www.nfl.com/draft/tracker/prospects/all-positions/all-colleges/all-statuses/2025?page={x}'
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    player_link_name = soup.find_all('a', class_='css-1mchkr3')
    for link in player_link_name:
        player_links_2025.append(link['href'])
    for name in player_link_name:
        player_names_2025.append(name.text)

# Join all the link lists into one list
player_links = player_links_2023 + player_links_2024 + player_links_2025

# Join all the name lists into one list
player_names =  player_names_2023 + player_names_2024 + player_names_2025

# Create a dataframe
df = pd.DataFrame({'Player': player_names, 'Link': player_links})

# Remove duplicates
df = df.drop_duplicates(subset=['Player'], keep='first')

# Initialize lists to hold the data
player_bios = []
player_grades = []
draft_projection = []

# Loop through the links and scrape the data, should take about 6 hours to run
for index, row in df.iterrows():
    url = row['Link']
    browser.visit(url)
    time.sleep(5)
    html = browser.html
    soup = bs(html, 'html.parser')
    try:
        # Append the player's bio to the dataframe
        player_bio = soup.find('div', class_='player-bio').text
        
    except AttributeError:
        player_bios.append('NA')
        player_grades.append('NA')
        draft_projection.append('NA')
    

df['Player Bio'] = player_bios
df['Player Grade'] = player_grades
df['Draft Projection'] = draft_projection
df.to_csv('scraped-prospect-data.csv')