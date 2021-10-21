from dataclasses import dataclass

import numpy as np
import pygame

from .core import Component, ParticleGroup
from .rng import Constant

__all__ = [
    "MovePolar",
    "MoveCartesian",
    "WrapTorus",
    "AngularVel",
    "Gravity",
    "Friction",
    "Interpolate",
    "BounceRect",
]


class MovePolar(Component):
    """A component that moves particles according to a velocity in polar coordinates."""

    requires = "speed", "angle", "pos"

    def logic(self: "ParticleGroup"):
        radians = self.angle * (np.pi / 180)
        self.pos += (self.speed * np.array([np.cos(radians), np.sin(radians)])).T


class MoveCartesian(Component):
    """Move particles according to a velocity in cartesian coordinates."""

    requires = "velocity", "pos"

    def logic(self: "ParticleGroup"):
        self.pos += self.velocity


class WrapTorus(Component):
    """A component that wrap the position of particles inside a rectangle"""

    requires = ("pos",)

    wrap_rect = (0, 0, 100, 100)  # left, top, width, height

    def logic(self: "ParticleGroup"):
        self.pos -= self.wrap_rect[:2]
        self.pos %= self.wrap_rect[2:]
        self.pos += self.wrap_rect[:2]


class AngularVel(Component):
    """Increase the angle of a particle by a constant."""

    requires = ("angle",)

    speed: float = 1

    def logic(self: "ParticleGroup"):
        self.angle += self.speed


class Gravity(Component):
    requires = ("velocity",)

    gravity = (0, 1)

    def logic(self: "ParticleGroup"):
        self.velocity += self.gravity


class Friction(Component):
    requires = ("speed",)
    friction = 0.99

    def logic(self: "ParticleGroup"):
        self.speed *= self.friction


class Interpolate(Component):
    interpolations = {}

    @classmethod
    def add(cls):
        super().add()
        cls._interpolations = {}
        for name, (a, b) in cls.interpolations.items():
            t = np.linspace(0, 1, cls.max_age)
            val = (1 - t) * a + t * b
            cls._interpolations[name] = val

    def logic(self):
        for name, values in self._interpolations.items():
            setattr(self, name, values[self.age])


class BounceRect(Component):
    requires = "velocity", "pos"
    bounce_limits = (0, 0, 100, 100)  # Left, Top, Right, Bottom
    bounce_elacticity = 0.8

    def logic(self):
        left = self.bounce_limits[0]
        if left is not None:
            over_left = self.pos[:, 0] < left
            self.pos[over_left, 0] = left
            self.velocity[over_left, 0] *= -self.bounce_elacticity

        top = self.bounce_limits[1]
        if top is not None:
            over_top = self.pos[:, 1] < top
            self.pos[over_top, 1] = top
            self.velocity[over_top, 1] *= -self.bounce_elacticity

        right = self.bounce_limits[2]
        if right is not None:
            over_right = self.pos[:, 0] > right
            self.pos[over_right, 0] = right
            self.velocity[over_right, 0] *= -self.bounce_elacticity

        bottom = self.bounce_limits[3]
        if bottom is not None:
            over_bottom = self.pos[:, 1] > bottom
            self.pos[over_bottom, 1] = bottom
            self.velocity[over_bottom, 1] *= -self.bounce_elacticity
