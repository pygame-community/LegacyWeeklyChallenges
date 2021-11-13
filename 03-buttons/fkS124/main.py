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
__author__ = "fkS#2984"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    # "Adventurous",
]

import pygame
from .app import App

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

BACKGROUND = 0xEEEEEE


def mainloop():
    pygame.init()

    app = App()

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            app.handle_events(event)

        screen.fill(BACKGROUND)

        # I centralized all the app inside the app class to permit more
        # adjustements.
        app.update(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
