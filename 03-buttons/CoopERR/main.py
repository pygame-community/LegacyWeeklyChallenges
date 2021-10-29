import sys, os
from pathlib import Path

import achievement

from pygame.constants import MOUSEBUTTONDOWN

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "03-buttons." + Path(__file__).absolute().parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "CoopERR"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

BACKGROUND = 0x0F1012


# This is a suggestion of the interface of the button class.
# There are many other ways to do it, but I strongly suggest to
# at least use a class, so that it is more reusable.

class Button:
    def __init__(self, position, size, content=None, sound=None, colour=(255,255,255), border_radius=0):
        self.position = position
        self.size = size
        self.content = content
        self.colour = colour
        self.highlight_colour = self.get_highlight_colour()
        self.sound = sound
        self.border_radius = border_radius
        self.button = self.create_button()
        self.rect = self.button.get_rect(topleft=self.position)
        self.highlight = False
        self.clicked = False
        self.double_clicked = False
        self.achievement = False

    def get_highlight_colour(self):
        HIGHLIGHT_FACTOR = 50
        l = [y+HIGHLIGHT_FACTOR for y in self.colour]
        m = [255 if y > 255 else y for y in l]
        return tuple(m)

    def create_button(self):
        button = pygame.Surface((self.size[0]+10, self.size[1]+10)).convert_alpha()
        button.fill((0,0,0,0))

        return button

    def handle_event(self, event: pygame.event.Event, double_click):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.highlight = True
        else:
            self.highlight = False

        if self.rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
            if double_click:
                self.double_clicked = True
            self.clicked = True
            self.achievement = True
        else:
            self.clicked = False
            self.double_clicked = False

    def get_achievement(self):
        self.achievement = True
            
    def draw(self, screen: pygame.Surface):
        if self.highlight:
            colour = self.highlight_colour
        else:
            colour = self.colour

        pygame.draw.rect(self.button, (0,0,0,255), (3,3,self.size[0],self.size[1]), border_radius=self.border_radius)
        pygame.draw.rect(self.button, colour, (0,0,self.size[0],self.size[1]), border_radius=self.border_radius)

        screen.blit(self.button, self.position)
        if self.content:
            t = text(self.content, "black")
            t_rect = t.get_rect()
            screen.blit(t, (self.rect.centerx - t_rect.centerx, self.rect.centery - t_rect.centery))
        


def mainloop():
    pygame.init()

    buttons = [
        Button((400, 400), (100, 50), colour=(0,0,255), content="hello", border_radius=20 ),
        Button((100, 100), (200, 200), colour=(255,0,255), content="goodbye", border_radius=50 ),
        Button((600, 550), (80, 140), colour=(120,120,255), content="ugh", border_radius=5 )
        # Define more buttons here when you have one working!
        # With different styles, behavior, or whatever cool stuff you made :D
    ]

    path = SUBMISSION_DIR / "assets" / "click"
    frames = []

    for file_name in os.listdir(path):
        image = load_image(file_name, scale=5, base=path)
        frames.append(image)

    click_achievement = achievement.Achievement((0,0), frames)
    sprites = pygame.sprite.Group(click_achievement)

    achi = False

    timer = 0
    dt = 0
    double_click = False

    def draw_achi(screen):
        sprites.update()
        print(sprites)
        sprites.draw(screen)

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if timer == 0:
                    double_click = False
                    timer = 0.001
                elif timer < 0.5:
                    double_click = True
                    timer = 0
            if event.type == pygame.QUIT:
                return

            for button in buttons:
                button.handle_event(event, double_click)

        screen.fill(BACKGROUND)
        for button in buttons:
            button.draw(screen)

            if button.achievement:
                achi = True

        if achi:
            draw_achi(screen)

        clock.tick(60)

        if timer != 0:
            timer += dt
        if timer >= 0.5:
            timer = 0
        dt = clock.tick(60) / 1000



if __name__ == "__main__":
    wclib.run(mainloop())
