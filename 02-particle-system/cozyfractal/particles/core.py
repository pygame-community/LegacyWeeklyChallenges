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

    def handle_event(self, event):
        pass

    def logic(self: "ParticleGroup"):
        pass

    def draw(self: "ParticleGroup", screen):
        pass


class ParticleGroup:
    Z = 0
    nb = 1000
    max_age = 100
    continuous = False
    nb_seed = 1

    seeds: np.array
    age: np.array

    def __init__(self, **init_override: IntoGenerator):
        self.alive = True
        if self.nb_seed == 1:
            self.seeds = np.zeros(self.nb, dtype=int)
        else:
            self.seeds = np.array([])  # placeholder
            init_override.setdefault("seeds", Uniform(0, self.nb_seed, True))

        if self.continuous:
            self.age = Uniform(0, self.max_age - 1, True).gen(self.nb)
        else:
            # TODO: If oneshot, age should be a single number shared by all
            self.age = np.zeros(self.nb, dtype=int)

        self.init = self._get_random_initializers(**init_override)

        for key, value in self.init.items():
            self.init[key] = value
            if isinstance(value, Generator):
                setattr(self, key, value.gen(self.nb))
            else:
                setattr(self, key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.init})>"

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
    def _get_random_initializers(cls, **overrides):
        to_get = cls._get_requires() - cls._get_provides()
        found = overrides
        for name in to_get:
            try:
                found.setdefault(name, getattr(cls, name))
            except AttributeError:
                pass

        missing = to_get - set(found)
        if missing:
            raise NameError(
                f"A component requires {missing} but {missing} was not found in the blueprint."
            ) from None
        return found

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset
                self.__init__(**self.init)

        for base in self.__class__.__bases__:
            if issubclass(base, Component):
                base.handle_event(self, event)

    def logic(self):
        self.age += 1

        dead = self.age >= self.max_age
        nb_dead = np.count_nonzero(dead)

        if self.continuous:
            for key, gen in self.init.items():
                getattr(self, key)[dead] = gen(nb_dead)
            self.age[dead] = 0
        elif nb_dead >= self.nb:
            self.alive = False
            return

        for base in self.__class__.__bases__:
            if issubclass(base, Component):
                base.logic(self)

    def draw(self, screen: pygame.Surface):
        for base in self.__class__.__bases__:
            if issubclass(base, Component):
                base.draw(self, screen)
