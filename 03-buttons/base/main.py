import sys
from pathlib import Path
from time import time

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "03-buttons." + Path(__file__).absolute().parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "CozyFractal#6978"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

BACKGROUND = 0x0F1012


class Button:
    CLICK_ANIM_DURATION = 0.2
    DOUBLE_CLICK_TIME = 0.2

    def __init__(self, rect, text, text_color, bg_color, callback, double_click=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.text_color = text_color
        self.bg_color = pygame.Color(bg_color)
        self.callback = callback
        self.callback_double_click = double_click

        self._hovered = False
        self.last_click = -1
        self.last_click_pos = (0, 0)
        self.is_pressed = False
        # Only used when there is a double click
        self.callback_called = True

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        if value != self._hovered:
            self._hovered = value

            if value:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            if not self.hovered:
                self.is_pressed = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.click(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False

    def click(self, pos):
        now = time()
        self.callback_called = False
        if self.callback_double_click and now - self.last_click < self.DOUBLE_CLICK_TIME:
            self.callback_called = True
            self.callback_double_click()
        self.last_click = now
        self.last_click_pos = pos
        self.is_pressed = True
        if self.callback_double_click is None:
            self.callback(12)

    def logic(self):
        if self.callback_double_click:
            if self.last_click < time() - self.DOUBLE_CLICK_TIME and not self.callback_called:
                self.callback()
                self.callback_called = True

    def draw(self, screen: pygame.Surface):
        if self.hovered:
            color = self.bg_color.lerp((0, 0, 0), 0.2)
        else:
            color = self.bg_color
        screen.fill(color, self.rect)

        now = time()
        time_since_last_click = now - self.last_click
        if time_since_last_click < self.CLICK_ANIM_DURATION or self.is_pressed:
            circle_surface = pygame.Surface(self.rect.size)
            radius = (time_since_last_click / self.CLICK_ANIM_DURATION) * radius_to_cover_rectangle(
                self.last_click_pos, self.rect
            )
            pygame.draw.circle(
                circle_surface,
                "white",
                pygame.Vector2(self.last_click_pos) - self.rect.topleft,
                radius,
            )
            circle_surface.set_alpha(42)
            screen.blit(circle_surface, self.rect)

        t = text(self.text, self.text_color)
        screen.blit(t, t.get_rect(center=self.rect.center))


def mainloop():
    pygame.init()

    def callback(*args):
        b = buttons[1]
        if b.text == "Yes":
            b.text = "No"
            b.text_color = "red"
        else:
            b.text = "Yes"
            b.text_color = "green"

    def double_click(*args):
        c = buttons[1].bg_color
        if c == (255, 255, 255, 255):
            c.update(0, 0, 0, 255)
        else:
            c.update(255, 255, 255, 255)

    buttons = [
        Button(
            (SIZE[0] / 2 - 100, SIZE[1] / 2 - 30, 200, 60), "Click me!", "#eeeeee", "blue", print
        ),
        Button((20, 20, 50, 200), "ok", "green", "white", callback, double_click)
        # Define more buttons here when you have one working!
        # With different styles, behavior, or whatever cool stuff you made :D
    ]
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            for button in buttons:
                button.handle_event(event)

        for button in buttons:
            button.logic()

        screen.fill(BACKGROUND)
        for button in buttons:
            button.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
