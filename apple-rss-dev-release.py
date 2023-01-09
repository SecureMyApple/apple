# A SIMPLE SCRIPT TO TABULATE THE RSS FEED FOR APPLE DEV AND PRODUCE A SUMMARY TABLE
# CREATED 09JAN23

import feedparser
import re
from tabulate import tabulate

# URL OF APPLE DEV RSS [BEST URL I COULD FIND FOR UPDATES]
feed_url = "feed://developer.apple.com/news/releases/rss/releases.rss"

# SEARCH TERMS
patterns = {
    "iphone": r"iPhone",
    "ipad": r"iPad",
    "iwatch": r"iWatch",
    "macos": r"macOS",
}

# PARSE
feed = feedparser.parse(feed_url)

# CREATE A LIST
rows = []

for item in feed.entries:
    # RIP TITLE, LINK AND DATE
    title = item.title
    link = item.link
    date = item.published
   
    for product, pattern in patterns.items():
        
        if re.search(pattern, title, re.IGNORECASE):
            rows.append((product, title, link, date))
            break

# PRINT
print(tabulate(rows, headers=["Product", "Title", "Link", "Date"], tablefmt="grid"))
