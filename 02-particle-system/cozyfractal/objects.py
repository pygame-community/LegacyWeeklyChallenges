"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
your particle system, without needing to implement a game that
goes with it too.
Feel free to modify everything in this file to your liking.
"""
import random
import time
from collections import deque, defaultdict
from colorsys import hsv_to_rgb
from functools import lru_cache
from operator import attrgetter
from random import gauss, choices, uniform

import pygame

# noinspection PyPackages
from .utils import *
from .particles import *


class State:
    def __init__(self, *initial_objects: "Object"):
        self.objects = set()
        self.objects_to_add = set()

        for obj in initial_objects:
            self.add(obj)

        self.by_type = {}

    def add(self, obj: "Object | ParticleGroup"):
        # We don't add objects immediately,
        # as it could invalidate iterations.
        self.objects_to_add.add(obj)
        obj.state = self
        return obj

    def logic(self):
        self.by_type = defaultdict(list)
        for obj in self.objects:
            self.by_type[type(obj)].append(obj)

        to_remove = set()
        for obj in self.objects:
            obj.logic()
            if not obj.alive:
                to_remove.add(obj)
        self.objects.difference_update(to_remove)
        self.objects.update(self.objects_to_add)
        self.objects_to_add.clear()

    def draw(self, screen):
        for obj in sorted(self.objects, key=attrgetter("Z")):
            obj.draw(screen)

    def handle_event(self, event):
        for obj in self.objects:
            if obj.handle_event(event):
                break


class Object:
    """
    The base class for all objects of the game.

    Controls:
     - [d] Show the hitboxes for debugging.
    """

    # Controls the order of draw.
    # Objects are sorted according to Z before drawing.
    Z = 0

    # All the objects are considered circles,
    # Their hit-box is scaled by the given amount, to the advantage of the player.
    HIT_BOX_SCALE = 1.2

    def __init__(self, pos, vel, sprite: pygame.Surface):
        # The state is set when the object is added to a state.
        self.state: "State" = None
        self.center = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.sprite = sprite
        self.rotation = 0.0  # for the sprite
        self.alive = True
        # Cache it every frame, as it was taking 10% (!!) of the processing power.
        self.rect = self.get_rect()

    def __str__(self):
        return f"<{self.__class__.__name__}(center={self.center}, vel={self.vel}, rotation={int(self.rotation)})>"

    @property
    def radius(self):
        """All objects are considered circles of this radius for collisions."""
        # The 1.2 is to be nicer to the player
        return self.sprite.get_width() / 2 * self.HIT_BOX_SCALE

    def distance_squared_to(self, other: "Object") -> float:
        dx = (self.center.x - other.center.x) % SIZE[0]
        dx = min(dx, SIZE[0] - dx)
        dy = (self.center.y - other.center.y) % SIZE[1]
        dy = min(dy, SIZE[1] - dy)
        return dx ** 2 + dy ** 2

    def collide(self, other: "Object") -> bool:
        """Whether two objects collide."""
        # The distance must be modified because everything wraps
        return self.distance_squared_to(other) <= (self.radius + other.radius) ** 2

    @property
    def rotated_sprite(self):
        # We round the rotation to the nearest integer so that
        # the cache has a chance to work. Otherwise there would
        # always be cache misses: it is very unlikely to have
        # to floats that are equal.
        return rotate_image(self.sprite, int(self.rotation))

    def get_rect(self):
        """Compute the rectangle containing the object."""
        return self.rotated_sprite.get_rect(center=self.center)

    def handle_event(self, event):
        """Override this method to make an object react to events.
        Returns True if the event was handled and should not be given to other objects."""
        return False

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.rect)

        # Goal: wrap around the screen.
        w, h = SIZE
        tl = 0, 0
        tr = w, 0
        br = w, h
        bl = 0, h

        shifts = []
        for a, b, offset in [
            (tl, tr, (0, h)),
            (bl, br, (0, -h)),
            (tl, bl, (w, 0)),
            (tr, br, (-w, 0)),
        ]:
            # For each side [a,b] of the screen that it overlaps
            if self.rect.clipline(a, b):
                shifts.append(offset)
                # Draw the spaceship at the other edge too.
                screen.blit(
                    self.rotated_sprite,
                    self.rotated_sprite.get_rect(center=self.center + offset),
                )

        # Take care of the corners of the screen.
        # Here I assume that no object can touch two sides of the screen
        # at the same time. If so, the code wouldn't be correct, but still
        # produce the expected result -.-'
        assert len(shifts) <= 2
        if len(shifts) == 2:
            screen.blit(
                self.rotated_sprite,
                self.rotated_sprite.get_rect(center=self.center + shifts[0] + shifts[1]),
            )

        # To see the exact size of the hitboxes
        if pygame.key.get_pressed()[pygame.K_d]:
            pygame.draw.circle(screen, "red", self.center, self.radius, width=1)

    def logic(self, **kwargs):
        # self.vel = clamp_vector(self.vel, self.MAX_VEL)
        self.center += self.vel

        self.center.x %= SIZE[0]
        self.center.y %= SIZE[1]

        self.rect = self.get_rect()


class ReactorParticles(ParticleGroup, Circle, WrapTorus, MovePolar):
    continuous = True
    gradient = ("#FFFEC9", "#FF8B12", "#82020090", "#39000050")
    speed = Gauss(2)
    max_age = 30
    wrap_rect = SCREEN


class Player(Object):
    Z = 10
    HIT_BOX_SCALE = 0.7  # harder to touch the player
    ACCELERATION = 0.7
    FRICTION = 0.9
    ROTATION_ACCELERATION = 3
    INITIAL_ROTATION = 90
    FIRE_COOLDOWN = 15  # frames
    SCALE = 3

    def __init__(self, pos, vel):
        super().__init__(pos, vel, load_image("player", self.SCALE))

        self.speed = 0
        self.fire_cooldown = -1

        self.reactor_on = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.fire()

    def sprite_to_screen(self, pos):
        pos = pygame.Vector2(pos) + (0.5, 0.5)
        pos -= pygame.Vector2(self.sprite.get_size()) / 2 / self.SCALE
        pos.rotate_ip(-self.rotation)
        return self.center + pos * self.SCALE

    @property
    def reactor_pos(self):
        r = self.sprite_to_screen((10, 18))
        return r

    @property
    def world_rotation(self):
        return -self.rotation - self.INITIAL_ROTATION

    def logic(self):
        if not self.reactor_on:
            self.state.add(
                ReactorParticles(
                    pos=Lambda(lambda: self.reactor_pos - (ReactorParticles.radius / 2,) * 2),
                    angle=Gauss(lambda: 180 + self.world_rotation, spread=10),
                )
            )
            self.reactor_on = True
        self.fire_cooldown -= 1

        # For continuous shooting:
        # if pressed[pygame.K_SPACE]:
        #     self.fire(new_objects)

        # Motion
        pressed = pygame.key.get_pressed()
        rotation_acc = pressed[pygame.K_LEFT] - pressed[pygame.K_RIGHT]
        raw_acceleration = 0.5 * pressed[pygame.K_DOWN] - pressed[pygame.K_UP]

        self.speed += raw_acceleration * self.ACCELERATION
        self.speed *= self.FRICTION  # friction

        # The min term makes it harder to turn at slow speed.
        self.rotation += rotation_acc * self.ROTATION_ACCELERATION * min(1.0, 0.4 + abs(self.speed))

        self.vel.from_polar((self.speed, self.INITIAL_ROTATION - self.rotation))

        super().logic()

    def fire(self):
        if self.fire_cooldown >= 0:
            return

        self.fire_cooldown = self.FIRE_COOLDOWN
        bullet = Bullet(self.center, self.world_rotation)
        self.state.add(bullet)

        # You can add particles here too.
        ...

    def on_asteroid_collision(self, asteroid: "Asteroid"):
        # For simplicity I just explode the asteroid, but depending on what you aim for,
        # it might be better to just loose some life or even reset the game...
        asteroid.explode(Bullet(self.center, self.rotation))

        # Add particles here (and maybe damage the ship or something...)
        ...


class Bullet(Object):
    Z = 1
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

        # Maybe some trail particles here ? You can put particles EVERYWHERE. Really.
        ...


def random_color():
    r, g, b = hsv_to_rgb(uniform(0, 1), 0.8, 0.8)
    return int(r * 255), int(g * 255), int(b * 255)


NB_COLORS = 10
COLORS = [random_color() for _ in range(NB_COLORS)]


class AsteroidExplosion(ParticleGroup, WrapTorus, MovePolar, AngularVel, Circle):
    Z = 1
    wrap_rect = SCREEN
    angle = Uniform(0, 360)
    rotation_speed = 2

    speed = Gauss(4)
    max_age = 50
    nb = 400

    colors_fade_to_transparent = True
    nb_seed = NB_COLORS
    gradient = COLORS


class AsteroidExplosion2(ParticleGroup, SurfComponent, WrapTorus, MovePolar):
    nb = 100
    max_age = 50
    wrap_rect = SCREEN
    angle = Uniform(0, 360)
    speed = Gauss(3)

    nb_seed = 6
    params_shape = (nb_seed, NB_COLORS)

    def compute_params(self):
        return (self.seeds,)

    def get_surf(cls, seed, color):
        pass


AsteroidExplosion2(color=2)


class Asteroid(Object):
    AVG_SPEED = 1
    EXPLOSION_SPEED_BOOST = 1.8

    def __init__(self, pos, vel, size=4, color=None):
        assert 1 <= size <= 4
        self.level = size
        # We copy to change the color
        self.color = color or random.choice(COLORS)

        super().__init__(pos, vel, self.colored_image(size, self.color))

    @staticmethod
    @lru_cache(100)
    def colored_image(size, color):
        sprite = load_image(f"asteroid-{16*2**size}").copy()
        sprite.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        return sprite

    def logic(self):
        super().logic()

        for bullet in self.state.by_type[Bullet]:
            if not bullet.alive:
                continue
            if self.collide(bullet):
                self.explode(bullet)
                return

        for player in self.state.by_type[Player]:
            if not player.alive:
                continue
            if self.collide(player):
                player.on_asteroid_collision(self)

    def explode(self, bullet):
        bullet.alive = False
        self.alive = False
        if self.level > 1:
            # We spawn two smaller asteroids in the direction perpendicular to the collision.
            perp_velocity = pygame.Vector2(bullet.vel.y, -bullet.vel.x)
            perp_velocity.scale_to_length(self.vel.length() * self.EXPLOSION_SPEED_BOOST)
            for mult in (-1, 1):
                self.state.add(
                    Asteroid(self.center, perp_velocity * mult, self.level - 1, self.color)
                )

        # You'll add particles here for sure ;)
        self.state.add(
            AsteroidExplosion(
                pos=Constant(self.center), seeds=Constant(COLORS.index(self.color), int)
            )
        )

    @classmethod
    def generate_many(cls, nb=10):
        """Return a set of nb Asteroids randomly generated."""
        objects = set()
        for _ in range(nb):
            angle = uniform(0, 360)
            distance_from_center = gauss(SIZE[1] / 2, SIZE[1] / 12)
            pos = SCREEN.center + from_polar(distance_from_center, angle)
            vel = from_polar(gauss(cls.AVG_SPEED, cls.AVG_SPEED / 6), gauss(180 + angle, 30))
            size = choices([1, 2, 3, 4], [4, 3, 2, 1])[0]
            objects.add(cls(pos, vel, size))

        return objects


class FpsCounter(Object):
    """
    A wrapper around pygame.time.Clock that shows the FPS on screen.

    Controls:
     - [F] Toggles the display of FPS
     - [U] Toggles the capping of FPS
    """

    Z = 1000
    REMEMBER = 30

    def __init__(self, fps):
        self.hidden = False
        self.cap_fps = False
        self.target_fps = fps
        self.clock = pygame.time.Clock()
        self.frame_starts = deque([time.time()], maxlen=self.REMEMBER)

        dummy_surface = pygame.Surface((1, 1))
        super().__init__((4, 8), (0, 0), dummy_surface)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self.hidden = not self.hidden
            elif event.key == pygame.K_u:
                self.cap_fps = not self.cap_fps

    def logic(self, **kwargs):
        # Passing 0 to tick() removes the cap on FPS.
        self.clock.tick_busy_loop(self.target_fps * self.cap_fps)

        self.frame_starts.append(time.time())

    @property
    def current_fps(self):
        if len(self.frame_starts) <= 1:
            return 0
        seconds = self.frame_starts[-1] - self.frame_starts[0]
        return (len(self.frame_starts) - 1) / seconds

    def draw(self, screen):
        if self.hidden:
            return

        color = "#89C4F4"
        t = text(f"FPS: {int(self.current_fps)}", color)
        r = screen.blit(t, self.center)  # Not really the center but it wasn't made for UI

        nb_particles = sum(p.nb for p in self.state.objects if isinstance(p, ParticleGroup))
        t = text(f"Particles: {nb_particles}", color)
        screen.blit(t, r.bottomleft)
