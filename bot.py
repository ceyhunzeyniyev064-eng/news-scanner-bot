bot.py
import os
import json
import time
import hashlib
import requests
import feedparser

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STATE_FILE = "seen.json"

RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.marketwatch.com/rss/topstories",
    "https://www.prnewswire.com/rss/all-news-releases-news.xml",
]

POSITIVE_KEYS = [
    "beats", "beat estimates", "raises guidance",
    "upgraded", "price target raised",
    "fda approval", "approved",
    "contract", "award",
    "buyback", "acquisition", "merger",
    "surges", "jumps", "soars"
]

NEGATIVE_KEYS = [
    "misses", "cuts guidance", "downgrade",
    "lawsuit", "bankruptcy", "investigation"
]

def load_seen():
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen), f)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def make_id(title, link):
    return hashlib.sha256((title + link).encode()).hexdigest()

def looks_positive(text):
    text = text.lower()
    for n in NEGATIVE_KEYS:
        if n in text:
            return False
    for p in POSITIVE_KEYS:
        if p in text:
            return True
    return False

def run():
    seen = load_seen()
    new_hits = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:30]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            sid = make_id(title, link)

            if sid in seen:
                continue

            seen.add(sid)

            if looks_positive(title):
                new_hits.append((title, link))

    if new_hits:
        message = "🚀 POSITIVE STOCK NEWS:\n\n"
        for title, link in new_hits:
            message += f"• {title}\n{link}\n\n"
        send_telegram(message)

    save_seen(seen)

if __name__ == "__main__":
    run()
