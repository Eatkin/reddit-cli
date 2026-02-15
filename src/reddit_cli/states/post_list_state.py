import asyncio
from typing import List

from textual.containers import Horizontal

from reddit_cli.common import Feed
from reddit_cli.common import FooterMetadata
from reddit_cli.common import HeaderMetadata
from reddit_cli.common import PostRowData
from reddit_cli.common import RedditPost
from reddit_cli.rss_handler import RSSHandler
from reddit_cli.states.common import BaseListViewState
from reddit_cli.states.state_stack import StateStack
from reddit_cli.states.post_detail_state import PostDetailState


async def fetch_feed_async(handler: RSSHandler) -> List[RedditPost]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, handler.get_feed)

class PostListState(BaseListViewState):

    def __init__(self, stack: StateStack, feed_config: Feed) -> None:
        super().__init__(stack)
        self.feed_config = feed_config
        self.posts: List[RedditPost] = []
        self.id = "PostListState"
        self.header_metadata = HeaderMetadata(
            content=feed_config.name,
            id="post-list-header",
            classes="list-view-header header"
        )
        self.footer_metadata = FooterMetadata(
            content="\[j/k] or \[up/down] to navigate, \[enter] to view post, \[h/left] to go back, \[r] to refresh.",
            id="post-list-footer",
            classes="list-view-footer footer"
        )

    def on_enter(self) -> None:
        if self.iterable_items:
            return
        super().on_enter()
        self.posts = []
        self.loading = True
        self.refresh()
        asyncio.create_task(self._fetch_posts())

    async def _fetch_posts(self, force_reload: bool=False) -> None:
        handler = RSSHandler(self.feed_config.url, force_reload=force_reload)
        self.posts = await fetch_feed_async(handler)
        self.iterable_items = self._generate_display_items()
        self.loading = False
        self._populate_listview()  
        self.refresh()

    def _generate_display_items(self) -> List[Horizontal]:
        items = []
        for post in self.posts:
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
                meta=""
            )
            items.append(data.to_container())
        return items

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