import csv
import requests
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
from urllib.parse import urljoin

BASE_URL = "https://www.bbc.com"

CATEGORIES = {
    "World": BASE_URL + "/news/world",
    "Business": BASE_URL + "/business",
    "Technology": BASE_URL + "/innovation/technology",
    "Science": BASE_URL + "/innovation/science"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

articles = []


for category, url in CATEGORIES.items():

    print("Scraping", category)

    try:
        page = requests.get(url, headers=HEADERS, timeout=15)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, "html.parser")

        headlines = soup.find_all(attrs={"data-testid": "card-headline"})

        if not headlines:
            headlines = soup.find_all(["h2", "h3"])

        seen = set()

        for tag in headlines:
            headline = tag.get_text(strip=True)

            if len(headline) < 15 or headline in seen:
                continue

            seen.add(headline)

            link_tag = tag.find_parent("a")
            link = urljoin(BASE_URL, link_tag["href"]) if link_tag and link_tag.get("href") else ""

            parent = tag
            date = datetime.now().strftime("%Y-%m-%d")

            for _ in range(5):
                if parent.parent is None:
                    break
                parent = parent.parent
                time_tag = parent.find("time")

                if time_tag:
                    date = time_tag.get("datetime") or time_tag.get_text(strip=True)
                    break

            articles.append([headline, date, category, link])

        print("Found", len(seen), "headlines")

    except requests.exceptions.RequestException as e:
        print("Error:", e)



if articles:
    with open("news_headlines.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Headline", "Date", "Category", "Link"])
        writer.writerows(articles)

    print("\nHeadlines saved successfully!")

    
    print("\n===== ANALYSIS =====")
    counts = Counter(article[2] for article in articles)

    for category, count in counts.items():
        print(category, ":", count)

    
    stop_words = {"the", "a", "an", "is", "in", "of", "to", "and", "for", "on", "with"}

    words = []

    for article in articles:
        for word in article[0].lower().split():
            word = word.strip(".,:;!?")
            if word.isalpha() and word not in stop_words:
                words.append(word)

    print("\nTop 10 Keywords:")

    for word, count in Counter(words).most_common(10):
        print(word, ":", count)

else:
    print("No headlines found. Check internet or BBC webpage structure.")
