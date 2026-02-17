import json
import re
import textwrap
from abc import ABC
from abc import abstractmethod
from typing import Dict, List
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

import feedparser
import requests
from bs4 import BeautifulSoup

from reddit_cli.common import RedditPost
from reddit_cli.utils import get_random_user_agent

class BaseHandler(ABC):
    FEED_CACHE: Dict[str, List[RedditPost]] = {}

    def __init__(self, feed_url: str, force_reload: bool=False, limit: int = 25, after: Optional[str] = None) -> None:
        # Parse and rebuild url with limit param
        self.feed_url = feed_url
        self.limit = limit
        self.after = after
        self.base_url = self._extract_base_url(self.feed_url)
        self._sanitise_feed_url()

        self.raw_feed: Optional[str] = None
        self.feed: Optional[List[RedditPost]] = None

        # Check if our feed is already cached
        if self.base_url in self.FEED_CACHE and not force_reload:
            self.feed = self.FEED_CACHE[self.base_url]

    @staticmethod
    def _extract_base_url(url: str) -> str:
        parsed = urlparse(url)
        stripped_url = urlunparse(parsed._replace(query="", fragment=""))
        return str(stripped_url)

    def _sanitise_feed_url(self) -> None:
        # Prepares url with query parameters
        parsed = urlparse(self.feed_url)
        query = parse_qs(parsed.query)  
        query['limit'] = [str(self.limit)]
        if self.after is not None:
            query['after'] = [self.after]
        new_query = urlencode(query, doseq=True)
        self.feed_url = urlunparse(parsed._replace(query=new_query))

    def _fetch_feed(self) -> str:
        """
        Fetch the RSS feed for the given URL.
        """
        header = {
            'User-Agent': get_random_user_agent()
        }
        self._sanitise_feed_url()
        response = requests.get(self.feed_url, headers=header)
        # TODO: Handle this gracefully
        response.raise_for_status()
        return response.text

    @abstractmethod
    def _parse_feed(self) -> List[RedditPost]:
        pass

    def get_feed(self) -> List[RedditPost]:
        """Return the parsed feed on demand, fetching and parsing if necessary."""
        if self.feed is not None:
            return self.feed
        
        self.raw_feed = self._fetch_feed()
        self.feed = self._parse_feed()
        # Cache the feed for future use
        self.FEED_CACHE[self.base_url] = self.feed
        return self.feed

    def load_more_posts(self) -> List[RedditPost]:
        """
        Used when the feed has already been loaded to get more posts
        Same as get_feed but will add to feed rather than replacing
        """
        self.raw_feed = self._fetch_feed()
        new_posts = self._parse_feed()
        # Get pre-existing posts
        old_posts = self.FEED_CACHE.get(self.feed_url, [])
        self.feed = old_posts + new_posts

        # Update cache
        self.FEED_CACHE[self.base_url] = self.feed
        return new_posts


class RSSHandler(BaseHandler):
    @staticmethod
    def _clean_content(content: str) -> str:
        soup = BeautifulSoup(content, "html.parser")

        text = soup.get_text(separator="\n\n")

        text = text.split("submitted by")[0]

        text = textwrap.dedent(text)

        lines = [line.rstrip() for line in text.splitlines()]
        text = "\n".join(lines)

        # collapse 3+ newlines into 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
    
    @staticmethod
    def _extract_external_url(content: str) -> Optional[str]:
        """External URLs have placeholder text [link] so can be easily found"""
        soup = BeautifulSoup(content, "html.parser")

        link_tag = soup.find("a", text="[link]")
        external_url = str(link_tag["href"]) if link_tag else None

        # Defaults to the link to the post
        if external_url and "reddit.com" in external_url:
            return None

        return external_url


    @staticmethod
    def _extract_image_url(content: str) -> Optional[str]:
        if not content:
            return None

        soup = BeautifulSoup(content, "html.parser")

        img = soup.find("img")

        if img and img.get("src"):
            return str(img["src"])

        return None


    def _parse_feed(self) -> List[RedditPost]:
        """Parse the raw feed data into structured RedditPost objects."""
        if self.raw_feed is None:
            raise Exception("Feed not fetched yet. Call fetch_feed() first.")

        feed = feedparser.parse(self.raw_feed)
        
        entries = []
        for entry in feed.entries:
            # Content is the raw HTML content of the post
            content = entry.content[0].value
            entry_obj = RedditPost(
                title=entry.title,
                post_url=entry.link,
                content_raw=content,
                content_clean=self._clean_content(content),
                subreddit=entry.tags[0].term if 'tags' in entry else 'Unknown',
                external_url=self._extract_external_url(content),
                image_url=self._extract_image_url(content)
            )
            entries.append(entry_obj)
        
        return entries

class JSONHandler(BaseHandler):

    REDDIT_BASE_URL = "https://www.reddit.com"

    def _parse_feed(self) -> List[RedditPost]:
        """Parse raw JSON into structured RedditPost objects."""
        if self.raw_feed is None:
            raise Exception("Feed not fetched yet. Call fetch_feed() first.")

        feed = json.loads(self.raw_feed).get('data', {}).get('children', [])

        entries = []
        for entry in feed:
            data = entry['data']
            entry_obj = RedditPost(
                title=data['title'],
                post_url=urljoin(self.REDDIT_BASE_URL, data['permalink']),
                content_raw=data['selftext_html'],
                content_clean=data['selftext'],
                subreddit=data['subreddit'],
                external_url=data.get('url_overridden_by_dest'),
                image_url=data.get('url_overridden_by_dest') if data.get('is_reddit_media_domain') else None,
                meta={'name': data.get('name')} # Used for the 'after' query param for lazy loading
            )
            entries.append(entry_obj)
        
        return entries
