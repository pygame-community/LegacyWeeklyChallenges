"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
a fog of war, without needed
Feel free to modify everything in this file to your liking.
"""
from random import choice, gauss

import pygame

from wclib import SIZE
from .utils import clamp, from_polar, load_image, random_in_rect


SCREEN = pygame.Rect(0, 0, *SIZE)


class Object:
    """The base class for all objects of the game."""

    def __init__(self, pos, sprite: pygame.Surface):
        self.pos = pygame.math.Vector2(pos)
        self.size = pygame.math.Vector2(sprite.get_size())
        self.sprite = sprite

    def __str__(self):
        return f"<{self.__class__.__name__}(pos={self.pos}, size={self.size})>"

    @property
    def rect(self):
        return pygame.Rect(self.pos, self.size)

    def draw(self, screen):
        screen.blit(self.sprite, self.pos)

    def logic(self, **kwargs):
        pass


class Object8Directional(Object):
    SCALE = 3
    SIZE = 16
    SHEET = "blue_ghost"

    ACCELERATION = 0.5
    DAMPING = 0.85

    # Asymptotic velocity will be solution of
    # x = x * DAMPING + ACCELERATION
    # That is,
    # x = ACCELERATION / (1 - DAMPING)

    def __init__(self, pos):
        self.velocity = pygame.Vector2()
        self.acceleration = pygame.Vector2()

        super().__init__(pos, self.get_image())

    def get_image(self):
        angle = self.velocity.as_polar()[1]
        idx = int((-angle + 90 + 45 / 2) % 360 / 360 * 8)
        sheet = load_image(self.SHEET, self.SCALE)
        unit = self.SIZE * self.SCALE
        return sheet.subsurface(idx * unit, 0, unit, unit)

    def logic(self, **kwargs):
        self.velocity *= self.DAMPING
        self.velocity += self.acceleration
        self.pos += self.velocity
        self.sprite = self.get_image()
        self.pos.x = clamp(self.pos.x, 0, SIZE[0]-self.sprite.get_width())
        self.pos.y = clamp(self.pos.y, 0, SIZE[1]-self.sprite.get_height())


class Player(Object8Directional):
    def __init__(self, pos) -> None:
        super().__init__(pos)
        self.radius = self.sprite.get_height()*2 + self.sprite.get_height()

    def logic(self, **kwargs):
        pressed = pygame.key.get_pressed()
        direction_x = (pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT]) * kwargs.get("dt", 1)
        direction_y = (pressed[pygame.K_DOWN] - pressed[pygame.K_UP]) * kwargs.get("dt", 1)

        self.acceleration = pygame.Vector2(direction_x, direction_y) * self.ACCELERATION
        super().logic(**kwargs)


class Ghost(Object8Directional):
    SHEET = "pink_ghost"
    ACCELERATION = 0.2
    DAMPING = 0.9

    def __init__(self, player, pos=None):
        if pos is None:
            pos = random_in_rect(SCREEN)
        super().__init__(pos)
        self.player = player
        self.goal = self.new_goal()

    def new_goal(self):
        direction = from_polar(60, gauss(self.velocity.as_polar()[1], 30))
        return self.rect.center + direction

    def logic(self, **kwargs):
        middle_area = SCREEN.inflate(-30, -30)
        while self.rect.collidepoint(self.goal) or not middle_area.collidepoint(self.goal):
            self.goal = self.new_goal()

        self.acceleration = (
            self.goal - self.rect.center
        ).normalize() * self.ACCELERATION * kwargs.get("dt", 1)
        super().logic(**kwargs)

    def draw(self, screen):
        if self.pos.distance_to(self.player.rect.center) < self.player.radius or\
           pygame.math.Vector2(self.rect.topright).distance_to(self.player.rect.center) < self.player.radius or\
           pygame.math.Vector2(self.rect.bottomright).distance_to(self.player.rect.center) < self.player.radius or\
           pygame.math.Vector2(self.rect.bottomleft).distance_to(self.player.rect.center) < self.player.radius:
            screen.blit(self.sprite, self.pos)


class SolidObject(Object):
    SHEET_RECT = [
        (0, 0, 24, 31),
        (24, 0, 24, 24),
        (48, 0, 24, 24),
        (72, 0, 16, 24),
        (88, 0, 48, 43),
        (136, 0, 16, 16),
    ]
    SCALE = 3

    def __init__(self, pos):
        sheet = load_image("tileset", self.SCALE)
        sheet.set_colorkey(0xFFFFFF)
        rect = choice(self.SHEET_RECT)
        rect = [x * self.SCALE for x in rect]
        super().__init__(pos, sheet.subsurface(rect))

    @classmethod
    def generate_many(cls, nb=16, max_tries=1000):
        objects = []
        tries = 0  # avoids infinite loop
        while len(objects) < nb and tries < max_tries:
            pos = random_in_rect(SCREEN)
            obj = cls(pos)
            if not any(obj.rect.colliderect(other.rect) for other in objects):
                objects.append(obj)
        return objects


class LayeredVisibility:
    def __init__(self, player: Player) -> None:
        self.player: Player = player

        self.surf: pygame.surface.Surface = pygame.surface.Surface(SIZE)
        self.surf.set_colorkey((255, 255, 255))
        self.old_surf: pygame.surface.Surface = pygame.surface.Surface(self.surf.get_size())
        self.old_surf.set_alpha(200)
        self.old_surf.set_colorkey((255, 255, 255))

    def draw(self, WIN: pygame.surface.Surface) -> None:
        pygame.draw.circle(self.surf, (255, 255, 255), self.player.rect.center, self.player.radius)

        pygame.draw.circle(self.old_surf, (30, 30, 30), self.player.rect.center, self.player.radius)
        old_surf_copy = self.old_surf.copy()
        pygame.draw.circle(old_surf_copy, (255, 255, 255), self.player.rect.center, self.player.radius)

        WIN.blit(self.old_surf, (0, 0))
        WIN.blit(old_surf_copy, (0, 0))
        WIN.blit(self.surf, (0, 0))
