from operator import attrgetter
import pygame
from objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C

__author__ = "Your Discord Tag Goes Here#7777"


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
    try:
        import lib
    except ImportError:
        # lib may not be in the path because of the architecture
        # of all the challenges and the fact that there are many
        # way to run them (through the shwcase, or on their own)
        import sys, pathlib

        ROOT_FOLDER = pathlib.Path(__file__).parents[3]
        sys.path.append(str(ROOT_FOLDER))
        import lib

    lib.run(mainloop())
