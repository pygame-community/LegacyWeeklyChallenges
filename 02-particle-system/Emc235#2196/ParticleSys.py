from typing import List, Tuple, Set, Union
from functools import partial
import numpy as np
import pygame
import random
import math


def clamp(val: float, min: float, max: float) -> float:
    """
    it clamps a value
    :param val: float
    :param min: float
    :param max: float
    :return: float
    """
    return min if val < min else max if val > max else val


class Particles:
    """
    a class for managing Particles

    Arguments
    ---------
    limit: int
        the max amount of particles that it can hold

    Methods
    ---------
    """

    __slots__ = ("radius_cutoff", "limit", "particles")

    def __init__(self, limit: int = 1000) -> None:
        self.radius_cutoff: float = 0.3
        self.limit: int = limit
        self.particles: Set[Particle] = set()

    def logic(self, dt: float = 1) -> "Particles":
        to_remove = set()
        for particle in self.particles:
            if particle.logic(dt):
                to_remove.add(particle)
        self.particles.difference_update(to_remove)
        return self

    def draw(self, surface) -> "Particles":
        for p in self.particles:
            p.draw(surface)
        return self

    def add(
        self,
        pos: pygame.math.Vector2,
        vel: pygame.math.Vector2,
        duration: int,
        rad: float,
        color: pygame.Color,
        image: pygame.surface.Surface = None,
    ) -> "Particles":
        if len(self.particles) >= self.limit:
            return self
        self.particles.add(Particle(pos, vel, duration, rad, color, image))
        return self

    def burst(
        self,
        pos: pygame.math.Vector2,
        vel: pygame.math.Vector2,
        duration: int,
        rad: float,
        color: pygame.Color,
        n: int = 50,
        image: Union[pygame.surface.Surface, None] = None,
    ) -> "Particles":
        if len(self.particles) >= self.limit:
            return self
        for _ in range(n):
            self.particles.add(
                Particle(
                    pos + [random.randint(-5, 5), random.randint(-5, 5)],
                    vel.rotate(math.degrees(random.random() * math.tau)),
                    duration + random.randint(-2, 2),
                    rad + random.randint(-3, 3) + 0.001,
                    color,
                    image,
                )
            )
        return self

    @property
    def length(self) -> int:
        return len(self.particles)


class Particle:
    __slots__ = ("pos", "vel", "duration", "age", "color", "woreoff", "rad", "image")

    def __init__(
        self,
        pos: pygame.math.Vector2,
        vel: pygame.math.Vector2,
        duration: int,
        rad: float,
        color: Union[Tuple[int, int, int], pygame.Color, List[int]],
        image: Union[pygame.surface.Surface, None] = None,
    ):
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(pos)
        self.vel: pygame.math.Vector2 = pygame.math.Vector2(vel)
        self.duration: int = duration
        self.age: int = 0
        self.rad: float = rad
        self.color: pygame.Color = pygame.Color(color)
        self.woreoff = self.color // pygame.Color(duration, duration, duration)
        self.image: Union[pygame.surface.Surface, None] = image

    def logic(self, dt: float = 1) -> bool:
        self.age += 1
        self.pos += self.vel * dt
        self.vel *= 0.9 * dt
        self.color -= self.woreoff
        return self.age >= self.duration

    def draw(self, surface: pygame.surface.Surface) -> None:
        if not self.image:
            pygame.draw.circle(surface, self.color, self.pos, self.rad)
        else:
            surface.blit(self.image, self.pos)
