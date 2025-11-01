import json
from datetime import datetime

# Read the JSON file
print("Reading JSON file...")
with open('guardian_sentiment_monthly_2000_to_now.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} records")

# Convert month_year to date format
print("Adding date field...")
for record in data:
    if record.get('month_year'):
        # Convert "2000-01" to "2000-01-01" (first day of the month)
        month_year = record['month_year']
        date_str = month_year + '-01'
        record['date'] = date_str
        # Keep month_year as well for reference

# Save updated JSON
output_file = 'guardian_sentiment_monthly_2000_to_now.json'
print(f"Writing to {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully updated {output_file}")
print(f"\nSample record:")
print(json.dumps(data[0], indent=2))

