import pandas as pd
from datetime import datetime

# Read the CSV file
print("Reading CSV file...")
df = pd.read_csv('guardian_sentiment_monthly_2000_to_now.csv')

print(f"Loaded {len(df)} records")

# Convert month_year string to date
# Adding '-01' to make it a proper date (first day of the month)
print("Converting month_year to date format...")
df['date'] = pd.to_datetime(df['month_year'] + '-01', format='%Y-%m-%d')

# Option 1: Keep both columns (month_year as string and date as date)
# Option 2: Replace month_year with date - I'll do this and also keep month_year for reference
# Let's reorder columns: date, month_year, avg_sentiment
df = df[['date', 'month_year', 'avg_sentiment']]

# Save to CSV
output_file = 'guardian_sentiment_monthly_2000_to_now.csv'
print(f"Writing to {output_file}...")
df.to_csv(output_file, index=False, date_format='%Y-%m-%d')

print(f"Successfully updated {output_file}")
print(f"\nSample data:")
print(df.head(10))
print(f"\nData types:")
print(df.dtypes)
print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")

