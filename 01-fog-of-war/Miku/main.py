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
__author__ = 'await ctx.send("Miku")#7006'
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]


from operator import attrgetter
import pygame

pygame.init()

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C

fog_size = 35
fogs = [
    pygame.Surface((fog_size, fog_size), pygame.SRCALPHA),
    pygame.Surface((1024, 768), pygame.SRCALPHA),
]
fog_x, fog_y = 1024 / fog_size, 768 / fog_size
fps_font = pygame.font.SysFont("Bold", 50)
fogs[0].fill((20, 20, 20, 255))
fogs[1].fill((20, 20, 20, 220))
# first fog is completely black, second is gray

# generates a light
def draw_light(radius, quality):
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    loop_count, color_change = 25 * quality, 8 / quality
    for i in range(loop_count):
        pygame.draw.circle(
            surface,
            (20, 20, 20, 220 - i * color_change),
            (radius, radius),
            radius - i * 2,
        )
    return surface


def mainloop():
    player = Player((100, 100))
    last_player_position = [100, 100]
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    light_r = 150
    light_rect = pygame.Rect(0, 0, light_r * 2, light_r * 2)
    light = draw_light(light_r, 12)
    # Dont pass a number higher than 12

    all_objects = trees + [player] + ghosts

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)
        # creates a fog area
        if last_player_position != player.rect.topleft:
            light_rect.center = player.rect.center
            position = (player.rect.center[0] / fog_x, player.rect.center[1] / fog_y)
            pygame.draw.circle(fogs[0], (0, 0, 0, 0), position, light_r / fog_x)
        last_player_position = player.rect.topleft

        screen.fill(BACKGROUND)
        for object in sorted(all_objects, key=attrgetter("rect.bottom")):
            if getattr(object, "SHEET", None) != "pink_ghost":
                object.draw(screen)
            else:
                if object.rect.colliderect(light_rect):
                    object.draw(screen, light_rect.center, light_r)

        # draws a fog
        fog = pygame.Surface.copy(fogs[1])
        fog2 = fogs[0]
        fog2 = pygame.transform.smoothscale(fog2, (1024, 768))
        fog.blit(fog2, (0, 0))
        pygame.draw.circle(fog, (0, 0, 0, 0), player.rect.center, light_r)
        screen.blit(fog, (0, 0))
        screen.blit(light, (player.rect.center[0] - light_r, player.rect.center[1] - light_r))
        # draws a fog

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
