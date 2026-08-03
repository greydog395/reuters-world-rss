import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime, timezone
from email.utils import format_datetime
import re


BASE = "https://www.reuters.com"

SOURCE = "https://www.reuters.com/world/"


MAX_ARTICLES = 50


headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/120 Safari/537.36"
    )
}


feed = FeedGenerator()

feed.title(
    "Reuters World News"
)

feed.link(
    href=SOURCE
)

feed.description(
    "Latest world news from Reuters"
)

feed.language(
    "en"
)


response = requests.get(
    SOURCE,
    headers=headers,
    timeout=30
)

response.raise_for_status()


soup = BeautifulSoup(
    response.text,
    "html.parser"
)


articles = []

seen = set()


for a in soup.find_all("a", href=True):

    href = a["href"]

    if "/world/" not in href:
        continue

    if href.startswith("/"):
        href = urljoin(
            BASE,
            href
        )

    if href in seen:
        continue

    seen.add(href)

    title = a.get_text(
        " ",
        strip=True
    )

    if len(title) < 20:
        continue

    articles.append(
        (
            title,
            href
        )
    )


count = 0


for title, url in articles[:MAX_ARTICLES]:

    try:

        page = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        page.raise_for_status()

    except:

        continue


    article = BeautifulSoup(
        page.text,
        "html.parser"
    )


    # Date
    date = datetime.now(
        timezone.utc
    )


    meta_date = article.find(
        "meta",
        property="article:published_time"
    )


    if meta_date:

        try:

            date = datetime.fromisoformat(
                meta_date["content"]
                .replace(
                    "Z",
                    "+00:00"
                )
            )

        except:

            pass


    # Image

    image = None

    og = article.find(
        "meta",
        property="og:image"
    )

    if og:

        image = og.get(
            "content"
        )


    description = (
        "Reuters World News article"
    )


    if image:

        description = (
            f'<img src="{image}"><br><br>'
            + description
        )


    item = feed.add_entry()

    item.title(
        title
    )

    item.link(
        href=url
    )

    item.guid(
        url,
        permalink=True
    )

    item.description(
        description
    )

    item.pubDate(
        format_datetime(date)
    )


    count += 1


print(
    "FOUND ARTICLES:",
    count
)


feed.lastBuildDate(
    format_datetime(
        datetime.now(timezone.utc)
    )
)


feed.rss_file(
    "feed.xml"
)
