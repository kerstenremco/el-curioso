import os
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.request import urlopen
from xml.etree import ElementTree

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
FEED_URL = os.getenv("FEED_URL") or "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/lo-mas-visto/portada"
MAX_ARTICLE_AGE = timedelta(hours=int(os.getenv("MAX_ARTICLE_AGE_HOURS") or 24))
ARTICLE_LIMIT = int(os.getenv("ARTICLE_LIMIT") or 30)

NAMESPACES = {
    "media": "http://search.yahoo.com/mrss/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


class NewsArticle(BaseModel):
    guid: str = Field(description="The unique identifier (URL) of the news article")
    title: str = Field(description="The title of the news article")
    pubDate: str = Field(description="The publication date of the news article")
    link: str = Field(description="The URL to the full news article")
    categories: list[str] = Field(default_factory=list, description="The topic categories the article is tagged with")
    media_title: Optional[str] = Field(default=None, description="The title of the article's associated media, if any")
    media_credit: Optional[str] = Field(default=None, description="The credit/attribution for the article's associated media, if any")
    media_thumbnail: Optional[str] = Field(default=None, description="The URL of the article's thumbnail image, if any")
    content: str = Field(description="The full body content of the news article")


def fetch_feed() -> bytes:
    with urlopen(FEED_URL) as response:
        return response.read()


def parse_media(item: ElementTree.Element) -> dict[str, Optional[str]]:
    media_group = item.find("media:group", NAMESPACES)
    contents = (
        media_group.findall("media:content", NAMESPACES)
        if media_group is not None
        else item.findall("media:content", NAMESPACES)
    )

    image = next((c for c in contents if c.get("medium") == "image"), None)
    if image is None:
        return {"media_title": None, "media_credit": None, "media_thumbnail": None}

    return {
        "media_title": image.findtext("media:title", namespaces=NAMESPACES),
        "media_credit": image.findtext("media:credit", namespaces=NAMESPACES),
        "media_thumbnail": image.get("url"),
    }


def parse_feed(xml_bytes: bytes) -> list[NewsArticle]:
    root = ElementTree.fromstring(xml_bytes)
    articles = []

    for item in root.iter("item"):
        guid = item.findtext("guid")
        title = item.findtext("title")
        pubDate = item.findtext("pubDate")
        link = item.findtext("link")
        content = item.findtext("content:encoded", namespaces=NAMESPACES)

        if not (guid and title and pubDate and link and content):
            continue

        articles.append(
            NewsArticle(
                guid=guid,
                title=title,
                pubDate=pubDate,
                link=link,
                categories=[c.text for c in item.findall("category") if c.text],
                content=content,
                **parse_media(item),
            )
        )

    return articles

def is_recent(pub_date: str, max_age: timedelta = MAX_ARTICLE_AGE) -> bool:
    published = parsedate_to_datetime(pub_date)
    return datetime.now(timezone.utc) - published <= max_age


def get_news_articles() -> list[NewsArticle]:
    xml_bytes = fetch_feed()
    articles = parse_feed(xml_bytes)
    recent_articles = [article for article in articles if is_recent(article.pubDate)]
    return recent_articles[:ARTICLE_LIMIT]