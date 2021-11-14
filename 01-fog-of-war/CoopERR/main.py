import sys
from pathlib import Path

from pygame.constants import SRCALPHA

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
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + [player] + ghosts
    solid_objects = trees + [player]

    fog = pygame.surface.Surface(pygame.display.get_surface().get_size(), pygame.SRCALPHA)
    fog.fill((0, 0, 0))

    def field_of_view():
        size = 150
        for i in range(200, 0, -1):
            pygame.draw.circle(fog, (0, 0, 0, i), player.rect.center, size)
            size -= 0.9

    def ghost_distance(ghost):
        distance_x = player.rect.center[0] - ghost.rect.center[0]
        distance_y = player.rect.center[1] - ghost.rect.center[1]

        return (abs(distance_x) + abs(distance_y)) < 150

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)

        screen.fill(BACKGROUND)

        for ghost in sorted(ghosts, key=attrgetter("rect.bottom")):
            if ghost_distance(ghost):
                ghost.draw(screen)
        for object in sorted(solid_objects, key=attrgetter("rect.bottom")):
            object.draw(screen)

        field_of_view()
        screen.blit(fog, (0, 0))

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
