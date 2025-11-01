import json
from datetime import datetime
from collections import defaultdict
import csv

# Read the JSON file
print("Reading JSON file...")
with open('guardian_uk_economic_news_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} articles")

# Dictionary to store sentiment values by month-year
sentiment_by_month = defaultdict(list)

# Process each article
for article in data:
    # Extract date and convert to datetime
    date_str = article.get('date', '')
    if date_str:
        try:
            # Parse ISO format date
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Create month-year key
            month_year = dt.strftime('%Y-%m')
            
            # Get sentiment value
            sentiment = article.get('sentiment', 0)
            
            # Add to dictionary
            sentiment_by_month[month_year].append(sentiment)
        except (ValueError, AttributeError):
            continue

# Calculate average sentiment for each month-year
month_data = []
for month_year in sorted(sentiment_by_month.keys()):
    sentiments = sentiment_by_month[month_year]
    avg_sentiment = sum(sentiments) / len(sentiments)
    month_data.append({
        'month_year': month_year,
        'avg_sentiment': avg_sentiment
    })

# Write to CSV
output_file = 'guardian_sentiment_monthly.csv'
print(f"Writing {len(month_data)} monthly records to {output_file}...")

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['month_year', 'avg_sentiment'])
    writer.writeheader()
    writer.writerows(month_data)

print(f"Successfully created {output_file}")
print(f"Date range: {month_data[0]['month_year']} to {month_data[-1]['month_year']}")
