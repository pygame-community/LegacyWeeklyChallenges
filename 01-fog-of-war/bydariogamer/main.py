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
__author__ = "bydariogamer#7949"
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


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + [player] + ghosts

    clock = pygame.time.Clock()

    # surface containing a circle with faded borders
    light = pygame.Surface((200, 200), pygame.SRCALPHA)
    light.fill((255, 255, 255, 0))
    for i in range(100):
        pygame.draw.circle(light, 3*[0]+[i], (100, 100), 100-i)

    # how slowly we want fog to come back
    fog_persistance = 4
    fog_count = 0

    # surface containing the fog
    dark = pygame.Surface(wclib.SIZE, pygame.SRCALPHA)
    dark.fill((0, 0, 0, 255))

    while True:
        # yield screen and process events
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        # run the logic of all objects
        for obj in all_objects:
            obj.logic(objects=all_objects)

        # fill screen with background color
        screen.fill(BACKGROUND)

        # make ghosts disappear if they are out of player view range
        for ghost in ghosts:
            ghost.sprite.set_alpha((120 - ghost.pos.distance_to(player.pos))*4)

        # draw all objects
        for obj in sorted(all_objects, key=attrgetter("rect.bottom")):
            obj.draw(screen)

        # light up player surroundings
        dark.blit(light, player.pos - (76, 76), special_flags=pygame.BLEND_RGBA_SUB)

        # make fog slowly come back
        fog_count += 1
        fog_count %= fog_persistance
        if not fog_count:
            dark.fill((0, 0, 0, 1), special_flags=pygame.BLEND_RGBA_ADD)

        # blit the fog
        screen.blit(dark, (0, 0))
        if __name__ == "__main__":
            pygame.display.set_caption(f"{__author__}'s fog of war   -   {int(clock.get_fps())}/60FPS")
        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
