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

from operator import attrgetter
import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject, Fog, Menu

BACKGROUND = 0x66856C


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]
    fog = Fog(player.rect)
    menu = Menu()

    all_objects = trees + ghosts + [player, menu]

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            menu.handle_event(event)

        for obj in all_objects:
            obj.logic(objects=all_objects)
        fog.logic(player, menu)
        menu.logic()

        # screen.fill(BACKGROUND)
        # for object in sorted(all_objects, key=attrgetter("rect.bottom")):
        #    object.draw(screen)
        fog.draw(screen, all_objects)
        menu.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
