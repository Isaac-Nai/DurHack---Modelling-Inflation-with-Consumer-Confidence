import json
from datetime import datetime
from collections import defaultdict
import csv

# Read both JSON files and merge them
print("Reading JSON files...")
all_articles = []

# Load existing 2000_to_now data
try:
    with open('guardian_uk_economic_news_2000_to_now.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
        all_articles.extend(existing_data)
        print(f"Loaded {len(existing_data)} articles from guardian_uk_economic_news_2000_to_now.json")
except FileNotFoundError:
    print("guardian_uk_economic_news_2000_to_now.json not found, skipping...")

# Load new 2000-2003 data
try:
    with open('guardian_uk_economic_news_2000_to_2003.json', 'r', encoding='utf-8') as f:
        new_data = json.load(f)
        print(f"Loaded {len(new_data)} articles from guardian_uk_economic_news_2000_to_2003.json")
        
        # Remove duplicates based on URL
        existing_urls = {article.get('url', '') for article in all_articles}
        new_unique = [article for article in new_data if article.get('url', '') not in existing_urls]
        all_articles.extend(new_unique)
        print(f"Added {len(new_unique)} unique articles from 2000-2003 data")
except FileNotFoundError:
    print("guardian_uk_economic_news_2000_to_2003.json not found, skipping...")

print(f"\nTotal articles: {len(all_articles)}")

# Dictionary to store sentiment values by month-year
sentiment_by_month = defaultdict(list)

# Process each article
for article in all_articles:
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
month_data_dict = {}
for month_year in sentiment_by_month.keys():
    sentiments = sentiment_by_month[month_year]
    avg_sentiment = sum(sentiments) / len(sentiments)
    month_data_dict[month_year] = avg_sentiment

# Generate all months from 2000-01 to the last month in data
start_date = datetime(2000, 1, 1)
if month_data_dict:
    # Find the last month in the data
    last_month_str = max(month_data_dict.keys())
    last_date = datetime.strptime(last_month_str + '-01', '%Y-%m-%d')
else:
    last_date = datetime.now()

# Create complete month list from 2000-01 to last month
complete_month_data = []
current_date = start_date

while current_date <= last_date:
    month_year = current_date.strftime('%Y-%m')
    
    if month_year in month_data_dict:
        # Use actual data if available
        avg_sentiment = month_data_dict[month_year]
    else:
        # Fill missing months with None (will appear as empty in CSV or null in JSON)
        avg_sentiment = None
    
    complete_month_data.append({
        'month_year': month_year,
        'avg_sentiment': avg_sentiment
    })
    
    # Move to next month
    if current_date.month == 12:
        current_date = current_date.replace(year=current_date.year + 1, month=1)
    else:
        current_date = current_date.replace(month=current_date.month + 1)

print(f"\nGenerated {len(complete_month_data)} monthly records (including {len(complete_month_data) - len(month_data_dict)} missing months)")

# Write to CSV
csv_output_file = 'guardian_sentiment_monthly_2000_to_now.csv'
print(f"Writing to {csv_output_file}...")

with open(csv_output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['month_year', 'avg_sentiment'])
    writer.writeheader()
    for row in complete_month_data:
        # Convert None to empty string for CSV
        csv_row = {
            'month_year': row['month_year'],
            'avg_sentiment': '' if row['avg_sentiment'] is None else row['avg_sentiment']
        }
        writer.writerow(csv_row)

print(f"Successfully created {csv_output_file}")

# Write to JSON
json_output_file = 'guardian_sentiment_monthly_2000_to_now.json'
print(f"Writing to {json_output_file}...")

with open(json_output_file, 'w', encoding='utf-8') as f:
    json.dump(complete_month_data, f, ensure_ascii=False, indent=2)

print(f"Successfully created {json_output_file}")
print(f"\nDate range: {complete_month_data[0]['month_year']} to {complete_month_data[-1]['month_year']}")

# Show statistics for 2000-2003
months_2000_2003 = [m for m in complete_month_data if m['month_year'] >= '2000-01' and m['month_year'] < '2004-01']
filled_months = sum(1 for m in months_2000_2003 if m['avg_sentiment'] is not None)
missing_months = sum(1 for m in months_2000_2003 if m['avg_sentiment'] is None)
print(f"\n2000-2003 statistics:")
print(f"  Total months: {len(months_2000_2003)}")
print(f"  Months with data: {filled_months}")
print(f"  Missing months: {missing_months}")
