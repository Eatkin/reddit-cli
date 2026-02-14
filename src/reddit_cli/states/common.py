from typing import Any
from typing import List
from typing import Optional

from textual.app import ComposeResult
from textual.widgets import ListItem
from textual.widgets import ListView
from textual.widgets import Static
from textual.reactive import reactive

from reddit_cli.common import HeaderMetadata
from reddit_cli.common import FooterMetadata
from reddit_cli.states.base_state import BaseState
from reddit_cli.states.state_stack import StateStack

class BaseListViewState(BaseState):

    BINDINGS = []
    who = reactive("BaseListViewState", recompose=True)

    def __init__(self, stack: StateStack):
        super().__init__(stack)
        self.cursor: int = 0
        self.iterable_items: List[Any] = []
        self.list_view: Optional[ListView] = None
        self.classes = "list-view-state"
        self.header_metadata: Optional[HeaderMetadata] = None
        self.footer_metadata: Optional[FooterMetadata] = None
        # Remove bindings cause we handle them manually in this base class

    def compose(self) -> ComposeResult:
        """Helper method to compose a ListView from iterable_items"""
        if self.header_metadata is not None:
            yield Static(self.header_metadata.content, id=self.header_metadata.id, classes=self.header_metadata.classes)

        if self.list_view is None:
            items = []

            for item in self.iterable_items:
                items.append(
                    ListItem(Static(item))
                )

            list_view = ListView(*items)
            self.list_view = list_view
            self.list_view.index = self.cursor
        else:
            self._populate_listview()
        yield self.list_view

        if self.footer_metadata is not None:
            yield Static(self.footer_metadata.content, id=self.footer_metadata.id, classes=self.footer_metadata.classes)

    def handle_input(self, key: str) -> None:
        """Vim style navigation for list views"""
        # DO NOT allow popping the state stack if we're in base state
        if key in ("h", "left") and len(self.stack) > 1:
            self.stack.pop()
            return

        if not self.iterable_items or self.list_view is None:
            return

        term_height = self.app.size.height // 2

        max_index = len(self.iterable_items) - 1

        if key in ("j", "down"):
            self.cursor = min(self.cursor + 1, max_index)
        elif key in ("k", "up"):
            self.cursor = max(self.cursor - 1, 0)
        elif key == "ctrl+d":
            self.cursor = min(self.cursor + term_height, max_index)
        elif key == "ctrl+u":
            self.cursor = max(self.cursor - term_height, 0)

        self.list_view.index = self.cursor

        self.refresh()

    def _populate_listview(self) -> None:
        if self.list_view is None:
            self.list_view = ListView()
        else:
            self.list_view.clear()

        items = []
        for item in self.iterable_items:
            if isinstance(item, str):
                it = ListItem(Static(item))
            else:
                it = ListItem(item)

            items.append(it)
        self.list_view.clear()
        self.list_view.extend(items)
        self.list_view.index = self.cursor