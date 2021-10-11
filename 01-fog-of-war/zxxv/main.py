import sys
from pathlib import Path
from functools import partial

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
__author__ = "zxxv#1547"
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    # "Adventurous",
]


from operator import attrgetter
import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C
FOG_COLOR = (0, 0, 0, 0)


class Game:
    '''
    Game object to control updating object initialization, logic updates, and drawing the fog.
    '''
    def __init__(self):
        self.players = [Player((100, 100), 200, 'arrow'), Player((400, 400), 200, 'wasd')]
        self.trees = SolidObject.generate_many(36)
        self.ghosts = [Ghost() for _ in range(16)]

        self.all_objects = self.ghosts + self.trees + self.players 

        self.fog_surface = pygame.Surface(wclib.SIZE)
        self.fog_surface.fill(FOG_COLOR)
    
    def update(self, screen, events):
        # Logic
        for obj in self.all_objects:
            obj.logic(objects=self.all_objects)
        
        # Draw
        screen.fill(BACKGROUND)
        for object in sorted(self.all_objects, key=attrgetter("rect.bottom")):
            object.draw(screen)
        self.draw_fog(screen)

    def draw_fog(self, screen):
        self.fog_surface.fill(FOG_COLOR)
        k = 100
        for i in range(k):
            for player in self.players:
            # for i in range(k):
                pygame.draw.circle(self.fog_surface, ((255//k)*i, (255//k)*i, (255//k)*i, 50), player.center_pos, player.radius - i)
        for tree in self.trees:
            tree.draw(self.fog_surface)
        screen.blit(self.fog_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    

def mainloop():
    # player = Player((100, 100))
    # trees = SolidObject.generate_many(36)
    # ghosts = [Ghost() for _ in range(16)]

    # all_objects = trees + [player] + ghosts
    game = Game()
    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        game.update(screen, events)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
