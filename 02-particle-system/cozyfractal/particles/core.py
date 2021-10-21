import numpy as np
import pygame
import pygame.gfxdraw

from .rng import *

__all__ = ["Component", "ParticleGroup"]


class Component:
    def add(self, group: "ParticleGroup"):
        self.nb = group.nb

    def logic(self, group: "ParticleGroup"):
        pass

    def draw(self, group: "ParticleGroup", screen):
        pass


class ParticleGroup:
    Z = 0

    def __init__(
        self, nb, max_age, *components: Component, continuous=False, seeds=1, **init: IntoGenerator
    ):
        self.alive = True
        self.nb = nb
        self.nb_seed = seeds
        if self.nb_seed == 1:
            self.seeds = np.zeros(nb, dtype=int)
        else:
            self.seeds = Uniform(0, self.nb_seed - 1, True).gen(nb)

        self.continuous = continuous
        self.max_age = max_age

        if continuous:
            self.age = Uniform(0, self.max_age - 1, True).gen(nb)
        else:
            # TODO: If oneshot, age should be a single number shared by all
            self.age = np.zeros(nb, dtype=int)

        self.components = components
        self.init = init

        for key, value in init.items():
            init[key] = make_generator(value)
            setattr(self, key, init[key].gen(self.nb))

        for c in components:
            c.add(self)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset
                self.__init__(
                    self.nb,
                    self.max_age,
                    *self.components,
                    continuous=self.continuous,
                    seeds=self.nb_seed,
                    **self.init
                )
                return True

    def logic(self):
        self.age += 1

        dead = self.age >= self.max_age
        nb_dead = np.count_nonzero(dead)

        if self.continuous:
            for key, gen in self.init.items():
                getattr(self, key)[dead] = gen(nb_dead)
        elif nb_dead == self.nb:
            self.alive = False

        self.age[dead] = 0

        for c in self.components:
            c.logic(self)

    def draw(self, screen: pygame.Surface):
        for c in self.components:
            c.draw(self, screen)
