
from calendar import month
import requests
import json
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
import pandas as pd
import matplotlib.pyplot as plt

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
start_date = end_date - timedelta(days=365)
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

all_articles = []
sia = SentimentIntensityAnalyzer()

print("Fetching UK economic news from The Guardian API...\n")

for keyword in keywords:
    print(f"Searching for keyword: {keyword}")
    
    page = 1
    page_size = 50
    total_pages = 1
    
    while page <= total_pages:
        url = (
            f"https://content.guardianapis.com/search?"
            f"q={keyword}&"
            f"from-date={start_date_str}&to-date={end_date_str}&"
            f"section=business|uk-news&"
            f"show-fields=body&"
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
            # Extract full HTML body
            body_html = article.get('fields', {}).get('body', '')
            
            # Clean HTML to plain text
            soup = BeautifulSoup(body_html, 'html.parser')
            body_text = soup.get_text(separator=' ', strip=True)
            
            # Sentiment analysis
            sentiment_score = sia.polarity_scores(body_text)['compound']
            
            all_articles.append({
                "keyword": keyword,
                "title": article.get('webTitle'),
                "section": article.get('sectionName'),
                "date": article.get('webPublicationDate'),
                "url": article.get('webUrl'),
                "body": body_text,
                "sentiment": sentiment_score
            })
        
        page += 1
        time.sleep(1)  # be polite
    
    print(f"Fetched {len(articles)} articles for keyword '{keyword}'\n")

print("\nTotal articles fetched:", len(all_articles))

# Optional: save to JSON
with open("guardian_uk_economic_news_full.json", "w", encoding="utf-8") as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=4)

print("Saved articles to guardian_uk_economic_news_full.json")

df = pd.DataFrame(all_articles)

# Ensure 'date' is datetime
df['date'] = pd.to_datetime(df['date'])

# Extract year-month for grouping
df['year_month'] = df['date'].dt.to_period('M')

# Group by month and calculate average sentiment
monthly_sentiment = df.groupby('year_month')['sentiment'].mean().reset_index()
monthly_sentiment['year_month'] = monthly_sentiment['year_month'].dt.to_timestamp()

print("\nAverage sentiment per month:")
print(monthly_sentiment)

# Plotting
plt.figure(figsize=(12,6))
plt.plot(monthly_sentiment['year_month'], monthly_sentiment['sentiment'], marker='o')
plt.title('Average Sentiment of UK Economic News Over Time')
plt.xlabel('Month')
plt.ylabel('Average Sentiment (-1 = negative, 1 = positive)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show(block=True)

