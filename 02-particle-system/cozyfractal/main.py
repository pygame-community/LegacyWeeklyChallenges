import random
import sys
from math import sqrt
from pathlib import Path

import numpy as np
import pygame.gfxdraw
from line_profiler_pycharm import profile

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
from . import particles

BACKGROUND = (15, 16, 17)


def mainloop():
    pygame.init()

    player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))
    # The state is just a collection of all the objects in the game
    state = State(FpsCounter(60))
    state = State(player, FpsCounter(60), *Asteroid.generate_many())

    mouse_generator = MousePosGenerator()

    class Fountain(ParticleGroup, MoveCartesian, Gravity, VelocityCircle):
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

    class Stars(ParticleGroup, Circle):
        Z = -1
        radius = 2
        nb = 100
        max_age = 2000
        continuous = True
        pos = UniformInRect(SCREEN)
        gradient = "black", "#F5D7aE", "black"

    cozy_text = text("CozyFractal", "white", 170, "title")
    cozy_rect = cozy_text.get_rect(center=(SIZE[0] // 2, SIZE[1] // 2))

    class CozyFire(ParticleGroup, Circle, MovePolar, Acceleration):
        continuous = True
        nb = 8000
        max_age = 200
        gradient = "#ffa50000", "#ffa500", "red", "#8E44AD", "#ffa50000"
        pos = UniformInImage(cozy_text, cozy_rect.topleft)
        speed = Gauss(-0, 0.1)
        angle = Gauss(90, 5)
        acceleration = -0.004
        radius = lambda age: chrange(age, (0, 200), (2, 4), flipped=True)

    class EdgeBubbles(ParticleGroup, SurfComponent, Aim, Friction):
        continuous = True
        nb = 3000
        gradient = "red", "orange", "#ffa50040"
        pos = UniformInRect(SCREEN.inflate(10, 10).move(-9, -9), True)

        aim = SCREEN.center
        speed = Gauss(1, 0.5)
        max_age = 50
        radius = lambda age: chrange(age, (0, 50), (2, 10), 0.5, True)
        friction = 0.99

        colors = 50
        start_gradient = particles.gradient(
            "#5593F2",
            "#6FB584",
            "#D2A647",
            "#F98040",
            "#F1495B",
            steps=colors,
            force_alpha=True,
        )

        @classmethod
        def get_params_range(cls):
            return cls.max_age, cls.colors

        @classmethod
        def get_surf(cls, age, color_id):
            r = int(cls.radius(age))
            color = cls.start_gradient[color_id]
            color[3] = int(chrange(age, (0, cls.max_age), (0, 255), 2, True))
            s = pygame.Surface((r * 2 + 1, r * 2 + 1), pygame.SRCALPHA)
            s.fill(0)
            pygame.gfxdraw.filled_circle(s, r, r, r, color)
            return s

        def compute_params(self):
            min_dist = min(
                (player.distance_squared_to(a) for a in state.objects if isinstance(a, Asteroid)),
                default=None,
            )

            color = (
                0
                if min_dist is None
                else max(0, int(self.get_params_range()[1] - sqrt(min_dist) / 6))
            )
            return (self.age, np.tile(color, self.nb))

    class Snow(ParticleGroup, Circle, Gravity, MoveCartesian):
        continuous = True
        pos = mouse_generator
        nb = 4000
        max_age = 100
        gradient = "white", "#ddccee", (10, 40, 50, 40)
        velocity = Gauss((0, -1), (0.3, 0.3))
        gravity = (0, 0.1)

    class PolygonFire(ParticleGroup, SurfComponent, MovePolar, AngularVel):
        continuous = True
        nb = 1500
        max_age = 64
        # pos = Constant((SIZE[0] - 100, SIZE[1] - 100))
        pos = Uniform(cozy_rect.bottomleft, cozy_rect.bottomright)
        nb_seed = 16
        nb_colors = 100
        angle = Gauss(90, 10)
        speed = Gauss(2)
        rotation_speed = Uniform(-1, 1)

        @classmethod
        def get_params_range(cls):
            return (cls.max_age, cls.nb_seed, cls.nb_colors)

        def compute_params(self):
            color = ((self.state.timer - self.age) / 5 % self.nb_colors).astype(int)
            return (self.age, self.seeds, color)

        @classmethod
        def get_surf(self, age, seed, color):
            sides = 3 + seed % 4
            r = chrange(age, (0, self.max_age), (4, 10), flipped=True)
            alpha = chrange(age, (0, self.max_age), (0, 100), 2, True)
            c = pygame.Color(0)
            c.hsva = (color / self.nb_colors * 360, 100, 100, alpha)

            rotation = age * (1 + seed / 5)
            points = [from_polar(r, rotation + a * 360 / sides) + (r, r) for a in range(sides)]

            s = pygame.Surface((2 * r + 1, 2 * r + 1), pygame.SRCALPHA)
            pygame.gfxdraw.filled_polygon(s, points, c)
            return s

    state.add(Stars())
    state.add(EdgeBubbles())
    state.add(CozyFire())
    state.add(PolygonFire())
    s = pygame.Vector2(0, -50)
    state.add(
        PolygonFire(
            pos=Uniform(cozy_rect.topleft + s, cozy_rect.topright + s),
            angle=Gauss(-90, 10),
        )
    )
    # state.add(Snow())
    # state.add(Fountain())

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
                elif event.key == pygame.K_SPACE:
                    for a in Asteroid.generate_many(10):
                        state.add(a)

            state.handle_event(event)
            mouse_generator.handle_event(event)

        # if random.random() < 0.01:
        #     state.add(Fireworks())

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()

        screen.fill(BACKGROUND)
        state.draw(screen)


if __name__ == "__main__":
    wclib.run(mainloop())
