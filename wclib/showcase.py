"""
This is the weekly challenges showcase.

This file contains all the state (or screens) of the app,
as well as the state machine (App) that orchestrate between them.
"""
from operator import attrgetter
from functools import partial
from random import shuffle
from typing import Callable

import pygame

from .constants import *
from .core import *
from .utils import text, load_image
from .widgets import *


class State:
    BG_COLOR = BACKGROUND

    def __init__(self, app: "App", *widgets: Widget):
        self.app = app
        self.widgets = list(widgets)

    def add(self, widget: Widget):
        self.widgets.append(widget)
        return widget

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return self.app.states.clear() or True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.states.pop()
                return True

        for widget in self.widgets:
            if widget.handle_event(event):
                return True
        return False

    def logic(self):
        for widget in self.widgets:
            widget.logic()

    def draw(self, screen):
        screen.fill(self.BG_COLOR)

        for widget in self.widgets:
            widget.draw(screen)


class App:
    """
    The app handle the main logic of the program.
    It is a stacked state machine.
    """

    TITLE = "PGCD Weekly Challenges Showcase"

    def __init__(self, initial_state: Callable[["App"], State]):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode(SIZE, pygame.SCALED)
        self.states = [initial_state(self)]

        pygame.display.set_caption(self.TITLE)

    @property
    def state(self):
        if self.states:
            return self.states[-1]
        return State(self)  # dummy, to finish the frame withou error

    def run(self):
        while self.states:
            for event in pygame.event.get():
                self.state.handle_event(event)
            self.state.logic()
            self.state.draw(self.screen)
            pygame.display.update()


class MenuState(State):
    GAPS = 20  # pixels between each button
    ButtonClass = BigButton

    def __init__(self, app: "App", title, buttons):
        self.timer = 0

        t = text(title, LIGHT, 82, TITLE_FONT)
        title = ImageWidget(t, t.get_rect(midtop=(SIZE[0] / 2, self.GAPS * 1.5)))

        buttons = [
            self.ButtonClass(
                button,
                partial(self.button_click, button),
                self.button_position(i),
            )
            for i, button in enumerate(buttons)
        ]

        self.scroll_area = ScrollableWidget(
            (0, 0), SIZE, title, *buttons, top=ACCENT, bottom=self.BG_COLOR
        )
        super().__init__(app, self.scroll_area)

        self.clock = pygame.time.Clock()

    def button_position(self, i):
        gaps = self.GAPS
        cols = SIZE[0] // (BigButton.TOTAL_SIZE[0] + gaps)
        start = (SIZE[0] - cols * BigButton.TOTAL_SIZE[0] - (cols - 1) * gaps) / 2

        return (
            start + (i % cols) * (BigButton.TOTAL_SIZE[0] + gaps),
            130 + i // cols * (BigButton.TOTAL_SIZE[1] + gaps),
        )

    def button_click(self, data):
        raise NotImplemented

    def logic(self):
        super().logic()
        self.timer += 1
        self.clock.tick(60)

        # we load one app per frame, for smoother UX
        # This just loads the first unloaded app
        any(b.app.load() for b in self.scroll_area if isinstance(b, BigButton))

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        screen.fill(ACCENT, (0, 0, SIZE[0], 4))


class ChallengeSelectState(MenuState):
    BG_COLOR = 0x151515
    ButtonClass = ChallengeButton

    def __init__(self, app: "App"):
        super().__init__(app, "Weekly Challenges", get_challenges())

    def button_click(self, challenge):
        self.app.states.append(EntrySelectState(self.app, challenge))


class EntrySelectState(MenuState):
    ButtonClass = EntryButton

    def __init__(self, app: "App", challenge):
        buttons = get_entries(challenge)
        super().__init__(app, get_challenge_data(challenge).name, buttons)
        self.challenge = challenge
        self.sorted = True

        icon = load_image("sort")
        r = icon.get_rect(topright=(SIZE[0] - 10, 16))
        sort_button = self.add(IconButton(r.topleft, r.size, icon, self.toggle_sort))

        self.toggle_sort(sort_button)

    def handle_event(self, event):
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                self.print_score_update_command()

    def toggle_sort(self, button: IconButton):
        buttons = [w for w in self.scroll_area if isinstance(w, BigButton)]

        self.sorted = not self.sorted
        if self.sorted:
            button.surf = load_image("shuffle")
            buttons.sort(key=lambda b: b.entry.entry.casefold())
        else:
            button.surf = load_image("sort")
            shuffle(buttons)

        button.surf.set_alpha(100)

        for i, button in enumerate(buttons):
            button.move_to(self.button_position(i))

    def button_click(self, entry):
        self.app.states.append(EntryViewState(self.app, entry))

    def print_score_update_command(self):
        print("pg!events wc update")
        for entry in get_entries(self.challenge):
            if entry.entry != "base":
                points = tuple(
                    [3 - i for i, diff in enumerate(DIFFICULTIES) if diff in entry.achievements]
                )
                print(f"( <@{entry.discord_tag}> {points} )")


class EntryViewState(State):
    def __init__(self, app: "App", entry: Entry):
        super().__init__(app)

        self.entry = entry

        self.embedded_app = EmbeddedApp(entry)

    def handle_event(self, event):
        super().handle_event(event)
        self.embedded_app.handle_event(event)

    def logic(self):
        self.embedded_app.logic()
        if self.embedded_app.exited:
            self.app.states.pop()

    def draw(self, screen):
        self.embedded_app.draw(screen)
