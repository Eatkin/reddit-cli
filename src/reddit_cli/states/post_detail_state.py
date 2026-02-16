import asyncio
from io import BytesIO
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Static
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual_image.widget import Image

from reddit_cli.common import RedditPost
from reddit_cli.common import HeaderMetadata
from reddit_cli.common import FooterMetadata
from reddit_cli.states.base_state import BaseState
from reddit_cli.states.state_stack import StateStack
from reddit_cli.utils import fetch_image_bytes

async def fetch_image_bytes_async(url: str) -> BytesIO | None:
    """Async wrapper for fetch_image_bytes to avoid blocking the event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_image_bytes, url)


class PostDetailState(BaseState):

    # Add bindings
    BINDINGS = BaseState.BINDINGS + [
        Binding("j", "scroll_up", "Scroll Up", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("ctrl+u", "page_up", "Page Up", show=False),
        Binding("ctrl+d", "page_down", "Page Down", show=False),
    ]


    who = reactive("PostDetailState", recompose=True)

    def __init__(self, stack: StateStack, post: RedditPost) -> None:
        super().__init__(stack)
        self.post = post
        self.id = "PostDetailState"
        self.header_metadata = HeaderMetadata(
            content=post.title,
            id="post-detail-header",
            classes="post-detail-header header"
        )
        self.footer_metadata = FooterMetadata(
            content="[h/left] to go back.",
            id="post-detail-footer",
            classes="post-detail-footer footer"
        )

        self.placeholder = Static("Loading image...", classes="post-image-placeholder")
        self.image_bytes: Optional[BytesIO] = None
        self.image_widget: Optional[Horizontal] = None
        
        self._set_content()

    def _set_content(self) -> None:
        img_content = self.post.image_url is not None
        external_url = self.post.external_url is not None
        components = []

        components.append(Static(f"Link to post: {self.post.post_url}", classes="post-url"))

        if img_content:
            components.append(Static(f"Attached image URL: {self.post.image_url}", classes="post-image-url"))

        if external_url:
            components.append(Static(f"External link: {self.post.external_url}", classes="post-external-link-url"))

        components.append(Static(self.post.content_clean, classes="post-content-body"))
            
        if img_content:
            components.append(self.placeholder)

        self.content = VerticalScroll(*components, classes="post-detail-body")

    def compose(self) -> ComposeResult:
        yield Static(self.header_metadata.content, id=self.header_metadata.id, classes=self.header_metadata.classes)
        yield self.content
        yield Static(self.footer_metadata.content, id=self.footer_metadata.id, classes=self.footer_metadata.classes)

    def handle_input(self, key: str) -> None:
        if key in ["h", "left"]:
            self.stack.pop()

    def on_enter(self) -> None:
        # Kick off image loading if there is a URL
        if self.post.image_url is not None:
            asyncio.create_task(self._load_image())

    async def _load_image(self) -> None:
        if self.image_widget is not None:
            return

        img_bytes = await fetch_image_bytes_async(self.post.image_url)  # type: ignore
        self.content.remove_children(".post-image-placeholder")
        if img_bytes:
            self.image_bytes = img_bytes
            # Remove the placeholder
            self.image_widget = Horizontal(Image(img_bytes, classes="post-image"), classes="post-image-container")
            self.content.mount(self.image_widget)
        else:
            self.content.mount(Static("Failed to load image!!"))
