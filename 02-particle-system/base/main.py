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
__package__ = "02-particle-system." + Path(__file__).parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "CozyFractal#0042"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]


from operator import attrgetter
import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import *

BACKGROUND = 0x66856C


def mainloop():
    player = Player((100, 100), (0, 0))

    objects = {player} | Asteroid.generate_many()

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        dead = set()
        new_objects = set()
        for obj in objects:
            obj.logic(events=events, objects=objects, new_objects=new_objects)
            if not obj.alive:
                dead.add(obj)
        objects.difference_update(dead)
        objects.update(new_objects)

        screen.fill(BACKGROUND)
        # for object in sorted(objects, key=attrgetter("rect.bottom")):
        for obj in objects:
            obj.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
