from functools import lru_cache, partial
from typing import Callable

import pygame

from .constants import ROOT_DIR, SIZE
from .core import (
    get_mainloop,
    get_challenges,
    get_entries,
    get_challenge_data,
)

TITLE = "title"
ACCENT = "#48929B"


@lru_cache()
def font(size=20, name=None):
    name = name or "regular"
    path = ROOT_DIR / "wclib" / "assets" / (name + ".ttf")
    return pygame.font.Font(path, size)


@lru_cache()
def text(txt, color, size=20, font_name=None):
    return font(size, font_name).render(str(txt), True, color)


class State:
    BG_COLOR = 0x151515

    def __init__(self, app: "App"):
        self.app = app

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.app.states.clear()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.app.states.pop()

    def logic(self):
        pass

    def draw(self, screen):
        screen.fill(self.BG_COLOR)


class App:
    """
    The app handle the main logic of the program.
    It is a stacked state machine.
    """

    TITLE = "PGCD Weekly Challenges Showcase"

    def __init__(self, initial_state: Callable[["App"], State]):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode(SIZE)
        self.states = [initial_state(self)]

        pygame.display.set_caption(self.TITLE)

    @property
    def state(self):
        if self.states:
            return self.states[-1]
        return State(self)  # dummy, to finish the frame withou error

    def run(self):
        while self.states:
            self.state.handle_events(pygame.event.get())
            self.state.logic()
            self.state.draw(self.screen)
            pygame.display.update()


class MenuState(State):
    def __init__(self, app: "App", title, buttons):
        super().__init__(app)
        self.title = title
        self.buttons = [
            Button(
                *button,
                partial(self.button_click, button),
                self.button_position(i),
            )
            for i, button in enumerate(buttons)
        ]

    @staticmethod
    def button_position(i):
        padding = 5
        cols = (SIZE[0] - 2 * padding) // Button.TOTAL_SIZE[0]
        col_width = SIZE[0] / cols

        return (
            padding + (i % cols) * col_width + (col_width - Button.TOTAL_SIZE[0]) / 2,
            120 + i // cols * (Button.TOTAL_SIZE[1] + padding),
        )

    def button_click(self, data):
        raise NotImplemented

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        screen.fill(ACCENT, (0, 0, SIZE[0], 4))

        t = text(self.title, 0xEEEEEE00, 82, TITLE)
        screen.blit(t, t.get_rect(midtop=(SIZE[0] / 2, 20)))

        for button in self.buttons:
            button.draw(screen)

    def handle_events(self, events):
        super().handle_events(events)

        for button in self.buttons:
            button.handle_events(events)


class ChallengeSelectState(MenuState):
    BG_COLOR = 0x151515

    def __init__(self, app: "App"):
        super().__init__(
            app, "Weekly Challenges", [[c, None] for c in get_challenges()]
        )

    def button_click(self, data):
        challenge, none = data
        self.app.states.append(EntrySelectState(self.app, challenge))


class EntrySelectState(MenuState):
    def __init__(self, app: "App", challenge):
        buttons = [(challenge, entry) for entry in get_entries(challenge)]
        super().__init__(app, get_challenge_data(challenge).name, buttons)
        self.challenge = challenge

    def button_click(self, data):
        challenge, entry = data
        self.app.states.append(EntryViewState(self.app, self.challenge, entry))


class EntryViewState(State):
    def __init__(self, app: "App", challenge, entry):
        super().__init__(app)

        self.challenge = challenge
        self.entry = entry

        self.embedded_app = EmbeddedApp(challenge, entry)

    def handle_events(self, events):
        super().handle_events(events)
        self.embedded_app.handle_events(events)

    def draw(self, screen):
        self.embedded_app.draw(screen)


class Button:
    NAME_HEIGHT = 32
    SIZE = (SIZE[0] // 5, SIZE[1] // 5)
    TOTAL_SIZE = (SIZE[0], SIZE[1] + NAME_HEIGHT)

    def __init__(self, challenge, entry, callback, position):
        # If entry is None, it is a button to select a challenge.
        self.challenge = challenge
        self.entry = entry
        self.callback = callback
        self.position = pygame.Vector2(position)
        self.mouse_over = False

        self.title = self.entry or get_challenge_data(challenge).name

        self.app = EmbeddedApp(challenge, entry or "base", (self.position, self.SIZE))

    @property
    def rect(self):
        return pygame.Rect(self.position, self.TOTAL_SIZE)

    def draw(self, screen):
        background = "#222728" if self.mouse_over else "#212121"
        pygame.draw.rect(screen, background, self.rect, border_radius=4)

        self.app.draw(screen)

        offset = pygame.Vector2(0, -self.NAME_HEIGHT / 2)
        t = text(self.title, ACCENT)
        screen.blit(t, t.get_rect(center=self.rect.midbottom + offset))

    def handle_events(self, events):
        self.mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())

        if not self.mouse_over:
            return

        self.app.handle_events(events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.callback()


class EmbeddedApp:
    def __init__(self, challenge, entry, rect=(0, 0, *SIZE)):
        self.challenge = challenge
        self.entry = entry
        self.rect = pygame.Rect(rect)
        self.virtual_screen = pygame.Surface(SIZE)

        self.mainloop = get_mainloop(challenge, entry)
        next(self.mainloop)
        self.mainloop.send((self.virtual_screen, []))

        self.crashed = False

    def handle_events(self, events):
        try:
            self.mainloop.send((self.virtual_screen, events))
        except Exception:  # Or BaseException ?
            self.crashed = True
            t = text("Crashed", "red", 30)
            self.virtual_screen.blit(
                t, t.get_rect(center=self.virtual_screen.get_rect().center)
            )

    def draw(self, screen: pygame.Surface):
        if self.rect.size != self.virtual_screen.get_size():
            pygame.transform.smoothscale(
                self.virtual_screen, self.rect.size, screen.subsurface(self.rect)
            )
        else:
            screen.blit(self.virtual_screen, self.rect)
