from textblob import TextBlob
from collections import Counter

GENERIC_PHRASES = ["nice product", "good product", "value for money", "awesome"]

def analyze_reviews(reviews):
    fake = 0
    genuine = 0
    suspicious = 0

    phrase_counter = Counter()

    for review in reviews:
        lower = review.lower()
        polarity = TextBlob(review).sentiment.polarity

        if len(review.split()) < 6 and polarity > 0.5:
            fake += 1
        elif any(p in lower for p in GENERIC_PHRASES):
            suspicious += 1
        elif abs(polarity) > 0.8:
            suspicious += 1
        else:
            genuine += 1

        phrase_counter.update(lower.split())

    total = len(reviews)

    return {
        "total": total,
        "fake": fake,
        "suspicious": suspicious,
        "genuine": genuine,
        "common_words": phrase_counter.most_common(5)
    }
