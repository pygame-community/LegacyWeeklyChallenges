import sys
import textwrap
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Sequence, Union

import numpy as np
import pygame.draw

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
from .rng import *

BACKGROUND = 0x0F1012


def particle_blueprint(name: str, *components: "Component"):
    assert name.isidentifier()

    provides = sum((c.provides for c in components), ())
    assert len(provides) == len(set(provides))

    depends = sum((c.depends for c in components), ())
    assert set(provides) == set(depends)

    def fmt(kind: str):
        get = attrgetter(kind)
        s = "\n".join(get(c) for c in components if get(c))
        return textwrap.indent(s.strip(), " " * 8).strip() or "pass"

    init = fmt("init")
    logic = "\n".join(c.logic for c in components if c.logic)
    draw = "\n".join(c.draw for c in components if c.draw)

    code = f"""
class {name}:
    def __init__(self, nb):
        self.age = 
        {fmt("init")}
        
    def logic(self):
        {fmt("logic")}
        
    def draw(self, screen):
        {fmt("draw")}
        
"""
    print(code)
    compiled = compile(code, f"particles-{name}.py", "exec")
    locs = {}
    klass = exec(compiled, globals(), locs)
    return locs[name]


class Component:
    depends: tuple = ()
    updates: tuple = ()
    provides: tuple = ()

    def logic(self, group: "ParticleGroup"):
        pass

    def draw(self, group: "ParticleGroup"):
        pass


class AngularVelComponent(Component):
    depends = ("speed", "angle")
    updates = ("pos",)

    def logic(self, group):
        radians = group.angle * (np.pi / 180)
        group.pos += (group.speed * np.array([np.cos(radians), np.sin(radians)])).T


class ColorGradientComponent(Component):
    provides = ("color",)

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def logic(self, group):
        group.color = self.gradient[group.age]


class WrapScreenTorus(Component):
    updates = ("pos",)

    def logic(self, group: "ParticleGroup"):
        group.pos %= SIZE


class MoveStraightTorusComponent(Component):
    depends = ("pos",)
    provides = ("pos",)

    def __init__(self, vel):
        self.vel = np.array(vel)

    def logic(self, group):
        group.pos += self.vel


@dataclass
class Continuous(Component):
    max_age: int

    def logic(self, group: "ParticleGroup"):
        dead = group.age > self.max_age
        nb_dead = np.count_nonzero(dead)

        group.age[dead] = 0

        for key, value in group.init.items():
            getattr(group, key)[dead] = make_generator(value).gen(nb_dead)


@dataclass
class AngularVel(Component):
    updates = ("angle",)

    speed: float

    def logic(self, group: "ParticleGroup"):
        group.angle += self.speed


class ParticleGroup:
    Z = 0

    def __init__(self, nb, *components: Component, **init: IntoGenerator):
        self.alive = True
        self.nb = nb
        self.age = np.zeros(nb)
        self.components = components
        self.init = init

        for key, value in init.items():
            setattr(self, key, make_generator(value).gen(self.nb))

        self.surf = pygame.Surface((7, 7))
        self.surf.set_colorkey(0)
        pygame.draw.circle(self.surf, "#ffa500", (3, 3), 3, 1)

        self.blit_args = [(self.surf, p) for p in self.pos]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.__init__(self.nb, *self.components, **self.init)
                return True

    def logic(self):
        self.age += 1
        for c in self.components:
            c.logic(self)

    def draw(self, screen: pygame.Surface):
        for c in self.components:
            c.draw(self)
        screen.blits(self.blit_args, False)


def mainloop():
    pygame.init()

    # player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))
    # The state is just a collection of all the objects in the game
    p = ParticleGroup(
        10000,
        # SpawnGauss((0, 0), (50, 50)),
        # SpawnPos((0, 0)),
        # MoveStraightTorusComponent((1, 1)),
        AngularVelComponent(),
        AngularVel(0.8),
        # WrapScreenTorus(),
        Continuous(100),
        age=Uniform(0, 100, True),
        pos=np.array(SIZE) / 2,
        speed=Gauss(8),
        angle=Uniform(0, 360),
    )

    state = State(FpsCounter(60), p)
    # state = State(player, FpsCounter(60), *Asteroid.generate_many())

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            else:
                state.handle_event(event)

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()

        screen.fill(BACKGROUND)
        state.draw(screen)


if __name__ == "__main__":
    wclib.run(mainloop())
