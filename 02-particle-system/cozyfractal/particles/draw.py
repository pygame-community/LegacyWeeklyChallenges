import time
from abc import abstractmethod, abstractclassmethod, ABC
from functools import cached_property
from typing import Union, Callable

import pygame
import pygame.gfxdraw
import numpy as np

from .colors import gradient
from .core import Component, ParticleGroup


class class_cached:
    def __init__(self, get):
        self.get = get
        self.name = "NONAME"
        self.owner = None

    def __repr__(self):
        return f"<class_cached(name={self.name})>"

    def __set_name__(self, owner, name):
        # We assume that each descriptor will be used only once,
        # as a decorator, so it is fine to store stuff
        # in the instance
        assert self.owner is None

        self.name = name
        self.owner = owner

    def __get__(self, instance, owner):
        if instance is None and owner is self.owner:
            return self

        if instance is None:  # called via a subclass of self.owner
            klass = owner
        else:  # called via an instance of a subclass of self.owner
            klass = instance.__class__

        value = self.get(klass)
        setattr(klass, self.name, value)
        return value


class SurfComponent(ABC, Component):
    requires = ("pos",)

    @class_cached
    def table(self):
        shape = self.get_params_range()
        indices = np.ndindex(*shape)
        return np.array([self.get_surf(*args) for args in indices]).reshape(shape)

    def draw(self, screen: pygame.Surface):
        params = self.compute_params()
        surfs = self.table[params]
        l = zip(surfs, self.pos)
        screen.blits(l, False)

    @abstractmethod
    def compute_params(self):
        pass

    @classmethod
    @abstractmethod
    def get_params_range(cls):
        pass

    @abstractmethod
    def get_surf(self, *args):
        pass


class Circle(SurfComponent):
    gradient = "white", "black"
    radius: Union[int, Callable[[int], int]] = 3

    @classmethod
    def get_params_range(cls):
        return (cls.max_age,)

    def compute_params(self):
        return self.age

    @class_cached
    def _gradient(cls):
        return gradient(*cls.gradient, steps=cls.max_age)

    @classmethod
    def get_surf(cls, age):
        r = cls.radius if not callable(cls.radius) else int(cls.radius(age))
        s = pygame.Surface((r * 2 + 1, r * 2 + 1), pygame.SRCALPHA)
        s.fill(0)
        color = cls._gradient[age]

        pygame.gfxdraw.filled_circle(s, r, r, r, color)
        return s


class VelocityCircle(SurfComponent):
    @classmethod
    def get_params_range(cls):
        return cls.max_age, 360

    @class_cached
    def _gradient(cls):
        return gradient(
            "#E8554E",
            "#F19C65",
            "#FFD265",
            "#2AA876",
            "#0A7B83",
            steps=cls.get_params_range()[1],
            loop=True,
        )

    def compute_params(self):
        val = np.linalg.norm(self.pos, axis=1) + 50 * time.time() % 360
        # val = np.arctan2(self.velocity[:, 0], self.velocity[:, 1])
        vel = (val % 360).astype(int)
        return (self.age, vel)

    @classmethod
    def get_surf(cls, age, vel):
        alpha = 255 - int(255 * (age / cls.max_age) ** 2)
        r = 3
        d = r * 2 + 1
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        s.fill(0)
        pygame.gfxdraw.filled_circle(s, r, r, r, (*cls._gradient[vel], alpha))
        return s
