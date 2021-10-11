import sys
from pathlib import Path

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "01-fog-of-war." + Path(__file__).parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "Your Discord Tag Goes Here#7777"
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]


from operator import attrgetter
import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject
from .fog import FogArea

BACKGROUND = 0x66856C


def mainloop():
    player = Player((100, 100))
    fog = FogArea(20, 20, 10)
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + [player] + ghosts

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)

        fog.logic(player)

        screen.fill(BACKGROUND)
        for obj in sorted(all_objects, key=attrgetter("rect.bottom")):
            if not isinstance(obj, Ghost) or fog.lighted_up(obj.rect.center):
                obj.draw(screen)

        fog.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
