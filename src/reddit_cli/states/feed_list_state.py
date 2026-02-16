from typing import List

from reddit_cli.common import CONFIG_YAML_PATH
from reddit_cli.common import Feed
from reddit_cli.common import FooterMetadata
from reddit_cli.common import HeaderMetadata
from reddit_cli.common import REDDIT_CLI_ASCII_ART
from reddit_cli.states.common import BaseListViewState
from reddit_cli.states.custom_sub_state import CustomSubState
from reddit_cli.states.state_stack import StateStack
from reddit_cli.states.post_list_state import PostListState
from reddit_cli.utils import read_feeds_from_yaml


class FeedListState(BaseListViewState):

    def __init__(self, stack: StateStack) -> None:
        super().__init__(stack)
        self.feeds: List[Feed] = read_feeds_from_yaml(CONFIG_YAML_PATH)
        self.iterable_items = [feed.name for feed in self.feeds]
        # Append add custom feed to the end
        self.iterable_items.append("Enter custom subreddit")
        self.cursor: int = 0
        self.id = "FeedListState"
        self.header_metadata = HeaderMetadata(content=REDDIT_CLI_ASCII_ART, id="ascii-art")
        self.footer_metadata = FooterMetadata(content="\[j/k] or \[up/down] to navigate, \[enter] to select, \[q] to quit", classes="footer")
    
    def handle_input(self, key: str) -> None:
        super().handle_input(key)  # Handle navigation keys
        if key == "enter":
            # Push the sub unless we've selected custom entry then go to custom sub state!
            if self.cursor == len(self.iterable_items) - 1:
                self.stack.push(CustomSubState(self.stack))
            else:
                selected_feed = self.feeds[self.cursor]
                self.stack.push(
                    PostListState(self.stack, selected_feed)
                )
        elif key == "q":
            self.stack.pop()

        self.refresh()