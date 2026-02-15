import os
from dataclasses import dataclass
from typing import Optional

from textual.containers import Horizontal
from textual.widgets import Static

# Jank ass finding of the feeds yaml
_this_dir = os.path.abspath(os.path.dirname(__file__))
_root_dir = _this_dir
# Move up two dirs
for i in range(2):
    _root_dir = os.path.dirname(_root_dir)

CONFIG_YAML_PATH = os.path.join(_root_dir, "config.yaml")
if not os.path.exists(CONFIG_YAML_PATH):
    # Try and load config.sample.yaml
    CONFIG_YAML_PATH = os.path.join(_root_dir, "config.sample.yaml")
if not os.path.exists(CONFIG_YAML_PATH):
    raise FileNotFoundError(f"Neither config.yaml nor config.sample.yaml found in {_root_dir}. Please create one of these files. Refer to the README for instructions.")

@dataclass
class RedditPost:
    """Contains all relevant information about the posts"""
    title: str
    post_url: str
    subreddit: str
    content_raw: str
    content_clean: str
    external_url: Optional[str] = None
    image_url: Optional[str] = None

@dataclass
class Feed:
    """Contains global information about the user's feeds"""
    name: str
    url: str

@dataclass
class PostRowData:
    """For displaying a post in a ListView, we only need a subset of the RedditPost data"""
    emoji: str
    subreddit: str
    title: str
    meta: str

    def to_container(self) -> Horizontal:
        container = Horizontal(
            Static(self.emoji, classes="col-emoji"),
            Static(self.subreddit, classes="col-subreddit"),
            Static(self.title, classes="col-title"),
            Static(self.meta, classes="col-meta"),
            classes="post-row"
        )
        return container

@dataclass
class BaseMetadata:
    """Information for rendering a static component"""
    content: str
    classes: Optional[str] = None
    id: Optional[str] = None

@dataclass
class HeaderMetadata(BaseMetadata):
    pass

@dataclass
class FooterMetadata(BaseMetadata):
    pass


REDDIT_CLI_ASCII_ART = """
 ███████████                █████     █████  ███   █████         █████████  █████       █████
▒▒███▒▒▒▒▒███              ▒▒███     ▒▒███  ▒▒▒   ▒▒███         ███▒▒▒▒▒███▒▒███       ▒▒███ 
 ▒███    ▒███   ██████   ███████   ███████  ████  ███████      ███     ▒▒▒  ▒███        ▒███ 
 ▒██████████   ███▒▒███ ███▒▒███  ███▒▒███ ▒▒███ ▒▒▒███▒      ▒███          ▒███        ▒███ 
 ▒███▒▒▒▒▒███ ▒███████ ▒███ ▒███ ▒███ ▒███  ▒███   ▒███       ▒███          ▒███        ▒███ 
 ▒███    ▒███ ▒███▒▒▒  ▒███ ▒███ ▒███ ▒███  ▒███   ▒███ ███   ▒▒███     ███ ▒███      █ ▒███ 
 █████   █████▒▒██████ ▒▒████████▒▒████████ █████  ▒▒█████     ▒▒█████████  ███████████ █████
▒▒▒▒▒   ▒▒▒▒▒  ▒▒▒▒▒▒   ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒ ▒▒▒▒▒    ▒▒▒▒▒       ▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒▒ 

╔═════════════════════════════╗
║ Reddit CLI — Powered by RSS ║
╚═════════════════════════════╝
""".strip()
