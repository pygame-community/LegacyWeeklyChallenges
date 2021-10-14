"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
a fog of war, without needed
Feel free to modify everything in this file to your liking.
"""
from operator import attrgetter
from random import choice, gauss
from typing import List

import numpy as np

from wclib import SIZE
from .utils import *

SCREEN = pygame.Rect(0, 0, *SIZE)


def np_blit_rect(dest, surf, pos):
    """Return the 8 coordinates to blit np array on each other, like pygame.blit, with bound checking."""
    w = dest.shape[0]
    h = dest.shape[1]

    sw = surf.shape[0]
    sh = surf.shape[1]

    # blit start position (on dest)
    x, y = map(int, pos)
    # blit end pos (on dest)
    bex, bey = x + sw, y + sh

    # if the beginning of the surf is outside dest (more on the top/left)
    # we take only what's inside
    sx = sy = 0
    if x < 0:
        sx = -x
        x = 0
    if y < 0:
        sy = -y
        y = 0

    # and we cut also what's on the other side
    if w < bex:
        bex = w
    if h < bey:
        bey = h

    # and finally update the end position of surf that will be blit
    ex = sx + (bex - x)
    ey = sy + (bey - y)

    return x, bex, y, bey, sx, ex, sy, ey


def np_blit(dest, surf, pos):
    """Blit an surf on dest like pygame.blit."""
    x1, x2, y1, y2, a1, a2, b1, b2 = np_blit_rect(dest, surf, pos)
    dest[x1:x2, y1:y2] = surf[a1:a2, b1:b2]


class Shadow:

    # All those values could be arguments of __init__,
    # but since I know I'll only have on instance at any time
    # they are more visible here.

    VISION = 150  # how many pixels we see in each direction
    GRADIENT_SIZE = VISION  # pixels
    PITCH_BLACK = 255
    DARK = 180  # out of 255
    MEMORY_DECAY = 8

    def __init__(self, size):
        self.timer = 0
        self.size = pygame.Vector2(size)
        self.memory = np.full(size, self.PITCH_BLACK, dtype=np.uint8)
        self.memory_surf = pygame.Surface(size, pygame.SRCALPHA)

        self.sight = self.compute_sight_surf(self.VISION, False)
        self.sight_inverted = 255 - self.sight
        self.sight_surf_inverted = self.compute_sight_surf(self.VISION, True)

    def sight_rect(self, center):
        r = pygame.Rect(0, 0, *self.sight.shape)
        r.center = center
        return r

    def logic(self, player, objects):
        self.timer += 1
        player_center = player.rect.center

        np.clip(self.memory, self.DARK, 254, out=self.memory)

        if self.timer % self.MEMORY_DECAY == 0:
            self.memory += 1

        # Blit the light circle on the memory
        x1, x2, y1, y2, a1, a2, b1, b2 = np_blit_rect(
            self.memory, self.sight, self.sight_rect(player_center).topleft
        )
        self.memory[x1:x2, y1:y2] = np.minimum(
            self.memory[x1:x2, y1:y2],
            self.sight[a1:a2, b1:b2],
        )

        pygame.surfarray.pixels_alpha(self.memory_surf)[:] = self.memory

    def draw(self, screen: pygame.Surface, player, objects: List["Object"]):
        player_center = pygame.Vector2(int(player.rect.centerx), int(player.rect.centery))
        vision_rect = self.sight_rect(player_center)

        # Draw screen with only static objects:
        for obj in sorted(objects, key=attrgetter("rect.bottom")):
            if obj.STATIC:
                obj.draw(screen)

        # Draw screen with moving objects too
        # with_moving = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        with_moving = pygame.Surface(vision_rect.size, pygame.SRCALPHA)
        for obj in sorted(objects, key=attrgetter("rect.bottom")):
            if obj.rect.colliderect(vision_rect):
                with_moving.blit(obj.sprite, obj.pos - vision_rect.topleft)

        # Erase just outside the circle
        pygame.surfarray.pixels_alpha(with_moving)[:] = self.sight_inverted
        with_moving.set_colorkey(0)
        screen.blit(with_moving, vision_rect)

        screen.blit(self.memory_surf, (0, 0))

    def compute_sight_surf(self, radius, inverted):
        # Draw a transparent gradient
        s = pygame.Surface((radius * 2 + 1, radius * 2 + 1), pygame.SRCALPHA)
        s.fill((0, 0, 0, self.PITCH_BLACK))
        start = radius - self.GRADIENT_SIZE
        end = radius
        for r in range(end, start - 1, -1):
            alpha = chrange(r, (start, end), (0, 255), 2)
            g = 255 - alpha
            if inverted:
                color = (255, 255, 255, 255 - alpha)
            else:
                color = (0, 0, 0, alpha)
            pygame.draw.circle(s, color, (radius, radius), r)
        return pygame.surfarray.pixels_alpha(s)


class Object:
    """The base class for all objects of the game."""

    STATIC = True

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
    STATIC = False
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
    ACCELERATION = 0.9

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
        while self.rect.collidepoint(self.goal) or not middle_area.collidepoint(self.goal):
            self.goal = self.new_goal()

        self.acceleration = (self.goal - self.rect.center).normalize() * self.ACCELERATION
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
