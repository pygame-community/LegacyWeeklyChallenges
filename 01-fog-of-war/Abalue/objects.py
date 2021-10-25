"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
a fog of war, without needed
Feel free to modify everything in this file to your liking.
"""
from random import choice, gauss
from operator import attrgetter

import pygame

from wclib import SIZE
from .utils import clamp, from_polar, load_image, random_in_rect

SCREEN = pygame.Rect(0, 0, *SIZE)


class Renderer:
    def __init__(self):
        self.background_color = 0x66856C

    def handle_event(self):
        pass

    def logic(self, **kwargs):
        pass

    def draw(self, display, objects):
        display.fill(self.background_color)
        for obj in objects:
            display.blit(obj.sprite, obj.pos)


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
        objects = kwargs["objects"]
        for obj in objects:
            if isinstance(obj, Menu):
                if obj.open:
                    return
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
        self.sprite.convert()
        self.goal = self.new_goal()
        self.dist_to_player = pygame.Vector2()

    def new_goal(self):
        direction = from_polar(60, gauss(self.velocity.as_polar()[1], 30))
        return self.rect.center + direction

    def logic(self, **kwargs):
        middle_area = SCREEN.inflate(-30, -30)
        while self.rect.collidepoint(self.goal) or not middle_area.collidepoint(self.goal):
            self.goal = self.new_goal()

        self.acceleration = (self.goal - self.rect.center).normalize() * self.ACCELERATION

        for object in kwargs["objects"]:
            if isinstance(object, Player):
                self.dist_to_player = (self.pos - object.pos).length()
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


class Menu:
    def __init__(self):
        # Should be a subclass of object but I'm lazy
        self.sprite = pygame.Surface((1, 1))
        self.pos = pygame.Vector2(-2, -2)
        #

        self.BG_COLOR = pygame.Color(85, 125, 245)
        self.BG_ALPHA = 220
        self.OPEN_VEL = 8
        self.FONT_SIZE = 22
        pygame.font.init()
        self.FONT = pygame.font.SysFont("helvetica", self.FONT_SIZE)
        self.FONT_COLOR = pygame.Color(5, 45, 165)
        __achievements__ = [  # can't grab from main to avoid recursive issues :(
            "Default",
            "Casual",
            "Ambitious",
            "Adventurous",
        ]
        self.ACHIEVEMENTS = [self.FONT.render(a, True, self.FONT_COLOR) for a in __achievements__]
        self.gaps = [20] * len(self.ACHIEVEMENTS)
        self.OPEN_ME_TXT = self.FONT.render(
            "press tab to toggle menu...", True, pygame.Color(255, 255, 255)
        )

        self.open = False
        self.has_opened = False
        self.selected = 2
        height = pygame.display.get_surface().get_height()
        width = 250
        self.rect = pygame.Rect(-width, 0, width, height)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.open = not self.open
                self.has_opened = True
            if event.key == pygame.K_UP and self.open:
                self.selected -= 1
                if self.selected < 0:
                    self.selected = len(self.ACHIEVEMENTS) - 1
            if event.key == pygame.K_DOWN and self.open:
                self.selected += 1
                if self.selected >= len(self.ACHIEVEMENTS):
                    self.selected = 0

    def logic(self, *args, **kwargs):
        # print(self.rect.topleft)
        # open and close menu
        if self.open and self.rect.right < self.rect.w:
            self.rect.x += self.OPEN_VEL
            self.rect.x = min(0, self.rect.x)
        elif not self.open and self.rect.left > -self.rect.w:
            self.rect.x -= self.OPEN_VEL
            self.rect.right = max(0, self.rect.right)

    def draw(self, display):
        surface = pygame.Surface(self.rect.size).convert()
        surface.set_alpha(self.BG_ALPHA)
        surface.fill(self.BG_COLOR)
        for i, a in enumerate(self.ACHIEVEMENTS):
            if self.selected == i:
                if self.gaps[i] < 40:
                    self.gaps[i] += 2
                    self.gaps[i] = min(self.gaps[i], 40)
                pygame.draw.rect(
                    surface,
                    pygame.Color(220, 220, 220),
                    (self.rect.x, 40 + i * 50, self.rect.w, 50),
                )
            else:
                if self.gaps[i] > 20:
                    self.gaps[i] -= 2
                    self.gaps[i] = max(self.gaps[i], 20)
            surface.blit(a, (self.rect.x + self.gaps[i], 50 + i * 50))
        display.blit(surface, (self.rect.topleft))
        if not self.has_opened:
            display.blit(self.OPEN_ME_TXT, (400, 700))


class Fog(Renderer):
    def __init__(self, player_rect):
        super().__init__()
        self.RADIUS = 200
        self.FADE_LEN = 150
        self.FADE_ITERS = 40
        self.COLOR = pygame.Color(0, 0, 0, 255)

        self.ALPHA_RANGE = [
            int((self.FADE_ITERS - i - 1) / self.FADE_ITERS * 200) for i in range(self.FADE_ITERS)
        ]
        self.RADIUS_RANGE = [
            self.RADIUS - self.FADE_LEN * i / self.FADE_ITERS for i in range(self.FADE_ITERS)
        ]

        self.pos = pygame.Vector2(player_rect.center)
        self.size = pygame.Vector2(pygame.display.get_window_size()) * 2
        self.mode = "ambitious"

        self.explore_surf = pygame.Surface(self.size / 2).convert_alpha()
        self.explore_mask = pygame.Surface(self.size / 2).convert_alpha()
        self.player_surf = pygame.Surface((self.RADIUS * 2, self.RADIUS * 2)).convert_alpha()
        self.player_mask = pygame.Surface((self.RADIUS * 2, self.RADIUS * 2)).convert_alpha()
        self.player_mask.fill(pygame.Color(254, 254, 254, 255))
        self.player_mask_casual = pygame.Surface((self.RADIUS * 2, self.RADIUS * 2)).convert_alpha()
        self.player_mask_casual.fill(pygame.Color(254, 254, 254, 255))
        pygame.draw.circle(
            self.player_mask_casual,
            pygame.Color(0, 0, 0, 0),
            (self.RADIUS, self.RADIUS),
            self.RADIUS,
        )

        # add player view mask
        for i in range(self.FADE_ITERS):
            color = pygame.Color(self.COLOR)
            color.a = self.ALPHA_RANGE[i]
            pygame.draw.circle(
                self.player_mask,
                color,
                (self.RADIUS, self.RADIUS),
                self.RADIUS_RANGE[i],
            )

    def logic(self, player, menu):
        self.pos.update(player.rect.center)
        pygame.draw.circle(self.explore_mask, pygame.Color(0, 0, 0, 200), self.pos, self.RADIUS)
        if menu.selected == 0:
            self.mode = "default"
        if menu.selected == 1:
            self.mode = "casual"
        elif menu.selected == 2:
            self.mode = "ambitious"
        elif menu.selected == 3:
            self.mode = "adventurous"

    def draw(self, screen, all_objects):
        # fill background
        if self.mode == "default":
            super().draw(screen, all_objects)
            return
        screen.fill(0x66856C)
        self.explore_surf.fill(0x66856C)
        self.player_surf.fill(0x66856C)
        # draw objects
        for object in sorted(all_objects, key=attrgetter("rect.bottom")):
            if isinstance(object, Ghost):
                fade = (
                    min(self.RADIUS, self.RADIUS * 5 / 3 - object.dist_to_player * 1.4)
                    / self.RADIUS
                    * 255
                )
                object.sprite.set_alpha(fade)
                self.player_surf.blit(
                    object.sprite, object.pos - self.pos + (self.RADIUS, self.RADIUS)
                )
            else:
                self.player_surf.blit(
                    object.sprite, object.pos - self.pos + (self.RADIUS, self.RADIUS)
                )
                if isinstance(object, Player):
                    player = object
            if not isinstance(object, Object8Directional):
                self.explore_surf.blit(object.sprite, object.pos)

        # add explore mask
        if self.mode == "adventurous":
            self.explore_surf.blit(self.explore_mask, (0, 0))
        else:
            self.explore_surf.fill(pygame.Color(0, 0, 0, 255))
        pygame.draw.circle(self.explore_surf, pygame.Color(0, 0, 0, 0), self.pos, self.RADIUS)
        if self.mode != "casual":
            self.player_surf.blit(self.player_mask, (0, 0))
        else:
            self.player_surf.blit(self.player_mask_casual, (0, 0))
        self.player_surf.set_colorkey(pygame.Color(254, 254, 254))
        screen.blit(self.explore_surf, (0, 0))
        screen.blit(
            self.player_surf,
            pygame.Vector2(player.rect.center) - (self.RADIUS, self.RADIUS),
        )
