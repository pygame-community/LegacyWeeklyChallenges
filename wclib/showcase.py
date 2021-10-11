import importlib
import json
import sys
from functools import lru_cache, partial
import traceback
from pathlib import Path
from threading import Thread
from typing import Callable, List

import pygame

from .constants import ROOT_DIR, SIZE
from .core import (
    get_mainloop,
    get_challenges,
    get_entries,
    get_challenge_data,
    get_missing_requirements,
    install_missing_requirements,
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
        super().__init__(app, "Weekly Challenges", [[c, None] for c in get_challenges()])

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
        self.missing_requirements = get_missing_requirements(challenge, entry)

        self.mainloop = self.load_mainloop()
        self.mainloop_next()

    def mainloop_next(self, events=(), _first=False):
        try:
            events = list(self.modify_events(events))
            if _first:
                next(self.mainloop)
            self.mainloop.send((self.virtual_screen, events))
        except StopIteration:
            pass
        except TypeError as e:
            # Yuck!
            if e.args == ("can't send non-None value to a just-started generator",):
                return self.mainloop_next(events, True)
            else:
                # Double yuck!
                print("Error:", e)
                print(traceback.print_exc())
                self.mainloop = self.crashed_mainloop(e)
        except Exception as e:  # Or BaseException ?
            print("Error:", e)
            print(traceback.print_exc())
            self.mainloop = self.crashed_mainloop(e)

    def load_mainloop(self):
        if self.missing_requirements:
            loop = self.install_mainloop()
        else:
            try:
                loop = get_mainloop(self.challenge, self.entry)
            except Exception as e:
                loop = self.crashed_mainloop(e)

        return loop

    def handle_events(self, events):
        if not self.mainloop:
            self.mainloop = self.load_mainloop()

        self.mainloop_next(events)

    def modify_mouse_pos(self, pos):
        return (
            (pos[0] - self.rect.x) * self.virtual_screen.get_width() // self.rect.w,
            (pos[1] - self.rect.y) * self.virtual_screen.get_height() // self.rect.h,
        )

    def modify_mouse_rel(self, pos):
        return (
            (pos[0]) * self.virtual_screen.get_width() // self.rect.width,
            (pos[1]) * self.virtual_screen.get_height() // self.rect.height,
        )

    def modify_events(self, events):
        for event in events:
            # We don't modify events as they may be used by other EmbeddedApps.
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                yield pygame.event.Event(
                    event.type,
                    button=event.button,
                    pos=self.modify_mouse_pos(event.pos),
                )
            elif event.type == pygame.MOUSEMOTION:
                yield pygame.event.Event(
                    event.type,
                    buttons=event.buttons,
                    pos=self.modify_mouse_pos(event.pos),
                    rel=self.modify_mouse_rel(event.rel),
                )
            else:
                yield event

    def draw(self, screen: pygame.Surface):
        if not self.mainloop:
            return

        if self.rect.size != self.virtual_screen.get_size():
            pygame.transform.smoothscale(
                self.virtual_screen, self.rect.size, screen.subsurface(self.rect)
            )
        else:
            screen.blit(self.virtual_screen, self.rect)

    def install_mainloop(self):
        w, h = SIZE
        install_rect = pygame.Rect(0, 0, 600, 100)
        install_rect.midbottom = (w / 2, h - 100)
        mouse = (0, 0)
        installing = False
        install_thread = None
        timer = 0
        clock = pygame.time.Clock()

        while True:
            timer += 1
            clock.tick(60)
            screen, events = yield

            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    mouse = event.pos
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and install_rect.collidepoint(mouse)
                    and not installing
                ):
                    installing = True
                    install_thread = Thread(
                        target=install_missing_requirements,
                        args=(self.challenge, self.entry),
                    )
                    install_thread.start()

            screen.fill("#272822")
            t = text("Missing requirements:", "white", 90)
            r = screen.blit(t, t.get_rect(midtop=(w / 2, 50)))

            for req in self.missing_requirements:
                t = text(req, "white", 72)
                r.top += 30
                r = screen.blit(t, t.get_rect(midtop=r.midbottom))

            # install button
            if install_rect.collidepoint(mouse):
                color = "#6B9BAC"
            else:
                color = "#4B7B8C"
            pygame.draw.rect(screen, color, install_rect, border_radius=10)
            # Button text
            txt = (
                "Install via pip"
                if not installing
                else "Installing" + "." * (timer // 30 % 4)
            )
            t = text(txt, "white", 80)
            screen.blit(t, t.get_rect(center=install_rect.center))

            # installation finished!
            if installing and not install_thread.is_alive():
                self.mainloop = None
                self.missing_requirements = get_missing_requirements(
                    self.challenge, self.entry
                )
                print("Still missing after install:", self.missing_requirements)
                return

    def crashed_mainloop(self, error):
        print(error)
        print(traceback.print_exc())
        screen, events = yield

        t = text(f"Crashed: {error}", "red", 30)
        r = screen.blit(t, t.get_rect(center=screen.get_rect().center))
        t = text("Check the console for details.", "red", 30)
        screen.blit(t, t.get_rect(midtop=r.midbottom))

        while True:
            # Do nothing.
            screen, events = yield
