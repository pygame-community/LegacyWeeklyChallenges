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
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C


def draw_circle(fog, pos, radius, fading_value):
    for i in range(fading_value, -1, -1):
        c = int(255 - i * (255 / fading_value))
        color = (c, c, c)
        pygame.draw.circle(fog, color, pos, radius + i * 2)


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + [player] + ghosts

    fog = pygame.Surface(wclib.SIZE)
    fog.fill((0, 0, 0))

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
        fog.fill((0, 0, 0))
        pos = (player.pos[0] + player.size[0] // 2, player.pos[1] + player.size[1] // 2)
        draw_circle(fog, pos, player.size[0], 100)
        screen.blit(fog, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
