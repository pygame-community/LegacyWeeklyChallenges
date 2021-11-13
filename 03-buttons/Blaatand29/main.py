import sys
from pathlib import Path

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
__author__ = "Blaatand29#0070"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    # "Adventurous",
]

import pygame
from random import randint

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

BACKGROUND = 0x0F1012


class Button:
    def __init__(self, rect, content: str, text_color, bg_color, bg_hover_color, border_color, border_thick, action):
        self.rect = pygame.Rect(rect)
        self.content = content
        self.text_color = text_color
        self.bg_color = bg_color
        self.bg_hover_color = bg_hover_color
        self.border_color = border_color
        self.border_thick = border_thick
        self.action = action

        self.hover = False
        self.background_color = bg_color

    def handle_event(self, event: pygame.event.Event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(mouse_pos):
                self.hover = True

            else:
                self.hover = False

        if self.hover:
            self.background_color = self.bg_hover_color
        else:
            self.background_color = self.bg_color

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                if self.action == "change_own_col":
                    self.bg_color = pygame.Color((randint(0, 255), randint(0, 255), randint(0, 255)))
                    self.bg_hover_color = pygame.Color((randint(0, 255), randint(0, 255), randint(0, 255)))
                    self.border_color = pygame.Color((randint(0, 255), randint(0, 255), randint(0, 255)))

    def draw(self, screen: pygame.Surface):
        screen.fill(self.border_color, self.rect)
        screen.fill(self.background_color, self.rect.inflate(-self.border_thick * 2, -self.border_thick * 2))

        t = text(self.content, self.text_color)
        t_rect = t.get_rect(center=self.rect.center)
        screen.blit(t, t_rect)


def mainloop():
    pygame.init()

    buttons = [
        Button((200, 200, 200, 60), "Click me!", "white", "darkblue", "blue", "white", 5, "change_own_col"),
        Button((500, 300, 300, 160), "Don't click me!", "green", "red", "pink", "black", 20, "change_own_col"),
        Button((300, 400, 50, 300), "tall", "black", "darkgreen", "green", "pink", 2, "change_own_col"),

    ]

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            for button in buttons:
                button.handle_event(event)

        screen.fill(BACKGROUND)
        for button in buttons:
            button.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
