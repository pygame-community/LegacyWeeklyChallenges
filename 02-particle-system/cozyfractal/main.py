import random
import sys
from pathlib import Path

import numpy as np
import pygame.gfxdraw

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
__package__ = "02-particle-system." + Path(__file__).parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "CozyFractal#0042"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .objects import *
from .utils import *
from .particles import *

BACKGROUND = 0x0F1012


def mainloop():
    pygame.init()

    # player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))
    # The state is just a collection of all the objects in the game
    state = State(FpsCounter(60))
    # state = State(player, FpsCounter(60), *Asteroid.generate_many())

    # p = ParticleGroup(
    #     1000,
    #     100,
    #     MovePolar(),
    #     AngularVel(0.8),
    #     VelocityCircle(),
    #     WrapScreenTorus(),
    # continuous=True,
    # pos=np.array(SIZE) / 2,
    # speed=Gauss(5, 0.1),
    # angle=Uniform(0, 360),
    # color=Constant(np.array([0, 0, 0])),
    # )
    mouse_generator = MousePosGenerator()

    class Fountain(ParticleGroup, MoveCartesian, BounceRect, Gravity, VelocityCircle):
        continuous = True
        nb = 5000
        max_age = 300
        gravity = (0, 0.1)
        wrap_rect = (0, 0, *SIZE)
        bounce_limits = (100, 100, SIZE[0] - 100, SIZE[1] - 100)

        velocity = Gauss((0, -8), (0.3, 0.2))
        pos = mouse_generator

    class Fireworks(ParticleGroup, MovePolar, Circle, Friction):
        nb = 1000
        max_age = 100
        gravity = (0, 0.1)
        gradient = "#FFF75D", "#FE650DA0", "#A1010000"
        # gradient = "red", "yellow", (255, 165, 0, 0)
        angle = Uniform(0, 360)
        speed = Gauss(8)
        pos = mouse_generator

        friction = 0.98
        bounce_limits = (0, 0, SIZE)

        interpolations = {"speed": (5, 0)}

    state.add(Fountain())

    frame = 1
    while True:
        frame += 1

        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    state.add(Fireworks())

            state.handle_event(event)
            mouse_generator.handle_event(event)

        if random.random() < 0.01:
            state.add(Fireworks())

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()

        screen.fill(BACKGROUND)
        state.draw(screen)


if __name__ == "__main__":
    wclib.run(mainloop())
