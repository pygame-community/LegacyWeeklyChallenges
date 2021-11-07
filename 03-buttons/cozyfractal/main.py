import sys
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from time import time
from typing import Callable

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

BACKGROUND = 0xFFF0F2
ButtonCallback = Callable[["Button"], None]


class ButtonStyle:
    def __init__(
        self, text_color="black", bg_color="white", icon: pygame.Surface = None, icon_padding=10
    ):
        self.text_color = text_color
        self.bg_color = pygame.Color(bg_color)
        self.icon = auto_crop(icon) if icon else None
        self.icon_padding = icon_padding

    def get_button_bg(self, button):
        bg = pygame.Surface(button.rect.size)

        if button.hovered:
            color = self.bg_color.lerp((0, 0, 0), 0.2)
        else:
            color = self.bg_color
        bg.fill(color)
        return bg

    def get_button_surf(self, button: "Button"):
        bg = self.get_button_bg(button)
        bg_rect = bg.get_rect()

        t = auto_crop(text(button.text, self.text_color))
        if self.icon is None:
            bg.blit(t, t.get_rect(center=bg_rect.center))
        else:
            icon_rect = self.icon.get_rect()
            icon_rect.inflate_ip(self.icon_padding, 0)
            text_rect = t.get_rect(midleft=icon_rect.midright)
            both_rect = icon_rect.union(text_rect)
            both_rect.center = bg_rect.center
            icon_rect.midleft = both_rect.midleft
            text_rect.midright = both_rect.midright
            bg.blit(self.icon, icon_rect)
            bg.blit(self.icon, icon_rect)
            bg.blit(t, text_rect)

            # for rect in (both_rect, icon_rect, text_rect):
            #     pygame.draw.rect(bg, "purple", rect, 1)
        return bg


class NinePatchStyle(ButtonStyle):
    def __init__(
        self,
        background: pygame.Surface,
        text_color="black",
        icon: pygame.Surface = None,
        icon_padding=10,
    ):
        self.background = background
        super().__init__(text_color, "black", icon, icon_padding)

    def get_button_bg(self, button):
        return ninepatch(self.background, button.rect.size)


class Button:
    CLICK_ANIM_DURATION = 0.2
    DOUBLE_CLICK_TIME = 0.2

    def __init__(
        self,
        rect,
        text,
        style: ButtonStyle,
        callback: ButtonCallback,
        double_click: ButtonCallback = None,
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.style = style
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

        # Fire the double click callback, and prevent the single from happening
        self.callback_called = False
        if self.callback_double_click and now - self.last_click < self.DOUBLE_CLICK_TIME:
            self.callback_called = True
            self.callback_double_click(self)

        self.last_click = now
        self.last_click_pos = pos
        self.is_pressed = True
        if self.callback_double_click is None:
            self.callback(self)

    def logic(self):
        if self.callback_double_click:
            if self.last_click < time() - self.DOUBLE_CLICK_TIME and not self.callback_called:
                self.callback(self)
                self.callback_called = True

    def draw(self, screen: pygame.Surface):
        surf = self.style.get_button_surf(self)
        screen.blit(surf, self.rect)

        # Draw light circle animation when click
        time_since_last_click = time() - self.last_click
        if time_since_last_click < self.CLICK_ANIM_DURATION or self.is_pressed:
            circle_surface = self.get_click_circle(time_since_last_click)
            screen.blit(circle_surface, self.rect)

    def get_click_circle(self, anim_time):
        circle_surface = pygame.Surface(self.rect.size)
        radius = min(1, anim_time / self.CLICK_ANIM_DURATION) * radius_to_cover_rectangle(
            self.last_click_pos, self.rect
        )
        pygame.draw.circle(
            circle_surface,
            "white",
            pygame.Vector2(self.last_click_pos) - self.rect.topleft,
            radius,
        )
        circle_surface.set_alpha(42)

        return circle_surface


def mainloop():
    pygame.init()

    dark_theme = False
    no_style = ButtonStyle("red", "white", load_image("x"))
    yes_style = ButtonStyle("green", "white", load_image("check"))
    click_me_style = NinePatchStyle(load_image("button"))

    def callback(button):
        if button.style is no_style:
            button.style = yes_style
            button.text = "Yes"
        else:
            button.style = no_style
            button.text = "No"

    def double_click(*args):
        nonlocal dark_theme

        dark_theme = not dark_theme

        for style in [no_style, yes_style]:
            style.bg_color = pygame.Color(42, 42, 42) if dark_theme else pygame.Color(230, 230, 230)

    buttons = [
        Button((SIZE[0] / 2 - 100, SIZE[1] / 2 - 30, 200, 100), "Click me!", click_me_style, print),
        Button((20, 20, 100, 50), "yes", yes_style, callback, double_click),
        Button((200, 20, 100, 50), "yes", yes_style, callback, double_click),
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
