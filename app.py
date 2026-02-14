from textual.app import App
from textual.events import Key

from reddit_cli.common import CONFIG_YAML_PATH
from reddit_cli.states.state_stack import StateStack
from reddit_cli.states.feed_list_state import FeedListState
from reddit_cli.style import THEMES
from reddit_cli.utils import read_theme_from_yaml

_theme_name = read_theme_from_yaml(CONFIG_YAML_PATH)

class RedditCLIApp(App[None]):
    
    CSS_PATH = THEMES.get(_theme_name, THEMES["default"])

    def __init__(self) -> None:
        super().__init__()
        self.stack = StateStack(self)

    def on_mount(self) -> None:
        # Push first state
        self.stack.push(FeedListState(self.stack))

    def on_key(self, event: Key) -> None:
        if self.stack.current:
            self.stack.current.handle_input(event.key)
            if not self.stack.current:
                self.exit()

def main() -> None:
    app = RedditCLIApp()
    app.run(inline=True)

if __name__ == "__main__":
    main()