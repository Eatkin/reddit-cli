from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.widget import Widget

if TYPE_CHECKING:
    from reddit_cli.states.state_stack import StateStack

class BaseState(Widget):
    def __init__(self, stack: StateStack) -> None:
        super().__init__()
        self.stack = stack
        self.cursor = 0

    def move_up(self) -> None:
        if self.cursor > 0:
            self.cursor -= 1

    def move_down(self, max_index: int) -> None:
        if self.cursor < max_index:
            self.cursor += 1

    def on_enter(self) -> None:
        # Called when state becomes active
        pass

    def on_exit(self) -> None:
        # Called when state is no longer active
        pass

    @abstractmethod
    def compose(self) -> ComposeResult:
        # Return a Textual Widget to be rendered
        pass

    @abstractmethod
    def handle_input(self, key: str) -> None:
        # Handle keyboard input
        pass
