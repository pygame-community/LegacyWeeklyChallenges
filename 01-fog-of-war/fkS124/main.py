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
__author__ = "fkS#2984"
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    "Adventurous",
]


from operator import attrgetter
import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C


def draw_gradient(surf, pos, radius, dep_alpha):
    for i in range(20, 0, -1):
        pygame.draw.circle(
            surf, (0, 0, 0, dep_alpha - (-i) * 7), pos, int(radius * i / 20)
        )


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + [player] + ghosts

    clock = pygame.time.Clock()

    radius = 150
    surf = pygame.Surface((1024, 768), pygame.SRCALPHA)
    surf.fill((0, 0, 0))
    second_surf = pygame.Surface((1024, 768), pygame.SRCALPHA)
    second_surf.fill((0, 0, 0))
    second_surf.set_alpha(180)
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)

        screen.fill(BACKGROUND)
        for object in sorted(all_objects, key=attrgetter("rect.bottom")):
            if type(object) is Ghost:
                if object.pos.distance_to(player.pos) < radius:
                    object.draw(screen)
            else:
                object.draw(screen)

        second_surf.fill((0, 0, 0))

        pygame.draw.circle(
            surf, (0, 0, 0, 0), player.pos + pygame.Vector2(20, 20), radius
        )
        draw_gradient(second_surf, player.pos + pygame.Vector2(20, 20), radius, 100)
        screen.blit(second_surf, (0, 0))
        screen.blit(surf, (0, 0))
        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
