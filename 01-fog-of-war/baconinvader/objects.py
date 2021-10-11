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


class Darkness:
    def __init__(self, min_light=0, reveal_light=40):
        self.rect = SCREEN.copy()

        self.min_light = min_light  # minimum light level
        self.reveal_light = reveal_light  # how light an uncovered part of the map is

        self.surface = pygame.Surface((SCREEN.w, SCREEN.h), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 255 - min_light))

        # uncovered part of the map
        self.shown_surface = self.surface.copy()

    def draw(self, screen, light):

        # draw darkness
        self.surface.blit(self.shown_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(self.surface, (0, 0))

        # clear light
        pygame.gfxdraw.box(self.surface, light.rect, (0, 0, 0, 255 - self.min_light))


class Light:
    def __init__(self, darkness, pos, light, max_light_radius, min_light_radius, radius):
        self.radius = radius

        # strength of the light, drops off to 0 at distance radius
        self.light = light
        # radius up to which the light is as bright as possible
        self.max_light_radius = max_light_radius

        self.min_light_radius = min_light_radius

        self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.radius * 2, self.radius * 2)

        self.darkness = darkness
        self.create_surface()

    # create the actual light surface
    def create_surface(self):
        import pygame.gfxdraw

        self.surface = pygame.Surface((self.rect.w, self.rect.h), flags=pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))

        # draw center bright point
        self.max_light_surface = pygame.Surface(
            (self.max_light_radius * 2, self.max_light_radius * 2),
            flags=pygame.SRCALPHA,
        )
        pygame.gfxdraw.filled_circle(
            self.max_light_surface,
            self.max_light_radius,
            self.max_light_radius,
            self.max_light_radius,
            (0, 0, 0, self.light),
        )

        self.surface.blit(
            self.max_light_surface,
            (self.radius - self.max_light_radius, self.radius - self.max_light_radius),
        )

        # how much dimmer the light should get per pixel
        light_change_per_pixel = (self.light) / (self.radius - self.max_light_radius)

        min_light_level = self.light - (
            light_change_per_pixel * (self.min_light_radius - self.max_light_radius)
        )

        # draw fade
        # reversed to prevent gaps in the drawing
        for i in reversed(range((self.radius - (self.max_light_radius)) * 1)):

            pix = i

            dist_from_center = self.max_light_radius + pix
            light_level = clamp(
                int(self.light - (light_change_per_pixel * pix)),
                min_light_level,
                255 - self.darkness.min_light,
            )
            colour = (0, 0, 0, light_level)

            pygame.gfxdraw.filled_circle(
                self.surface,
                self.rect.w // 2,
                self.rect.h // 2,
                int(self.max_light_radius + pix),
                colour,
            )

        # draw full_surface (surface that will be permanently drawn on the FOW)
        self.full_surface = pygame.Surface(
            (self.radius * 2, self.radius * 2), flags=pygame.SRCALPHA
        )
        self.full_surface.fill((0, 0, 0, 255))
        pygame.gfxdraw.filled_circle(
            self.full_surface,
            self.radius,
            self.radius,
            self.radius,
            (0, 128, 0, 255 - self.darkness.reveal_light),
        )

    def get_visible_objects(self, objects):
        visible_objects = []
        for obj in objects:
            visible = True

            if hasattr(obj, "velocity"):  # ghosts, basically
                dx = obj.rect.centerx - self.rect.centerx
                dy = obj.rect.centery - self.rect.centery
                dist = ((dx ** 2) + (dy ** 2)) ** 0.5

                # object not within range
                if dist > self.radius:
                    visible = False

            if visible:
                visible_objects.append(obj)

        return visible_objects

    def update(self):
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def draw(self, screen, visible_objects):

        self.draw_surface = self.surface.copy()

        # get objects in range
        objects_in_range = []
        dists = []
        for obj in visible_objects:
            if type(obj) == Player:
                continue

            dx = obj.rect.centerx - self.rect.centerx
            dy = obj.rect.centery - self.rect.centery
            dist = ((dx ** 2) + (dy ** 2)) ** 0.5

            # object within range
            if dist <= self.radius:
                objects_in_range.append(obj)
                dists.append(dist)

        # create shadows
        self_center_pos = pygame.Vector2(self.pos)
        self_center_pos.x += self.rect.w / 2
        self_center_pos.y += self.rect.h / 2

        for i, obj in enumerate(objects_in_range):
            center_pos = pygame.Vector2(obj.pos)
            center_pos.x += obj.rect.w / 2
            center_pos.y += obj.rect.h / 2

            angle = pygame.Vector2(0, 0).angle_to(center_pos - self_center_pos)

            shadow_start_length = (obj.rect.w + obj.rect.h) / 2

            dist = dists[i]

            # create the vertices of the shadow polygon

            # "start" points are closest to the object
            # "side" points are the points which are at the edge of the light radius
            # "end" points are points that are used to make the shadow complete and prevent gaps from being left
            shadow_start_left = pygame.Vector2((-shadow_start_length / 2, 0))
            shadow_start_left.rotate_ip(angle + 90)
            shadow_start_left += center_pos

            shadow_side_left = shadow_start_left - self_center_pos
            shadow_side_left.scale_to_length(self.radius)
            shadow_side_left += self_center_pos

            shadow_end_left = center_pos - self_center_pos
            shadow_end_left.scale_to_length(self.radius)
            shadow_end_left += shadow_side_left

            shadow_start_right = pygame.Vector2((shadow_start_length / 2, 0))
            shadow_start_right.rotate_ip(angle + 90)
            shadow_start_right += center_pos

            shadow_side_right = shadow_start_right - self_center_pos
            shadow_side_right.scale_to_length(self.radius)
            shadow_side_right += self_center_pos

            shadow_end_right = center_pos - self_center_pos
            shadow_end_right.scale_to_length(self.radius)
            shadow_end_right += shadow_side_right

            pygame.gfxdraw.filled_circle(
                self.draw_surface,
                int(center_pos.x - self.pos.x),
                int(center_pos.y - self.pos.y),
                int(shadow_start_length // 2),
                (0, 0, 0, 0),
            )

            ##uncomment these and you can see the points in action
            ##green - start, blue - side, red - end
            # pygame.gfxdraw.filled_circle(screen, int(shadow_start_left.x), int(shadow_start_left.y), 5 , (0,255,0,128))
            # pygame.gfxdraw.filled_circle(screen, int(shadow_start_right.x), int(shadow_start_right.y), 5 , (0,255,0,128))

            # pygame.gfxdraw.filled_circle(screen, int(shadow_side_left.x), int(shadow_side_left.y), 7 , (255,0,0,128))
            # pygame.gfxdraw.filled_circle(screen, int(shadow_side_right.x), int(shadow_side_right.y), 7 , (255,0,0,128))

            # pygame.gfxdraw.filled_circle(screen, int(shadow_end_left.x), int(shadow_end_left.y), 9 , (0,0,255,128))
            # pygame.gfxdraw.filled_circle(screen, int(shadow_end_right.x), int(shadow_end_right.y), 9 , (0,0,255,128))

            # offset so they can be relative to the draw surface
            shadow_start_left -= self.pos
            shadow_start_right -= self.pos
            shadow_side_left -= self.pos
            shadow_side_right -= self.pos
            shadow_end_left -= self.pos
            shadow_end_right -= self.pos

            pygame.gfxdraw.filled_polygon(
                self.draw_surface,
                [
                    shadow_start_left,
                    shadow_side_left,
                    shadow_end_left,
                    shadow_end_right,
                    shadow_side_right,
                    shadow_start_right,
                ],
                (0, 0, 0, 0),
            )

        self.darkness.surface.blit(
            self.draw_surface, self.rect, special_flags=pygame.BLEND_RGBA_SUB
        )

    def draw_uncovered(self, screen):
        # draw the uncovered parts of the map
        self.darkness.shown_surface.blit(
            self.full_surface, self.rect, special_flags=pygame.BLEND_RGBA_MIN
        )
