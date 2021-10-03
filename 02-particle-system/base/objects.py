"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
your particle system, without needing to implement a game that
goes with it too.
Feel free to modify everything in this file to your liking.
"""
from random import choice, gauss

import pygame

from wclib import SIZE
from .utils import *

SCREEN = pygame.Rect(0, 0, *SIZE)


class Object:
    """The base class for all objects of the game."""

    MAX_VEL = 2

    def __init__(self, pos, vel, sprite: pygame.Surface):
        self.center = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.size = pygame.Vector2(sprite.get_size())
        self.sprite = sprite
        self.rotation = 0

    def __str__(self):
        return f"<{self.__class__.__name__}(center={self.center}, vel={self.vel}, rotation={int(self.rotation)} size={self.size})>"

    @property
    def rotated_sprite(self):
        # We round the rotation to the nearest integer so that
        # the cache has a chance to work. Otherwise there would
        # always be cache misses: it is very unlikely to have
        # to floats that are equal.
        return rotate_image(self.sprite, int(self.rotation))

    def draw(self, screen):
        screen.blit(
            self.rotated_sprite, self.rotated_sprite.get_rect(center=self.center)
        )

    def logic(self, **kwargs):
        self.vel = clamp_vector(self.vel, self.MAX_VEL)
        self.center += self.vel


class Player(Object):
    def __init__(self, pos, vel):
        super().__init__(pos, vel, load_image("player"))

    def logic(self, **kwargs):
        pressed = pygame.key.get_pressed()
        rotation_acc = pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT]
        raw_acceleration = pressed[pygame.K_DOWN] - pressed[pygame.K_UP]

        # self.acceleration = pygame.Vector2(direction_x, direction_y) * self.ACCELERATION
        super().logic(**kwargs)
