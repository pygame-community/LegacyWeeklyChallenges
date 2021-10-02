"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
a fog of war, without needed
Feel free to modify everything in this file to your liking.
"""
import random
from random import choice, gauss

import pygame

from wclib import SIZE
from .utils import clamp, from_polar, load_image, random_in_rect

SCREEN = pygame.Rect(0, 0, *SIZE)


class Object:
    """The base class for all objects of the game."""

    def __init__(self, pos, sprite: pygame.Surface):
        self.pos = pygame.Vector2(pos)
        self.size = pygame.Vector2(sprite.get_size())
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

        self.pos.x = clamp(self.pos.x, 0, SIZE[0])
        self.pos.y = clamp(self.pos.y, 0, SIZE[1])


class Player(Object8Directional):
    def logic(self, **kwargs):
        pressed = pygame.key.get_pressed()
        direction_x = pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT]
        direction_y = pressed[pygame.K_DOWN] - pressed[pygame.K_UP]

        self.acceleration = pygame.Vector2(direction_x, direction_y) * self.ACCELERATION
        super().logic(**kwargs)


class Ghost(Object8Directional):
    SHEET = "pink_ghost"
    ACCELERATION = 0.2
    DAMPING = 0.9

    def __init__(self, pos=None):
        if pos is None:
            pos = random_in_rect(SCREEN)
        super().__init__(pos)
        self.goal = self.new_goal()

    def new_goal(self):
        direction = from_polar(60, gauss(self.velocity.as_polar()[1], 30))
        return self.rect.center + direction

    def logic(self, **kwargs):
        middle_area = SCREEN.inflate(-30, -30)
        while self.rect.collidepoint(self.goal) or not middle_area.collidepoint(
                self.goal
        ):
            self.goal = self.new_goal()

        self.acceleration = (
                                    self.goal - self.rect.center
                            ).normalize() * self.ACCELERATION
        super().logic(**kwargs)


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


class LightGlow:
    def __init__(self):
        self.x = 50
        self.y = 50
        self.surf = pygame.Surface((250, 250), pygame.SRCALPHA)
        self.intensity = 155
        self.surf.fill((155, 155, 155))

    def set_intensity(self, val):
        self.intensity = val
        self.surf.fill((val, val, val))


class DarkOverlay:
    def __init__(self):
        self.light = LightGlow()
        self.surf = pygame.Surface(SCREEN.size, pygame.SRCALPHA)
        self.light.set_intensity(255)
        self.cell_size = 16 * 4
        self.grid_surf = pygame.Surface((self.cell_size, self.cell_size))
        self.grid_surf.fill((255, 255, 255))
        self.grid = [[255 * random.random() for _ in range(SCREEN.w // self.cell_size)] for _ in range(SCREEN.h // self.cell_size)]

    def draw_cell_at_pos(self, intensity, row, col, surf: pygame.Surface):
        self.grid_surf.fill((intensity, intensity, intensity))
        surf.blit(self.grid_surf, (col * self.cell_size, row * self.cell_size), special_flags=pygame.BLEND_RGBA_MULT)

    def set_grid_lighting(self, source, spread=4):
        def set_cell_val(_cell, val, _offset=(0, 0)):
            row = _cell[0] + _offset[0]
            col = _cell[1] + _offset[1]
            if row < 0:
                row = 0
            if col < 0:
                col = 0
            try:
                self.grid[row][col] = val
            except IndexError:
                return
        for i in range(spread, -1, -1):
            cell_offsets = []
            for j in range(i * 2):
                cell_offsets.extend([[j - i + 1, x - i + 1] for x in range(i * 2)])
            for offset in cell_offsets:
                set_cell_val(source, 255 // (i + 1), _offset=offset)

    def draw(self, surf: pygame.Surface, pos):
        self.grid = [[0 for _ in range(SCREEN.w // self.cell_size)] for _ in range(SCREEN.h // self.cell_size)]
        source_cell = [int(pos.y // self.cell_size), int(pos.x // self.cell_size)]  # row, col
        # self.grid[source_cell[0]][source_cell[1]] = 255
        self.set_grid_lighting(source_cell)
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                self.draw_cell_at_pos(self.grid[row][col], row, col, surf)
