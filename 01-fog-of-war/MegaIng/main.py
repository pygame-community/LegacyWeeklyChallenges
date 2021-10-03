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
__author__ = "MegaIng4572#7777"
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


class FogOverlay:
    def __init__(self, player: Player, view_radii: tuple[int, int], steps: int):
        self.player = player
        self.view_radii = view_radii
        self.steps = steps
        self.active_overlay: pygame.Surface = pygame.Surface(wclib.SIZE, pygame.SRCALPHA)
        self.passive_overlay: pygame.Surface = pygame.Surface(wclib.SIZE, pygame.SRCALPHA)
        self.passive_overlay.fill((0, 0, 0, 255))

    def update_overlays(self):
        self.active_overlay.fill((0, 0, 0, 255))  # Solid black
        center = self.player.pos + self.player.size / 2  # Center on player, looks slightly better than topleft
        for radius, alpha in (
                (self.view_radii[0] + (self.view_radii[1] - self.view_radii[0]) * i / self.steps,
                 255 * i / self.steps
                 )
                for i in reversed(range(self.steps))
        ):
            pygame.draw.circle(self.active_overlay, (0, 0, 0, alpha),
                               center,
                               radius)
        self.passive_overlay.fill((0, 0, 0, 200), special_flags=pygame.BLEND_RGBA_MAX)
        self.passive_overlay.blit(self.active_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def mainloop():
    player = Player((100, 100))
    fog = FogOverlay(player, (100, 300), 100)
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
        fog.update_overlays()

        screen.fill(BACKGROUND)
        for obj in sorted(all_objects, key=attrgetter("rect.bottom")):
            obj.draw(screen)
        screen.blit(fog.active_overlay, (0, 0))
        for obj in sorted(trees, key=attrgetter("rect.bottom")):
            obj.draw(screen)
        screen.blit(fog.passive_overlay, (0, 0))

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
