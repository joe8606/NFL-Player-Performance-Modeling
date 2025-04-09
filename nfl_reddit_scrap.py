import os
import json
from datetime import datetime, timezone
import praw

# 初始化 Reddit client
reddit = praw.Reddit(
    client_id="你的 client_id",
    client_secret="你的 client_secret",
    user_agent="nfl_reddit_scraper by /u/your_username"
)

output_path = "dat/reddit_nfl_top_2023.json"
os.makedirs("dat", exist_ok=True)

print("🔍 Fetching top posts from r/nfl in 2023...")

subreddit = reddit.subreddit("nfl")
results = []

for submission in subreddit.top(time_filter='year', limit=1000):
    created_year = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).year
    if created_year != 2023:
        continue

    # 抓取留言
    submission.comments.replace_more(limit=0)  # 移除「更多留言」
    top_comments = [comment.body for comment in submission.comments[:5]]  # 抓前 5 則留言內容

    results.append({
        "title": submission.title,
        "score": submission.score,
        "url": submission.url,
        "permalink": f"https://reddit.com{submission.permalink}",
        "created_utc": submission.created_utc,
        "num_comments": submission.num_comments,
        "id": submission.id,
        "top_comments": top_comments
    })

print(f"✅ Collected {len(results)} posts")

# 存成 JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"💾 Saved to {output_path}")
