import sys
from operator import attrgetter
from pathlib import Path

import pygame

# We make sure the lib is in the path, otherwise we may not be able to import it.
ROOT_FOLDER = Path(__file__).parents[3]
sys.path.append(ROOT_FOLDER)

import lib
from objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C


def mainloop():
    player = Player((100, 100))
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

        screen.fill(BACKGROUND)
        for object in sorted(all_objects, key=attrgetter("rect.bottom")):
            object.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    lib.run(mainloop())
