import asyncio
import logging
from typing import Dict
from typing import List
from typing import Optional

from requests.exceptions import HTTPError
from textual.containers import Horizontal
from textual.widgets import ListItem
from textual.widgets import Static

from reddit_cli.common import Feed
from reddit_cli.common import FooterMetadata
from reddit_cli.common import HeaderMetadata
from reddit_cli.common import PostRowData
from reddit_cli.common import RedditPost
from reddit_cli.feed_handlers import BaseHandler
from reddit_cli.feed_handlers import JSONHandler
from reddit_cli.feed_handlers import RSSHandler
from reddit_cli.states.common import BaseListViewState
from reddit_cli.states.state_stack import StateStack
from reddit_cli.states.post_detail_state import PostDetailState


async def fetch_feed_async(handler: BaseHandler) -> List[RedditPost]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, handler.get_feed)

async def update_feed_async(handler: BaseHandler) -> List[RedditPost]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, handler.load_more_posts)

class PostListState(BaseListViewState):

    def __init__(self, stack: StateStack, feed_config: Feed) -> None:
        super().__init__(stack)
        self.feed_config = feed_config
        self.posts: List[RedditPost] = []
        self.after: Optional[str] = None
        self.id = "PostListState"
        self.header_metadata = HeaderMetadata(
            content=feed_config.name,
            id="post-list-header",
            classes="list-view-header header"
        )
        self.footer_text: Dict[str, str] = {
            "default": "\[j/k] or \[up/down] to navigate, \[enter] to view post, \[h/left] to go back, \[r] to refresh.",
            "bottom": "\[ctrl+L] load more posts, \[j/k] or \[up/down] to navigate, \[enter] to view post, \[h/left] to go back, \[r] to refresh."
        }
        self.footer_metadata = FooterMetadata(
            content=self.footer_text['default'],
            id="post-list-footer",
            classes="list-view-footer footer"
        )

    def on_enter(self) -> None:
        if self.iterable_items:
            return
        super().on_enter()
        self.loading = True
        self.refresh()
        asyncio.create_task(self._fetch_posts())

    async def _fetch_posts(self, force_reload: bool=False) -> None:
        # Decide which handler to use
        handler_class = RSSHandler if '.rss' in self.feed_config.url else JSONHandler
        handler = handler_class(self.feed_config.url, force_reload=force_reload)

        try:
            self.posts = await fetch_feed_async(handler)
        except HTTPError as e:
            logging.error(str(e))
            response = e.response
            status_code = response.status_code
            reason = response.reason
            # Set styling of the error
            error_msg = self.query_one(".nostyle", Static)
            # Adjust classes!
            error_msg.set_class(True, "error-message")
            error_msg.set_class(False, "nostyle")
            error_msg.update(f"Oh no! An error occurred! Status code: {status_code}, reason: {reason}")
            self.loading = False
            self.refresh()
            return

        # Set after attribute for lazy loading
        if self.posts:
            self.after = self.posts[-1].meta.get("name")

        self.iterable_items = self._generate_display_items(self.posts)
        self.loading = False

        self._populate_listview()  
        self.refresh()

    async def _load_more_posts(self) -> None:
        handler_class = RSSHandler if '.rss' in self.feed_config.url else JSONHandler
        if handler_class == RSSHandler:
            logging.info("Loading more posts not allowed for RSS feeds")
            return

        if not self.iterable_items:
            logging.info("Cannot load more posts, none have been loaded in the first place!")

        if not self.after:
            logging.info("Cannot load more posts, final post item has no meta.name attribute")
            return

        handler = handler_class(self.feed_config.url, force_reload=True, after=self.after)

        new_posts = await update_feed_async(handler)
        if new_posts:
            self.after = new_posts[-1].meta.get("name")
        new_items = self._generate_display_items(new_posts)

        self.posts.extend(new_posts)
        self.iterable_items.extend(new_items)
        self.loading = False

        list_items = [
            ListItem(Static(item)) if isinstance(item, str)
            else ListItem(item)
            for item in new_items
        ]

        if self.list_view is not None:
            self.list_view.extend(list_items)

        self.refresh()
        self._update_footer()

    def _generate_display_items(self, posts: List[RedditPost]) -> List[Horizontal]:
        items = []
        for post in posts:
            # Emoji for image/link/selfpost
            if post.image_url:
                emoji = "📷" 
            elif post.external_url:
                emoji = "🔗"
            else:
                emoji = "📰"

            data = PostRowData(
                emoji=emoji,
                subreddit=post.subreddit,
                title=post.title,
                meta=post.meta
            )
            items.append(data.to_container())
        return items

    def _update_footer(self) -> None:
        # Check if we're at the bottom and update texts
        footer = self.query_one("#post-list-footer", Static)
        if self.cursor == len(self.iterable_items) - 1:
            footer.update(self.footer_text['bottom'])
        else:
            footer.update(self.footer_text['default'])

    def handle_input(self, key: str) -> None:
        """Additional input handling for this state so we can refresh the feed with 'r'."""
        super().handle_input(key)

        if key == "r":
            self.loading = True
            self.refresh()
            asyncio.create_task(self._fetch_posts(force_reload=True))
        elif key == "enter":
            selected_post = self.posts[self.cursor]
            self.stack.push(
                PostDetailState(self.stack, selected_post)
            )

        self._update_footer()

        if key == "ctrl+l" and self.cursor == len(self.iterable_items) - 1:
            self.loading = True
            asyncio.create_task(self._load_more_posts())