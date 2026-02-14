import re
import textwrap
from typing import Dict, List
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from reddit_cli.common import RedditPost
from reddit_cli.utils import get_random_user_agent

class RSSHandler:
    FEED_CACHE: Dict[str, List[RedditPost]] = {}

    def __init__(self, feed_url: str, force_reload: bool=False) -> None:
        self.feed_url = feed_url
        self.raw_feed = None
        self.feed = None

        # Check if our feed is already cached
        if self.feed_url in self.FEED_CACHE and not force_reload:
            self.feed = self.FEED_CACHE[self.feed_url]

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
    def _extract_image_url(content: str) -> Optional[str]:
        if not content:
            return None

        soup = BeautifulSoup(content, "html.parser")

        img = soup.find("img")

        if img and img.get("src"):
            return str(img["src"])

        return None


    def _fetch_feed(self) -> None:
        """
        Fetch the RSS feed for the given URL.
        """
        header = {
            'User-Agent': get_random_user_agent()
        }
        response = requests.get(self.feed_url, headers=header)
        # TODO: Handle this gracefully
        response.raise_for_status()
        self.raw_feed = feedparser.parse(response.text)

    def _parse_feed(self) -> None:
        """Parse the raw feed data into structured RedditPost objects."""
        if self.raw_feed is None:
            raise Exception("Feed not fetched yet. Call fetch_feed() first.")
        
        entries = []
        for entry in self.raw_feed.entries:
            # Content is the raw HTML content of the post
            content = entry.content[0].value
            entry_obj = RedditPost(
                title=entry.title,
                post_url=entry.link,
                content_raw=content,
                content_clean=self._clean_content(content),
                subreddit=entry.tags[0].term if 'tags' in entry else 'Unknown',
                image_url=self._extract_image_url(content)
            )
            entries.append(entry_obj)
        
        self.feed = entries

    def get_feed(self) -> List[RedditPost]:
        """Return the parsed feed on demand, fetching and parsing if necessary."""
        if self.feed is not None:
            return self.feed
        
        self._fetch_feed()
        self._parse_feed()
        assert self.feed is not None, "This should never happen and is only here to satisfy type checkers."
        # Cache the feed for future use
        self.FEED_CACHE[self.feed_url] = self.feed
        return self.feed
