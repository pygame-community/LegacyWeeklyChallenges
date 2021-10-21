from typing import Type

import numpy as np
import pygame
import pygame.gfxdraw

from .rng import *

__all__ = ["Component", "ParticleGroup"]


class Component:
    """Components are Mixins for ParticleGroup"""

    requires = ()
    provides = ()

    def logic(self: "ParticleGroup"):
        pass

    def draw(self: "ParticleGroup", screen):
        pass

    @classmethod
    def add(cls):
        pass

    def __init_subclass__(cls, **kwargs):
        if issubclass(cls, ParticleGroup):
            cls.add()


class ParticleGroup:

    Z = 0
    nb = 1000
    max_age = 100
    continuous = False
    nb_seed = 1

    def __init__(self, **init_override: IntoGenerator):
        self.alive = True
        if self.nb_seed == 1:
            self.seeds = np.zeros(self.nb, dtype=int)
        else:
            self.seeds = Uniform(0, self.nb_seed - 1, True).gen(self.nb)

        if self.continuous:
            self.age = Uniform(0, self.max_age - 1, True).gen(self.nb)
        else:
            # TODO: If oneshot, age should be a single number shared by all
            self.age = np.zeros(self.nb, dtype=int)

        self.init = self._get_random_initializers()
        self.init.update(init_override)

        for key, value in self.init.items():
            gen = self.init[key] = make_generator(value)
            setattr(self, key, gen(self.nb))

    @classmethod
    def _get_all_from_bases(cls, what: str):
        collec = ()
        for base in cls.__bases__:
            if issubclass(base, Component):
                collec += getattr(base, what)
        return collec

    @classmethod
    def _get_requires(cls):
        return set(cls._get_all_from_bases("requires"))

    @classmethod
    def _get_provides(cls):
        return set(cls._get_all_from_bases("provides"))

    @classmethod
    def _get_random_initializers(cls):
        to_get = cls._get_requires() - cls._get_provides()
        found = {}
        for name in to_get:
            try:
                found[name] = getattr(cls, name)
            except KeyError:
                raise NameError(
                    f"A component requires '{name}' but '{name}' was not found in the blueprint."
                ) from None
        return found

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset
                self.__init__(**self.init)
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

        for base in self.__class__.__bases__:
            if issubclass(base, Component):
                base.logic(self)

    def draw(self, screen: pygame.Surface):
        for base in self.__class__.__bases__:
            if issubclass(base, Component):
                base.draw(self, screen)
