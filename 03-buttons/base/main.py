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
__author__ = "CozyFractal#0042"  # Put yours!
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


# This is a suggestion of the interface of the button class.
# There are many other ways to do it, but I strongly suggest to
# at least use a class, so that it is more reusable.
class Button:
    def __init__(self, position, size, content: str):  # Just an example!
        self.position = position
        self.size = size
        self.content = content

    def handle_event(self, event: pygame.event.Event):
        # Use this to update the state of the button according to user inputs.
        # It is usually a good idea to have this separated from the rest according
        # to the principle of separation of concerns.
        ...

    def draw(self, screen: pygame.Surface):
        # Use this to draw the button on the screen
        # As a placeholder, I draw its content, but it may be more complex
        # when you do it. Maybe you use images, maybe likely some background,
        # maybe some border and even shadows ?
        t = text(self.content, "orange")
        screen.blit(t, self.position)


def mainloop():
    pygame.init()

    buttons = [
        Button((20, 20), (200, 60), "Click me!"),
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
                button.handle_event(event)

        screen.fill(BACKGROUND)
        for button in buttons:
            button.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
