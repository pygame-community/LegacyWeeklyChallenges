import pygame
import pygame.gfxdraw
import numpy

from colorsys import hsv_to_rgb
from random import uniform, randint
from wclib.constants import SIZE

__all__ = [
    "ParticleManager",
    "Particle",
    "BouncingParticle",
    "ShootParticle",
    "FilledParticle",
]
class ParticleManager:

    __slots__ = ("particles",)

    LIMITER = 0
    MULTIPLIER = 50
    RANDOMNESS = 1
    TEN_THOUSAND_RANDOMNESS = 10000 * RANDOMNESS
    NORMAL_VALUES: list = numpy.random.default_rng().normal(size=TEN_THOUSAND_RANDOMNESS).tolist()
    iterative = 0

    # randomize pos, vel, life, color, size

    @classmethod
    def gauss(cls):
        cls.iterative += 1
        cls.iterative %= cls.TEN_THOUSAND_RANDOMNESS
        return cls.NORMAL_VALUES[cls.iterative - 1]

    @classmethod
    def randomize_pos(cls, pos):
        return (
            pygame.Vector2(2 ** (cls.gauss() * cls.RANDOMNESS), 2 ** (cls.gauss() * cls.RANDOMNESS))
            + pos
        )

    @classmethod
    def randomize_vel(cls, vel):
        return vel.rotate(cls.gauss() * 10 * cls.RANDOMNESS) * (cls.gauss() * 0.5 + 1)

    @classmethod
    def randomize_life(cls, life):
        return 1 + int((life - 1) * 2 ** (cls.gauss() * cls.RANDOMNESS))

    @classmethod
    def randomize_color(cls, color):
        if randint(0, 1):
            return pygame.Color(color) + pygame.Color(
                *(abs(int(cls.gauss() * cls.RANDOMNESS)) for _ in range(3))
            )
        else:
            return pygame.Color(color) - pygame.Color(
                *(abs(int(cls.gauss() * cls.RANDOMNESS)) for _ in range(3))
            )

    @classmethod
    def randomize_size(cls, size):
        return size * 2 ** (cls.gauss() * cls.RANDOMNESS)

    @staticmethod
    def random_color():
        r, g, b = hsv_to_rgb(uniform(0, 1), 0.8, 0.8)
        return pygame.Color(int(r * 255), int(g * 255), int(b * 255))

    def __init__(self):
        self.particles = set()

    def logic(self):
        to_remove = set()
        for particle in self.particles:
            particle.logic()
            if particle.age >= particle.life:
                to_remove.add(particle)
        self.particles.difference_update(to_remove)
        if len(self.particles) < self.LIMITER:
            self.burst(
                (randint(0, SIZE[0]), randint(0, SIZE[1])),
                pygame.Vector2(5),
                color=self.random_color(),
                level=1,
            )

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.particles.clear()

    def burst(self, pos, vel, color=None, level=1):
        n = self.MULTIPLIER * level
        for i in range(n):
            self.particles.add(
                Particle(
                    pos,
                    self.randomize_vel(2 * vel.rotate(i * 360 / n)),
                    40,
                    self.random_color(),
                    5,
                )
            )
            self.particles.add(
                BouncingParticle(
                    pos,
                    self.randomize_vel(2 * vel.rotate(i * 360 / n)),
                    60,
                    self.random_color(),
                    4,
                )
            )
            if color:
                self.particles.add(
                    FilledParticle(
                        pos,
                        self.randomize_vel(2 * vel.rotate(i * 360 / n)),
                        40,
                        self.randomize_color(color),
                        self.randomize_size(5),
                    )
                )
            else:
                self.particles.add(
                    FilledParticle(
                        pos,
                        2 * vel.rotate(i * 360 / n),
                        40,
                        self.random_color(),
                        5,
                    )
                )

    def firetrail(self, pos, vel, color=pygame.Color(255, 165, 0)):
        for _ in range(ParticleManager.MULTIPLIER):
            self.particles.add(Particle(pos, -vel, 20, pygame.Color(255, 0, 0), 3))
            self.particles.add(Particle(pos, self.randomize_vel(-vel), 20, color, 3))

    def shot(self, pos, vel, color=pygame.Color(255, 165, 0)):
        for _ in range(ParticleManager.MULTIPLIER):
            self.particles.add(ShootParticle(pos, self.randomize_vel(vel), 10, color, 5))


class Particle:

    __slots__ = ("pos", "vel", "life", "color", "size", "age", "decay")

    def __init__(
        self,
        pos: pygame.Vector2,
        vel: pygame.Vector2,
        life: int,
        color: pygame.Color,
        size: int,
    ):

        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.life = int(life)
        self.color = color
        self.size = int(size)

        self.age = 0
        self.decay = self.color // pygame.Color(life, life, life)

    def logic(self):
        self.age += 1
        self.pos += self.vel
        self.vel *= 0.9
        self.color -= self.decay

    def draw(self, display):
        pygame.gfxdraw.circle(
            display,
            int(self.pos.x),
            int(self.pos.y),
            int(self.size * self.age / self.life),
            self.color,
        )


class FilledParticle(Particle):
    def __init__(self, pos, vel, life, color, size):
        super().__init__(pos, vel, life, color, size)

    def draw(self, display):
        pygame.gfxdraw.filled_circle(
            display,
            int(self.pos.x),
            int(self.pos.y),
            int(self.size * self.age / self.life),
            self.color,
        )


class BouncingParticle(FilledParticle):
    def __init__(self, pos, vel, life, color, size):
        super().__init__(pos, vel, life, color, size)

    def logic(self):
        if not (0 < self.pos.x < SIZE[0]):
            self.vel.x *= -1
            if 0 > self.pos.x:
                self.pos.x = 0
            if SIZE[0] < self.pos.x:
                self.pos.x = SIZE[0]
        if not (0 < self.pos.y < SIZE[1]):
            self.vel.y *= -1
            if 0 > self.pos.y:
                self.pos.y = 0
            if SIZE[0] < self.pos.y:
                self.pos.y = SIZE[1]

        self.age += 1
        self.pos += self.vel


class ShootParticle(Particle):
    def __init__(self, pos, vel, life, color, size):
        super().__init__(pos, vel, life, color, size)

    def draw(self, display):
        pygame.gfxdraw.line(
            display,
            int(self.pos.x),
            int(self.pos.y),
            int(self.pos.x + self.vel.x),
            int(self.pos.y + self.vel.y),
            self.color,
        )
