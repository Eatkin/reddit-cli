from textual.app import App

from reddit_cli.states.base_state import BaseState

class StateStack:
    def __init__(self, app: App[None], boss_mode: bool = False) -> None:
        self.boss_mode = boss_mode
        self.stack: list[BaseState] = []
        self.app = app

    def push(self, state: BaseState) -> None:
        if self.stack:
            self.stack[-1].display = False
            self.stack[-1].on_exit()

        self.stack.append(state)

        self.app.mount(state)
        state.on_enter()


    def pop(self) -> None:
        if not self.stack:
            return

        state = self.stack.pop()
        state.on_exit()
        state.remove()  

        if self.stack:
            previous = self.stack[-1]
            previous.display = True
            previous.on_enter()


    @property
    def current(self) -> BaseState | None:
        return self.stack[-1] if self.stack else None

    def __len__(self) -> int:
        return len(self.stack)
