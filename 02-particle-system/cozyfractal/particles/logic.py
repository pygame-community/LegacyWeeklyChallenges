from dataclasses import dataclass

import numpy as np
import pygame

from .core import Component, ParticleGroup

__all__ = ["MovePolar", "MoveCartesian", "WrapTorus", "AngularVel", "Gravity"]


class MovePolar(Component):
    """A component that moves particles according to a velocity in polar coordinates."""

    depends = "speed", "angle", "pos"
    updates = ("pos",)

    def logic(self, group):
        radians = group.angle * (np.pi / 180)
        group.pos += (group.speed * np.array([np.cos(radians), np.sin(radians)])).T


class MoveCartesian(Component):
    """Move particles according to a velocity in cartesian coordinates."""

    depends = "velocity", "pos"
    updates = ("pos",)

    def logic(self, group: "ParticleGroup"):
        group.pos += group.velocity


class WrapTorus(Component):
    """A component that wrap the position of particles inside a rectangle"""

    updates = ("pos",)

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

    def logic(self, group: "ParticleGroup"):
        group.pos -= self.rect.topleft
        group.pos %= self.rect.size
        group.pos += self.rect.topleft


@dataclass
class AngularVel(Component):
    """Increase the angle of a particle by a constant."""

    updates = ("angle",)

    speed: float

    def logic(self, group: "ParticleGroup"):
        group.angle += self.speed


@dataclass
class Gravity(Component):
    updates = ("velocity",)

    def __init__(self, gravity):
        if isinstance(gravity, (float, int)):
            gravity = (0, gravity)
        self.gravity = np.array(gravity)

    def logic(self, group: "ParticleGroup"):
        group.velocity += self.gravity
