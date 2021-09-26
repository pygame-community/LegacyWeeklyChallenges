import importlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Callable

import pygame

from .constants import ROOT_DIR, SIZE
from .core import MainLoop, get_mainloop

TITLE = "title"
ACCENT = "#48929B"


@lru_cache()
def font(size=20, name=None):
    name = name or "regular"
    path = ROOT_DIR / "lib" / "assets" / (name + ".ttf")
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

    def logic(self):
        pass

    def draw(self, screen):
        screen.fill(self.BG_COLOR)


class App:
    """
    The app handle the main logic of the program.
    It is a stacked state machine.
    """

    def __init__(self, initial_state: Callable[["App"], State]):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode(SIZE)
        self.states = [initial_state(self)]

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


class ChallengeSelectState(State):
    BG_COLOR = 0x151515

    def __init__(self, app: "App"):
        super().__init__(app)
        # Challenges are the only files/folders that start with digits
        self.challenges = [c.stem for c in ROOT_DIR.glob("[0-9]*")]

    def logic(self):
        if len(self.challenges) == 1:
            self.app.states[-1] = EntrySelectState(self.app, self.challenges[0])


class EntrySelectState(State):
    def __init__(self, app: "App", challenge):
        super().__init__(app)
        self.challenge = challenge
        data: dict = json.loads((ROOT_DIR / challenge / "data.json").read_text())
        self.name = data.get("name", "No name")
        self.entries = list(self.load_entries())

        padding = 5
        cols = (SIZE[0] - 2 * padding) // Button.TOTAL_SIZE[0]
        col_width = SIZE[0] / cols

        def compute_pos(i):
            return (
                padding
                + (i % cols) * col_width
                + (col_width - Button.TOTAL_SIZE[0]) / 2,
                120 + i // cols * (Button.TOTAL_SIZE[1] + padding),
            )

        self.buttons = [
            Button(
                self.challenge, entry, lambda: self.button_click(entry), compute_pos(i)
            )
            for i, entry in enumerate(self.load_entries())
        ]

    def button_click(self, entry):
        print(entry)

    def load_entries(self):
        challenge_dir = ROOT_DIR / self.challenge
        for directory in challenge_dir.iterdir():
            main = directory / "main.py"
            if not main.exists():
                continue

            yield directory.stem

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        screen.fill(ACCENT, (0, 0, SIZE[0], 4))

        t = text(self.name, 0xEEEEEE00, 82, TITLE)
        screen.blit(t, t.get_rect(midtop=(SIZE[0] / 2, 20)))

        for button in self.buttons:
            button.draw(screen)

    def handle_events(self, events):
        super().handle_events(events)

        for button in self.buttons:
            button.handle_events(events)


class Button:
    NAME_HEIGHT = 32
    SIZE = (SIZE[0] // 5, SIZE[1] // 5)
    TOTAL_SIZE = (SIZE[0], SIZE[1] + NAME_HEIGHT)

    def __init__(self, challenge, entry, callback, position):
        self.challenge = challenge
        self.entry = entry
        self.callback = callback
        self.position = pygame.Vector2(position)
        self.mouse_over = False

        self.app = EmbeddedApp(challenge, entry, (self.position, self.SIZE))

    @property
    def rect(self):
        return pygame.Rect(self.position, self.TOTAL_SIZE)

    def draw(self, screen):
        background = "#222728" if self.mouse_over else "#212121"
        pygame.draw.rect(screen, background, self.rect, border_radius=4)

        self.app.draw(screen)

        offset = pygame.Vector2(0, -self.NAME_HEIGHT / 2)
        t = text(self.entry, ACCENT)
        screen.blit(t, t.get_rect(center=self.rect.midbottom + offset))

    def handle_events(self, events):
        self.mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())

        if not self.mouse_over:
            return

        self.app.handle_events(events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
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
