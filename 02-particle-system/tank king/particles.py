import pygame
import random
import time
from .utils import map_to_range, clamp, SIZE
from typing import Union

scale = pygame.transform.scale
rotate = pygame.transform.rotate


class ParticleSystem:
    def __init__(self):
        self.particles: list[BaseParticle] = []

    def add_particle(
        self, pos, vel, particle_type: Union[str, None] = None, extra_params: dict = None
    ):
        if particle_type is not None:
            if particle_type == "trail":
                self.particles.append(TrailParticles(pos, vel))
            elif particle_type == "exhaust":
                self.particles.append(ExhaustParticles(pos, vel))
            elif particle_type == "damage":
                self.particles.append(DamageParticle(pos, vel, extra_params=extra_params))
            elif particle_type == "break":
                self.particles.append(ObjectBreakingParticle(pos, vel, extra_params=extra_params))

    def update(self, screen: pygame.Surface):
        self.particles = [i for i in self.particles if i.alive]
        for i in self.particles:
            i.update()
            i.draw(screen)


class BaseParticle:
    def __init__(self, pos, vel, sprite=None, extra_parameters: dict = None):
        self.vel = pygame.Vector2(*vel)
        self.center = pygame.Vector2(*pos)
        self.sprite = sprite
        self.alive = True
        self.rotation = 0.0
        self.extra_params = extra_parameters

    def update(self):
        self.center += self.vel

    def draw(self, screen: pygame.Surface):
        if self.sprite is not None:
            rotated_image = rotate(self.sprite, int(self.rotation))
            screen.blit(rotated_image, rotated_image.get_rect(center=self.center))


class TrailParticles(BaseParticle):
    def __init__(self, pos, vel, size=2):
        super().__init__(pos, vel)
        self.rotation = random.randint(0, 360)
        self.timer = time.time()
        self.size = size
        self.original_size = size
        self.real_size = size

    def update(self):
        if time.time() - self.timer > 0.25:
            self.original_size -= 0.1
            self.size = int(self.original_size)
            self.timer = time.time()
            # self.sprite.set_alpha(map_to_range(self.size, 0, self.real_size, 0, 255))
        if self.size < 1:
            self.size = 1
            self.alive = False
        # self.sprite = scale(self.sprite, (self.size * 3.3, self.size * 3.3))
        super().update()

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(
            screen, (255, 125, 0), pygame.Rect(self.center.x, self.center.y, self.size, self.size)
        )


class ExhaustParticles(BaseParticle):
    particle_sprite = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(
        particle_sprite,
        (0, 255, 0),
        particle_sprite.get_rect().center,
        particle_sprite.get_width() // 2,
    )

    def __init__(self, pos, vel, size=5):
        super().__init__(pos, vel, ExhaustParticles.particle_sprite)
        self.rotation = random.randint(0, 360)
        color = (
            random.choice([0, 150, 255]),
            random.choice([0, 150, 255]),
            random.choice([0, 150, 255]),
        )
        self.sprite.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self.sprite.fill(color, special_flags=pygame.BLEND_ADD)
        self.size = size
        self.original_size = size
        self.real_size = size

    def update(self):
        self.original_size -= clamp(random.random(), 0.025, 0.125)
        self.size = int(self.original_size)
        self.sprite.set_alpha(map_to_range(self.size, 0, self.real_size, 0, 255))
        if self.size < 1:
            self.size = 1
            self.alive = False
        self.sprite = scale(self.sprite, (self.size * 3.3, self.size * 3.3))
        super().update()


class DamageParticle(BaseParticle):
    def __init__(self, pos, vel, extra_params: dict = None):
        super().__init__(pos, vel)
        self.player_sprite: pygame.Surface = extra_params["sprite"]
        size = random.randint(1, 10)
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        rect = pygame.Rect(
            random.randint(0, self.player_sprite.get_width() - size),
            random.randint(0, self.player_sprite.get_height() - size),
            size,
            size,
        )
        self.sprite.blit(self.player_sprite, (0, 0), rect)
        self.player_sprite.lock()
        for i in range(size * 10):
            x, y = random.randint(0, self.player_sprite.get_width() - 1), random.randint(
                0, self.player_sprite.get_height() - 1
            )
            if self.player_sprite.get_at([x, y])[3] > 128:
                self.player_sprite.set_at(
                    [x, y], (58, 68, 102, 255)
                )  # a particular color selected from image
        self.player_sprite.unlock()
        self.size = size
        self.original_size = size
        self.real_size = size
        self.timer = time.time()

    def update(self):
        self.rotation += 1
        if time.time() - self.timer > 0.25:
            self.timer = time.time()
            self.original_size -= 0.1
            self.size = int(self.original_size)
        if self.size < 1:
            self.size = 1
            self.alive = False
        super().update()

    def draw(self, screen: pygame.Surface):
        super().draw(screen)


class ObjectBreakingParticle(BaseParticle):
    def __init__(self, pos, vel, extra_params: dict = None):
        super().__init__(pos, vel, extra_params["sprite"])
        # self.color = extra_params['color']
        self.points = [
            [
                random.randint(0, self.sprite.get_width()),
                random.randint(0, self.sprite.get_height()),
            ]
            for _ in range(3)
        ]
        # p = [[0, 0], [self.sprite.get_width(), 0], [self.sprite.get_width(), self.sprite.get_height()]]
        # p += points
        # pygame.draw.polygon(self.sprite, (0, 255, 0), points)
        self.surf = pygame.Surface(self.sprite.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(self.surf, (255, 255, 255), self.points)
        self.sprite.blit(self.surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # extracting only the non-transparent portion
        all_x = [i[0] for i in self.points]
        all_y = [i[1] for i in self.points]
        x1 = min(all_x)
        x2 = max(all_x)
        y1 = min(all_y)
        y2 = max(all_y)
        rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
        # pygame.draw.rect(self.sprite, (0, 255, 0), pygame.Rect(x1, y1, x2 - x1, y2 - y1), 1)
        self.sprite = self.sprite.subsurface(rect)
        self.rot_speed = random.randint(1, 5)
        self.timer = time.time()

    def update(self):
        self.rotation += self.rot_speed
        offset = 50
        if (
            self.center.x < -self.sprite.get_width() - offset
            or self.center.x > SIZE[0] + self.sprite.get_width() + offset
        ):
            self.alive = False
        elif (
            self.center.y < -self.sprite.get_height() - offset
            or self.center.y > SIZE[1] + self.sprite.get_height() + offset
        ):
            self.alive = False
        else:
            if (
                time.time() - self.timer > 10
                and max(self.sprite.get_width(), self.sprite.get_height()) < 25
            ):
                self.alive = False
        super().update()
