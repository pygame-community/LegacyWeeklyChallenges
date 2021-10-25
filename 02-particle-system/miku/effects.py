import pygame, sys, random, math
from functools import lru_cache
import numpy as np

pygame.init()


class EffectManager:
    def __init__(self, limit=1000):
        self.particle_limit = limit
        self.length = 1
        self.particles = set()
        self.tasks = []
        # task = [(particle, args), amount left, wait after spawn]

    def run(self):
        self.length = len(self.particles)
        to_remove = set()
        number = self.length - self.particle_limit
        for particle in self.particles:
            particle.logic()
            if particle.dead:
                to_remove.add(particle)
            elif number > 0:
                number -= 1
                to_remove.add(particle)
        self.particles.difference_update(to_remove)
        for task in self.tasks:
            task[2][0] += 1
            if task[2][0] == task[2][1]:
                task[2][0] = 0
                task[1] -= 1
                self.particles.add(task[0]())
            elif task[2][1] == -1:
                self.particles.add(task[0]())
            if task[1] == 0:
                self.tasks.remove(task)

    def add_task(self, particle, amount, wait_ticks):
        self.tasks.append([particle, amount, [0, wait_ticks]])

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)


class Particle:
    @lru_cache(maxsize=2000, typed=True)
    def __init__(self, position=(0, 0), lifetime=300, surface=None):
        self.position = position
        self.pos = position
        self.lifetime = lifetime
        self.surface = surface
        self.dead = False

    def life(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.dead = True

    def logic(self):
        self.life()

    def draw(self, window):
        pass


class CrashParticle(Particle):
    @lru_cache(maxsize=2000, typed=True)
    def __init__(self, position=(0, 0), pieces=20, lifetime=300, speed=15, surface=None):
        super().__init__(position, lifetime, surface)
        size = surface.get_size()
        needed_size = (size[0] // 8, size[1] // 8)
        self.need_size = needed_size
        self.speed = speed
        self.change_frame = speed
        s = pygame.Surface.copy(self.surface)
        center = s.get_rect()
        center.x, center.y = position[0], position[1]
        self.center = center.center

        self.mini_surfaces = []
        for i in range(pieces):
            x = random.randint(0, size[0] - needed_size[0])
            y = random.randint(0, size[1] - needed_size[1])
            new_surf = s.subsurface(x, y, needed_size[0], needed_size[1])
            angle = np.arctan2(self.center[1] - y, self.center[0] - x)
            rrange = (abs(self.center[0] - x), abs(self.center[1] - y))
            angle = (np.cos(angle * rrange[0]), math.sin(angle * rrange[1]))
            self.mini_surfaces.append(
                [[self.center[0] - x, self.center[1] - y], new_surf, angle, 0]
            )
            # 											0						1		 2		 3

    def logic(self):
        self.life()
        self.change_frame -= 1
        for surface in self.mini_surfaces:
            surface[0] = [surface[0][0] + surface[2][0], surface[0][1] + surface[2][1]]
            if self.change_frame == 0:
                size = surface[1].get_size()
                new_size = int(size[0] - size[0] * 0.05), int(size[1] - size[1] * 0.05)
                if sum(new_size) < 2:
                    self.mini_surfaces.remove(surface)
                else:
                    surface[3] += 5
                    surface[1] = pygame.transform.rotate(surface[1], surface[3])
                    surface[1] = pygame.transform.scale(surface[1], (new_size))
        if self.change_frame <= 0:
            self.change_frame = self.speed

    def draw(self, window):
        for surf in self.mini_surfaces:
            window.blit(surf[1], surf[0])


class TrailParticle(Particle):
    @lru_cache(maxsize=2000, typed=True)
    def __init__(
        self,
        position=(0, 0),
        offset=(0, 0),
        radian=1,
        speed=1,
        lifetime=300,
        transparent=False,
        alpha=255,
        random_rotation=False,
        center_position=False,
        surface=None,
    ):
        super().__init__(position, lifetime, surface)
        self.speed = 1
        self.lifetime = lifetime
        self.surface = surface
        pos = [*position]
        if center_position:
            size = surface.get_size()
            pos[0] -= size[0] // 2
            pos[1] -= size[1] // 2
        self.alpha = [transparent, alpha]
        self.alpha_speed = int(1 / lifetime * alpha)
        if random_rotation:
            self.surface = pygame.transform.rotate(self.surface, random.randint(0, 360))
        self.position = [
            pos[0] + random.gauss(-offset[0], offset[0]),
            pos[1] + random.gauss(-offset[1], offset[1]),
        ]
        self.angle = (np.cos(radian) * speed, np.sin(radian) * speed)

    def logic(self):
        self.life()
        if self.alpha[0]:
            self.alpha[1] -= self.alpha_speed
        self.surface.set_alpha(self.alpha[1])
        self.position[0] += self.angle[0]
        self.position[1] += self.angle[1]

    def draw(self, window):
        window.blit(self.surface, self.position)


class SimpleParticle(Particle):
    @lru_cache(maxsize=2000, typed=True)
    def __init__(
        self,
        position=(0, 0),
        offset=(0, 0),
        lifetime=300,
        color=(255, 255, 255),
        size=50,
        bold=0,
        dark_over_time=0,
        change_size_over_time=0,
    ):
        super().__init__(position, lifetime, None)
        self.lifetime = lifetime
        self.color = color
        self.size = size
        self.bold = bold
        self.dark = dark_over_time
        self.small = change_size_over_time
        pos = [*position]
        self.position = (
            pos[0] + random.randint(-offset[0], offset[0]),
            pos[1] + random.randint(-offset[1], offset[1]),
        )

    def logic(self):
        self.life()
        if self.dark:
            self.color = tuple([max(i + self.dark, 0) for i in self.color])
        if self.small:
            self.size = self.size + self.small if self.size + self.small > 1 else 1

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.position, self.size, self.bold)
