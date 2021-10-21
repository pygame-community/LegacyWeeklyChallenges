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
    "Acceleration",
    "Interpolate",
    "BounceRect",
    "Aim",
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

    requires = ("angle", "rotation_speed")

    rotation_speed: float = 1

    def logic(self: "ParticleGroup"):
        self.angle += self.rotation_speed


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


class Acceleration(Component):
    requires = ("speed",)
    acceleration = 1

    def logic(self: "ParticleGroup"):
        self.speed += self.acceleration


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
        normals = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for limit, normal in zip(self.bounce_limits, normals):
            self.handle_bounce(limit, normal)

    def handle_bounce(self, limit, normal):
        if limit is None:
            return

        for axis, direction in enumerate(normal):
            if direction == 0:
                continue
            elif direction < 0:
                over_limit = self.pos[:, axis] > limit
            else:
                over_limit = self.pos[:, axis] < limit
            self.pos[over_limit, axis] = limit
            self.velocity[over_limit, axis] *= -self.bounce_elacticity


class Aim(Component):
    requires = "pos", "speed"
    aim = (50, 50)

    def logic(self: "ParticleGroup"):
        direction = self.aim - self.pos
        direction /= np.linalg.norm(direction, axis=1)[..., None]
        direction *= self.speed[..., None]

        self.pos += direction
