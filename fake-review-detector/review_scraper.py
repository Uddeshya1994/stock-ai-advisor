import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_asin(url):
    import re
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    return match.group(1) if match else None

def fetch_reviews(asin):
    url = f"https://www.amazon.in/product-reviews/{asin}"
    response = requests.get(url, headers=HEADERS, timeout=10)

    soup = BeautifulSoup(response.text, "html.parser")
    reviews = []

    for block in soup.select(".review-text-content span"):
        text = block.get_text(strip=True)
        if len(text) > 20:
            reviews.append(text)

    return reviews[:20]  # limit to avoid blocking
