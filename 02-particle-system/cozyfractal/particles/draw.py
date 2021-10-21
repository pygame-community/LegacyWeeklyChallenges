import pygame
import pygame.gfxdraw
import numpy as np

from .colors import gradient
from .core import Component, ParticleGroup


class SurfComponent(Component):
    extra_params = ()

    def add(self, group: "ParticleGroup"):
        super().add(group)

        if group.nb_seed > 1:
            self.shape = (group.max_age, group.nb_seed, *self.extra_params)
        else:
            self.shape = (group.max_age, *self.extra_params)

        print("shape", self.shape)
        indices = np.ndindex(*self.shape)
        self.table = np.array([self.get_surf(*args) for args in indices]).reshape(self.shape)

    def draw(self, group: "ParticleGroup", screen: pygame.Surface):
        params = self.compute_params(group)
        surfs = self.table[params]
        l = zip(surfs, group.pos)
        screen.blits(l, False)

    def compute_params(self, group):
        age = group.age
        seed = group.seeds

        if group.nb_seed > 1:
            return age, seed
        return (age,)

    def get_surf(self, *args):
        raise NotImplemented


class Circle(SurfComponent):
    def __init__(self, *colors, size=3):
        self.colors = colors
        self.size = size

    def add(self, group: "ParticleGroup"):
        self.gradient = gradient(*self.colors, group.nb)
        super().add(group)

    def get_surf(self, age):
        s = pygame.Surface((self.size * 2 + 1, self.size * 2 + 1))
        pygame.gfxdraw.filled_circle(s, self.size, self.size, self.size, self.gradient[age])
        s.set_colorkey(0)
        return s


class VelocityCircle(SurfComponent):
    extra_params = (360,)

    def add(self, group: "ParticleGroup"):
        self.gradient = gradient(
            "#E8554E",
            "#F19C65",
            "#FFD265",
            "#2AA876",
            "#0A7B83",
            steps=self.extra_params[0],
            loop=True,
        )
        super().add(group)

    def compute_params(self, group):
        # val = np.linalg.norm(group.pos - np.array(SIZE) / 2, axis=1)
        val = group.angle
        vel = (val % 360).astype(int)
        return (*super().compute_params(group), vel)

    def get_surf(self, age, vel):
        alpha = 255 - int(255 * (age / self.shape[0]) ** 2)
        r = 3
        d = r * 2 + 1
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        s.fill(0)
        pygame.gfxdraw.filled_circle(s, r, r, r, (*self.gradient[vel], alpha))
        return s
