from dataclasses import dataclass

import numpy as np
import pygame

from .core import Component, ParticleGroup

__all__ = ["MovePolar", "MoveCartesian", "WrapTorus", "AngularVel", "Gravity"]


class MovePolar(Component):
    """A component that moves particles according to a velocity in polar coordinates."""

    depends = "speed", "angle", "pos"

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


@dataclass
class AngularVel(Component):
    """Increase the angle of a particle by a constant."""

    requires = ("angle",)

    speed: float = 1

    def logic(self: "ParticleGroup"):
        self.angle += self.speed


@dataclass
class Gravity(Component):
    requires = ("velocity",)

    gravity = (0, 1)

    def logic(self: "ParticleGroup"):
        self.velocity += self.gravity
