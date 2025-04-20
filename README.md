README
The purpose of this repository is for Rutgers Data Mining final project.
Group 1: Andy Li, Joe Lin, Chen Yang

Important files:
Data mining workflow.pdf - Initial workflow of project

nfl_players_data.R - Retrieval of NFL player positions data QB, RB, WR/TE from NFLFastR package.
  qb_stats.csv - Quarterback stats
  rb_stats.csv - Runningback stats
  wrte_stats.csv - Wide Receiver/Tight End stats

nfl_scraper_functions.py - Web scraping functions for retrieving player statistics from NFL.com
nfl_scraper.py - Calling nfl_scraper_functions.py to fetch player stats.
  dat folder - Contains scraped player data
  
scrape.py - Scraper for NFL.com prospect player bio and grades.
  scraped-prospect-data.csv - data from scrape.py. Contains prospect player bios used for sentiment analysis, and player grade.
  
sentiment.ipynb - Sentiment analysis using Bert Base Multilingual Uncased LLM
  Player Bio and Grade with Sentiment.csv - NFL player bio and grade data with sentiment scores from LLM

QB RB WRTE Models.ipynb - Majority of analysis, EDA, EPA prediction using Random Forest, XGBoost models.

  
