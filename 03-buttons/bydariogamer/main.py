import sys
from pathlib import Path

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
__author__ = "bydariogamer#7949"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

import pygame
import time

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *
from .particles import ParticleManager
from operator import attrgetter

pygame.mixer.init()

BACKGROUND = 0x0F1012

assets = Path(__file__).parent / "assets"


class Button:
    MULTIPLE_CLICK_INTERVAL = 0.3
    PARTICLE_MANAGER = ParticleManager()

    def __init__(
            self,
            rect,
            color=None,
            outcolor=None,
            background=None,
            image=None,
            icon=None,
            label=None,
            sound=None,
            on_click=None,
    ):
        self.rect = pygame.Rect(rect)
        self.color = pygame.Color(color) if color else None
        self.outcolor = outcolor if outcolor else self.color + pygame.Color(15, 15, 15) if color else None
        self.background = background
        self.image = image
        self.icon = icon
        self.label = label
        self.sound = sound
        self.on_click = on_click

        self.last_clicked = 0
        self.click_count = 0

    def handle_event(self, event: pygame.event.Event):
        if self.mouseover and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if time.time() - self.last_clicked < self.MULTIPLE_CLICK_INTERVAL:
                    self.click_count += 1
                else:
                    self.click_count = 1
                self.last_clicked = time.time()
                if self.on_click:
                    for function in self.on_click:
                        function(self)

    def draw(self, screen: pygame.Surface):
        if self.color:
            pygame.draw.rect(
                screen,
                self.outcolor if self.mouseover else self.color,
                self.rect
            )
        if self.image:
            blit_centered(
                screen,
                self.image,
                self.rect
            )
        if (self.icon and not self.label) or (self.icon and self.label and not self.mouseover):
            blit_centered(
                screen,
                self.icon,
                self.rect
            )
        if (self.label and not self.icon) or (self.icon and self.label and self.mouseover):
            blit_centered(
                screen,
                text(
                    self.label,
                    tuple(pygame.Color(255, 255, 255) - self.color) if self.color else tuple(
                        pygame.Color(255, 255, 255) - pygame.Color(BACKGROUND))),
                self.rect
            )

    @property
    def mouseover(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    @property
    def mouseclicking(self):
        return self.mouseover and pygame.mouse.get_pressed(num_buttons=3)[0]

    def play_sound(self):
        self.sound.play()

    def burst_particles(self):
        self.PARTICLE_MANAGER.burst(
            self.rect.center,
            pygame.Vector2(2, 0),
            color=self.color
        )

    def shoot_particles(self):
        self.PARTICLE_MANAGER.shot(
            self.rect.center,
            pygame.Vector2(20, 0),
        )

    def update_text(self):
        times = "once" if self.click_count == 1 else "twice" if self.click_count == 2 else "many times"
        self.label = "I've been clicked " + times


def mainloop():
    pygame.init()

    buttons = [
        Button(
            (20, 20, 200, 60),
            (150, 20, 20),
            label="Click!",
            sound=pygame.mixer.Sound(str(assets / "click.wav")),
            on_click=[Button.play_sound],
        ),
        Button(
            (20, 100, 200, 60),
            (150, 150, 20),
            label="Sparks!",
            on_click=[Button.shoot_particles],
        ),
        Button(
            (20, 400, 200, 300),
            (100, 100, 250),
            sound=pygame.mixer.Sound(str(assets / "click.wav")),
            icon=pygame.image.load(str(assets / "play.png")),
            label="Play",
            on_click=[Button.burst_particles, Button.play_sound],
        ),
        Button(
            (300, 500, 500, 100),
            (100, 250, 250),
            label="Click me many times",
            on_click=[Button.update_text],
        ),
    ]

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            for button in sorted(buttons, key=attrgetter("rect.right")):
                button.handle_event(event)

        Button.PARTICLE_MANAGER.logic()

        screen.fill(BACKGROUND)
        Button.PARTICLE_MANAGER.draw(screen)
        for button in sorted(buttons, key=attrgetter("rect.left")):
            button.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
