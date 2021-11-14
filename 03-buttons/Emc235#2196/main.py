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

import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *
from .button import Button

BACKGROUND = 0x0F1012


# This is a suggestion of the interface of the button class.
# There are many other ways to do it, but I strongly suggest to
# at least use a class, so that it is more reusable.


def mainloop():
    pygame.init()

    sprite = pygame.surface.Surface((250, 100))
    sprite.fill((255, 255, 255))
    hover_sprite = pygame.surface.Surface((250, 100))
    hover_sprite.fill((200, 200, 200))

    buttons = [
        Button(
            pygame.math.Vector2(SIZE) // 2,
            (250, 100),
            anchor="center",
            bg_clr=(30, 30, 30),
            text="click me!",
            font_size=40,
            text_clr=(0, 0, 0),
            border_radius=60,
            on_click=lambda: print("Clicked!"),
            sprite=sprite,
            hover_sprite=hover_sprite,
        ),
        Button(
            (5, 5),
            (350, 100),
            anchor="topleft",
            bg_clr=(30, 30, 30),
            text=" Double click me!",
            font_size=40,
            border_radius=60,
            on_click=lambda: print("Double Clicked!"),
            double_click=True,
            double_click_limit=300,
        )
        # Define more buttons here when you have one working!
        # With different styles, behavior, or whatever cool stuff you made :D
    ]

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for button in buttons:
            button.event_handler(events, clock)

        screen.fill(BACKGROUND)
        for button in buttons:
            button.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
