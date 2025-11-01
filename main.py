import requests
import json
from datetime import datetime, timedelta
import time
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')




# Your Guardian API key
API_KEY = "479213d4-f49c-4a0b-8cd2-cd248972fb6d"

# Keywords to track
keywords = [
    "inflation",
    "mortgage",
    "housing",
    "unemployment",
    "cost of living",
    "economy"
]

# Date range (example: last 30 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

all_articles = []

print("Fetching UK economic news from The Guardian API...\n")

for keyword in keywords:
    print(f"Searching for keyword: {keyword}")
    
    page = 1
    page_size = 50  # Max per page
    total_pages = 1  # initial placeholder
    
    while page <= total_pages:
        url = (
            f"https://content.guardianapis.com/search?"
            f"q={keyword}&"
            f"from-date={start_date_str}&to-date={end_date_str}&"
            f"section=business|uk-news&"
            f"page-size={page_size}&page={page}&"
            f"api-key={API_KEY}"
        )
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break
        
        data = response.json()
        results = data.get('response', {})
        
        total_pages = results.get('pages', 1)
        articles = results.get('results', [])
        
        for article in articles:
            all_articles.append({
                "keyword": keyword,
                "title": article.get('webTitle'),
                "section": article.get('sectionName'),
                "date": article.get('webPublicationDate'),
                "url": article.get('webUrl')
            })
        
        page += 1
        time.sleep(1)  # polite delay to avoid hitting rate limits
    
    print(f"Found {len(articles)} articles for keyword '{keyword}'\n")

print("\nTotal articles fetched:", len(all_articles))

# Optional: save to JSON or CSV
with open("guardian_uk_economic_news.json", "w", encoding="utf-8") as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=4)

print("Saved articles to guardian_uk_economic_news.json")


url = article['url']
sia = SentimentIntensityAnalyzer()


for article in all_articles:
    headline = article['title']
    score = sia.polarity_scores(headline)
    article['sentiment'] = score['compound']  # -1 to 1


