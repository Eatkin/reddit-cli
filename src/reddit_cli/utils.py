import os
import random
from io import BytesIO
from typing import List

import requests
import yaml

from reddit_cli.common import Feed

def get_random_user_agent() -> str:
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(user_agents)
    
def read_feeds_from_yaml(file_path: str) -> List[Feed]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find {file_path}. Please create it and add some Reddit RSS feed URLs in the specified format.")

    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    feeds = []
    for feed_data in data.get('feeds', []):
        url = feed_data.get('url')
        if url is None:
            print(f"Feed skipped due to missing url key: {feed_data}")
            continue
        # Silently replace .rss with .json
        url = url.replace('.rss', '.json')
        # Check to make sure is valid feed
        if ".json" not in url:
            print(f"Feed is not recognised as a valid rss/json feed: {url}")
            continue
        feeds.append(Feed(name=feed_data.get('name', url), url=url))

    return feeds

def read_theme_from_yaml(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find {file_path}. Please create it and add a theme name in the specified format.")

    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    theme_name = data.get('theme')
    if not theme_name:
        raise ValueError("Theme name not found in YAML file. Please ensure it has a 'theme' key.")

    try:
        theme_name = str(theme_name).strip()
    except Exception as e:
        raise ValueError(f"Error processing theme name: {e}")

    # Satisfy the stupid type checker
    assert isinstance(theme_name, str), "Theme name must be a string."

    return theme_name


def fetch_image_bytes(url: str) -> BytesIO | None:
    """Download an image from a URL into a BytesIO buffer."""
    # TODO: Add image cachine to avoid repeat requests
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        print(f"Failed to fetch image: {e}")
        return None