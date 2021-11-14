import math
import sys
from pathlib import Path
from typing import Sequence

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
from .objects import Ghost, Player, SolidObject, Object

BACKGROUND = 0x66856C
SCREEN_SIZE = (1024, 768)
CHUNK_SIZE = (16, 16)
NUMBER_HORIZONTAL_CHUNKS = SCREEN_SIZE[0] // CHUNK_SIZE[0]
NUMBER_VERTICAL_CHUNKS = SCREEN_SIZE[1] // CHUNK_SIZE[1]
MAX_DARKNESS_LEVEL = 210


def generate_light(player):
    light = pygame.Surface((SCREEN_SIZE[0] * 2.2, SCREEN_SIZE[1] * 2.2), pygame.SRCALPHA)
    for opacity_level in range(0, MAX_DARKNESS_LEVEL, 5):
        pygame.draw.circle(
            light,
            (0, 0, 0, opacity_level),
            light.get_rect().center,
            player.VISION_RADIUS,
            int(player.VISION_RADIUS * (1 - opacity_level / MAX_DARKNESS_LEVEL)),
        )
    pygame.draw.circle(
        light,
        (0, 0, 0, MAX_DARKNESS_LEVEL),
        light.get_rect().center,
        light.get_width(),
        light.get_width() - player.VISION_RADIUS,
    )
    return light


def update_unvisited_chunks(player, unvisited_chunks):
    for chunk in set(unvisited_chunks):
        chunk_rect = pygame.rect.Rect(
            chunk[0] * CHUNK_SIZE[0],
            chunk[1] * CHUNK_SIZE[1],
            CHUNK_SIZE[0],
            CHUNK_SIZE[1],
        )
        player_distance_with_chunk = math.sqrt(
            (chunk_rect.center[0] - player.rect.center[0]) ** 2
            + (chunk_rect.center[1] - player.rect.center[1]) ** 2
        )
        if player_distance_with_chunk < player.VISION_RADIUS + chunk_rect.width // 2:
            unvisited_chunks.remove(chunk)


def display(screen, objects, player, light, unvisited_chunks):
    screen.fill(BACKGROUND)

    for element in sorted(objects, key=attrgetter("rect.bottom")):
        if (
            isinstance(element, Ghost)
            and element.pos.distance_to(player.pos) > player.VISION_RADIUS
        ):
            continue  # Don't draw ghost if it's too far, just go to the next element
        element.draw(screen)

    for chunk_position in unvisited_chunks:
        # Hide unvisited blocks
        screen.fill(
            pygame.Color("black"),
            rect=pygame.rect.Rect(
                chunk_position[0] * CHUNK_SIZE[0],
                chunk_position[1] * CHUNK_SIZE[1],
                CHUNK_SIZE[0],
                CHUNK_SIZE[1],
            ),
        )

    screen.blit(
        light,
        (
            player.rect.center[0] - light.get_width() // 2,
            player.rect.center[1] - light.get_height() // 2,
        ),
    )


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects: Sequence[Object] = trees + [player] + ghosts

    light = generate_light(player)

    unvisited_chunks = set()
    for x in range(NUMBER_HORIZONTAL_CHUNKS):
        for y in range(NUMBER_VERTICAL_CHUNKS):
            unvisited_chunks.add((x, y))

    player_chunk = (
        player.rect.center[0] // CHUNK_SIZE[0],
        player.rect.center[1] // CHUNK_SIZE[1],
    )
    if player_chunk in unvisited_chunks:
        unvisited_chunks.remove(player_chunk)

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for element in all_objects:
            element.logic(objects=all_objects)

        update_unvisited_chunks(player, unvisited_chunks)

        display(screen, all_objects, player, light, unvisited_chunks)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
