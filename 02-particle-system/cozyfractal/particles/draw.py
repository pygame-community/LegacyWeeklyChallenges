import time
from typing import Union, Callable

import pygame
import pygame.gfxdraw
import numpy as np

from .colors import gradient
from .core import Component, ParticleGroup


class SurfComponent(Component):
    extra_params = ()
    requires = ("pos",)

    @classmethod
    def add(cls):
        super().add()
        if cls.nb_seed > 1:
            cls.params_shape = (cls.max_age, cls.nb_seed, *cls.extra_params)
        else:
            cls.params_shape = (cls.max_age, *cls.extra_params)

        indices = np.ndindex(*cls.params_shape)
        cls.table = np.array([cls.get_surf(*args) for args in indices]).reshape(cls.params_shape)

    def draw(self, screen: pygame.Surface):
        params = self.compute_params()
        surfs = self.table[params]
        l = zip(surfs, self.pos)
        screen.blits(l, False)

    def compute_params(self):
        age = self.age
        seed = self.seeds

        if self.nb_seed > 1:
            return age, seed
        return (age,)

    @classmethod
    def get_surf(cls, *args):
        raise NotImplemented


class Circle(SurfComponent):
    gradient = "white", "black"
    radius: Union[int, Callable[[int], int]] = 3

    colors_fade_to_transparent = False
    """This option requires that extra_params to be set to (len(gradient), )."""

    @classmethod
    def add(cls):
        if not cls.colors_fade_to_transparent:
            cls._gradient = gradient(*cls.gradient, steps=cls.max_age)
        else:
            cls._gradient = cls.gradient
        super().add()

    @classmethod
    def get_surf(cls, age, *color):
        r = cls.radius if not callable(cls.radius) else int(cls.radius(age))
        s = pygame.Surface((r * 2 + 1, r * 2 + 1), pygame.SRCALPHA)
        s.fill(0)

        if color:
            color = pygame.Color(cls.gradient[color[0]])
            color.set_length(4)
            color.a = 255 - int(255 * (age / cls.max_age) ** 2)
        else:
            color = cls._gradient[age]

        pygame.gfxdraw.filled_circle(s, r, r, r, color)
        return s


class VelocityCircle(SurfComponent):
    extra_params = (360,)

    @classmethod
    def add(cls):
        cls._gradient = gradient(
            "#E8554E",
            "#F19C65",
            "#FFD265",
            "#2AA876",
            "#0A7B83",
            steps=cls.extra_params[0],
            loop=True,
        )
        super().add()

    def compute_params(self):
        val = np.linalg.norm(self.pos, axis=1) + 50 * time.time() % 360
        # val = np.arctan2(self.velocity[:, 0], self.velocity[:, 1])
        vel = (val % 360).astype(int)
        return (*super().compute_params(), vel)

    @classmethod
    def get_surf(cls, age, vel):
        alpha = 255 - int(255 * (age / cls.params_shape[0]) ** 2)
        r = 3
        d = r * 2 + 1
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        s.fill(0)
        pygame.gfxdraw.filled_circle(s, r, r, r, (*cls._gradient[vel], alpha))
        return s
