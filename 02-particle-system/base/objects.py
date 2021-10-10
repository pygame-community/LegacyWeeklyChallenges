"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
your particle system, without needing to implement a game that
goes with it too.
Feel free to modify everything in this file to your liking.
"""
from colorsys import hsv_to_rgb
from random import choice, gauss, choices

import pygame

from wclib import SIZE
from .utils import *

SCREEN = pygame.Rect(0, 0, *SIZE)


class Object:
    """The base class for all objects of the game."""

    def __init__(self, pos, vel, sprite: pygame.Surface):
        self.center = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.size = pygame.Vector2(sprite.get_size())
        self.sprite = sprite
        self.rotation = 0.0  # for the sprite
        self.alive = True

    def __str__(self):
        return f"<{self.__class__.__name__}(center={self.center}, vel={self.vel}, rotation={int(self.rotation)} size={self.size})>"

    @property
    def rotated_sprite(self):
        # We round the rotation to the nearest integer so that
        # the cache has a chance to work. Otherwise there would
        # always be cache misses: it is very unlikely to have
        # to floats that are equal.
        return rotate_image(self.sprite, int(self.rotation))

    @property
    def rect(self):
        return self.rotated_sprite.get_rect(center=self.center)

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.rect)

        # Corners
        w, h = SIZE
        tl = 0, 0
        tr = w, 0
        br = w, h
        bl = 0, h

        for a, b, offset in [
            (tl, tr, (0, h)),
            (bl, br, (0, -h)),
            (tl, bl, (w, 0)),
            (tr, br, (-w, 0)),
        ]:
            # For each side of the screen that it overlaps
            if self.rect.clipline(a, b):
                # Draw the spaceship at the other edge too.
                screen.blit(
                    self.rotated_sprite,
                    self.rotated_sprite.get_rect(center=self.center + offset),
                )

    def logic(self, **kwargs):
        # self.vel = clamp_vector(self.vel, self.MAX_VEL)
        self.center += self.vel

        self.center.x %= SIZE[0]
        self.center.y %= SIZE[1]


class Player(Object):
    ACCELERATION = 0.2
    FRICTION = 0.96
    ROTATION_ACCELERATION = 2
    INITIAL_ROTATION = 90
    FIRE_COOLDOWN = 10  # frames

    def __init__(self, pos, vel):
        super().__init__(pos, vel, load_image("player", 3))

        self.speed = 0
        self.fire_cooldown = -1

    def logic(self, events, objects, new_objects, **kwargs):
        pressed = pygame.key.get_pressed()

        # Fire
        self.fire_cooldown -= 1
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.fire(new_objects)
        if pressed[pygame.K_SPACE]:
            self.fire(new_objects)

        # Motion
        rotation_acc = pressed[pygame.K_LEFT] - pressed[pygame.K_RIGHT]
        raw_acceleration = pressed[pygame.K_DOWN] - pressed[pygame.K_UP]

        self.speed += raw_acceleration * self.ACCELERATION
        self.speed *= self.FRICTION  # friction

        self.rotation += (
            rotation_acc * self.ROTATION_ACCELERATION * min(1, 0.4 + abs(self.speed))
        )

        self.vel.from_polar((self.speed, self.INITIAL_ROTATION - self.rotation))

        super().logic(**kwargs)

    def draw(self, screen):
        super().draw(screen)

    def fire(self, objects: set):
        if self.fire_cooldown >= 0:
            return

        self.fire_cooldown = self.FIRE_COOLDOWN
        bullet = Bullet(self.center, 270 - self.rotation)
        objects.add(bullet)


class Bullet(Object):
    SPEED = 10
    TIME_TO_LIVE = 60 * 2

    def __init__(self, pos, angle):
        super().__init__(pos, from_polar(self.SPEED, angle), load_image("bullet", 2))
        self.rotation = 90 - angle
        self.time_to_live = self.TIME_TO_LIVE

    def logic(self, **kwargs):
        super().logic(**kwargs)

        self.time_to_live -= 1

        if self.time_to_live <= 0:
            self.alive = False


class Asteroid(Object):
    AVG_SPEED = 1

    def __init__(self, pos, vel, size=4, color=None):
        assert 1 <= size <= 4
        # We copy to change the color
        sprite = load_image(f"asteroid-{16*2**size}").copy()
        sprite.fill(color or self.random_color(), special_flags=pygame.BLEND_RGB_MULT)

        super().__init__(pos, vel, sprite)

    def random_color(self):
        r, g, b = hsv_to_rgb(uniform(0, 1), 1, 1)
        return int(r * 255), int(g * 255), int(b * 255)

    @classmethod
    def generate_many(cls, nb=8):
        objects = set()
        for _ in range(nb):
            angle = uniform(0, 360)
            pos = SCREEN.center + from_polar(gauss(SIZE[1] / 2, SIZE[1] / 12), angle)
            vel = from_polar(
                gauss(cls.AVG_SPEED, cls.AVG_SPEED / 6), gauss(180 + angle, 30)
            )
            size = choices([1, 2, 3, 4], [4, 3, 2, 1])[0]
            objects.add(cls(pos, vel, size))

        return objects
