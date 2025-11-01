from bs4 import BeautifulSoup
import requests

url = "https://www.bbc.co.uk/news/business"
headers = {"User-Agent": "Mozilla/5.0"}
html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, "html.parser")

articles = soup.find_all("article")

for a in articles[:5]:
    title = a.find("h2")
    date = a.find("time")
    if title:
        print("Headline:", title.get_text(strip=True))
    if date and date.has_attr("datetime"):
        print("Date:", date["datetime"])
    print()

print()