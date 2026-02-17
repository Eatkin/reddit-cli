import sys
from logging.config import dictConfig

from textual.app import App
from textual.events import Key

from reddit_cli.common import CONFIG_YAML_PATH
from reddit_cli.states.state_stack import StateStack
from reddit_cli.states.feed_list_state import FeedListState
from reddit_cli.style import THEMES
from reddit_cli.utils import read_theme_from_yaml

# Setup logging globally
dictConfig({
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "file_formatter": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "mode": "a",
            "encoding": "utf-8",
            "formatter": "file_formatter",
            "level": "DEBUG",
        },
    },

    "root": {
        "handlers": ["file_handler"],
        "level": "DEBUG",
    },
})


_theme_name = read_theme_from_yaml(CONFIG_YAML_PATH)

class RedditCLIApp(App[None]):
    
    CSS_PATH = THEMES.get(_theme_name, THEMES["default"])

    def __init__(self, boss_mode: bool = False) -> None:
        super().__init__()
        self.stack = StateStack(self, boss_mode=boss_mode)

    def on_mount(self) -> None:
        # Push first state
        self.stack.push(FeedListState(self.stack))

    def on_key(self, event: Key) -> None:
        if self.stack.current:
            self.stack.current.handle_input(event.key)
            if not self.stack.current:
                self.exit()

def main() -> None:
    clargs = sys.argv
    boss_mode =  clargs[-1] == "--boss-mode"
    app = RedditCLIApp(boss_mode=boss_mode)
    app.run(inline=True)

if __name__ == "__main__":
    main()