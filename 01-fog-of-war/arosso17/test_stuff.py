import sys
from pathlib import Path
import numpy as np

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
__author__ = "treehuggerbear1#2361"
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
from .utils import load_image
import random

BACKGROUND = 0x66856C

def dist(pos, other):
    return np.sqrt((pos[0]-other[0])**2 + (pos[1]-other[1])**2)

def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    houses = []
    wells = []
    dead_trees = []
    bushes = []
    for obj in trees:
        if obj.rect[2] == 144:
            houses.append(obj)
        elif obj.rect[2] == 48 and obj.rect[3] == 72:
            wells.append(obj)
        elif obj.rect[2] == 72 and (obj.rect[3] == 93 or obj.rect[3] == 72):
            dead_trees.append(obj)
        elif obj.rect[2] == 48 and obj.rect[3] == 48:
            bushes.append(obj)
    ghosts = [Ghost() for _ in range(16)]
    all_objects = trees + [player]
    clock = pygame.time.Clock()
    first = True
    FPS = 60
    # 1024 x 768
    while True:
        screen, events = yield
        # would put outside loop, but weird showcase stuff messes up
        if first:
            # for pic
            fog = load_image("fog")
            fog.set_alpha(25)

            lights = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            fog_of_war = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            explored_map = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.rect(explored_map, (0, 0, 0, 255), [0, 0, screen.get_width(), screen.get_height()])

            for obj in trees:
                if obj.rect[2] == 144:
                    pygame.draw.circle(lights, (234, 206, 9, 15),
                                       (obj.rect[0] + 32, obj.rect[1] + 94), 45, 20)
                    pygame.draw.circle(lights, (234, 206, 9, 15),
                                       (obj.rect[0] - 32 + obj.rect[2], obj.rect[1] + 94), 45, 20)
                    pygame.draw.circle(lights, (234, 206, 9, 40),
                                       (obj.rect[0] + 32, obj.rect[1] + 94), 25)
                    pygame.draw.circle(lights, (234, 206, 9, 40),
                                       (obj.rect[0] - 32 + obj.rect[2], obj.rect[1] + 94), 25)
                    pygame.draw.rect(lights, (234, 206, 9, 150),
                                     (obj.rect[0] + 21, obj.rect[1] + 84, 21, 18))
                    pygame.draw.rect(lights, (234, 206, 9, 150),
                                     (obj.rect[0] - 45 + obj.rect[2], obj.rect[1] + 84, 21, 18))
            # for pic
            explored_map.blit(fog, (0, 0))
            pygame.draw.rect(fog_of_war, (0, 0, 0, 150), [0, 0, screen.get_width(), screen.get_height()])
            first = False
        for event in events:
            if event.type == pygame.QUIT:
                return
        for obj in all_objects:
            obj.logic(objects=all_objects)
        screen.fill(BACKGROUND)
        for object in sorted(all_objects, key=attrgetter("rect.bottom")):
            object.draw(screen)
        screen.blit(lights, (0, 0))
        screen.blit(fog_of_war, (0, 0))

        # for ghost in ghosts:
        #     ghost.logic()
        #     dis = dist(ghost.pos, player.pos)
        #     if dis < 175:
        #         ghost.draw(screen)

        for ghost in ghosts:
            ghost.logic()
            dis = dist(ghost.pos, player.pos)
            if dis < 200:
                ghost.sprite.set_alpha(255)
                if dis > 100:
                    ghost.sprite.set_alpha(355 - (355/150)*dis)
                ghost.draw(screen)

        screen.blit(explored_map, (0, 0))
        for i in range(0, 150, 2):
            pygame.draw.circle(fog_of_war, (0, 0, 0, i),
                               (player.pos[0] + player.size[0] / 2, player.pos[1] + player.size[1] / 2), i + 50, 2)
        pygame.draw.circle(fog_of_war, (0, 0, 0, 0),
                           (player.pos[0] + player.size[0] / 2, player.pos[1] + player.size[1] / 2), 50)
        pygame.draw.circle(explored_map, (0, 0, 0, 150), [player.pos[0] + player.size[0] / 2, player.pos[1] + player.size[1] / 2], 150)
        clock.tick(FPS)
        print(clock.get_fps())

if __name__ == "__main__":
    wclib.run(mainloop())
