import re
from typing import Any
from urllib.parse import urljoin
  
from textual import on
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Input
from textual.widgets import Static
from textual.validation import Function

from reddit_cli.common import Feed
from reddit_cli.common import FooterMetadata
from reddit_cli.common import HeaderMetadata
from reddit_cli.states.base_state import BaseState
from reddit_cli.states.state_stack import StateStack
from reddit_cli.states.post_list_state import PostListState

class CustomSubState(BaseState):

    BASE_URL = "https://www.reddit.com/r/"

    who = reactive("CustomSubState", recompose=True)

    def __init__(self, stack: StateStack) -> None:
        super().__init__(stack)
        self.id = "CustomSubState"
        self.header_metadata = HeaderMetadata(
            content="Enter a subreddit name",
            id="custom-sub-header",
            classes="custom-sub-header header"
        )
        self.footer_metadata = FooterMetadata(
            content="\[esc] to go back, \[enter] to submit.",
            id="custom-sub-footer",
            classes="custom-sub-footer footer"
        )

    def compose(self) -> ComposeResult:
        yield Static(self.header_metadata.content, id=self.header_metadata.id, classes=self.header_metadata.classes)
        yield Input(placeholder="Enter subreddit name",
                    validators=[Function(lambda w: re.fullmatch(r'[\w\-]+', w) is not None, "Subreddit contains invalid characters.")],
                    id="subreddit-input"
        )
        yield Static(id='validation-error')
        yield Static(self.footer_metadata.content, id=self.footer_metadata.id, classes=self.footer_metadata.classes)

    def _focus_input(self) -> None:
        # Make sure cursor is in the input box by default
        self.query_one("#subreddit-input", Input).focus()

    def on_mount(self) -> None:
        self._focus_input()

    def on_enter(self) -> None:
        super().on_enter()
        self._focus_input()

    def _is_valid(self, event: Any) -> bool:
        result = event.validation_result
        if result is None:
            return False
        if not isinstance(result.is_valid, bool):
            return False
        return result.is_valid

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        validation_error = self.query_one("#validation-error", Static)
        if not self._is_valid(event):
            validation_result = event.validation_result
            if validation_result is not None:
                failure_descriptions = validation_result.failure_descriptions
                failure_message = "\n".join(failure_descriptions)
                validation_error.update(failure_message)
        else:
            validation_error.update('')

    @on(Input.Submitted)
    def goto_subreddit_feed(self, event: Input.Submitted) -> None:
        if self._is_valid(event):
            inp = self.query_one('#subreddit-input', Input).value
            feed = Feed(inp, urljoin(self.BASE_URL, f'{inp}/.json'))
            self.stack.push(
                PostListState(self.stack, feed)
            )


    def handle_input(self, key: str) -> None:
        if key == "escape":
            self.stack.pop()