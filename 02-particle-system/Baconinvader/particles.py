from .objects import *

import numpy as np
from pygame.gfxdraw import filled_circle
import pygame as p

from random import random
from math import cos, sin


class Particles(Object):
    def __init__(
        self,
        pos,
        vel,
        angle,
        spread,
        speed,
        speed_variance,
        max_particles,
        particles_size,
        size_variance,
        particles_lifetime,
        colour,
        colour_variance,
        size_change,
    ):

        Object.__init__(self, pos, vel, p.Surface((1, 1)))

        self.angle = angle
        self.spread = spread
        self.speed = speed
        self.speed_variance = speed_variance

        self.max_particles = max_particles
        self.particles_lifetime = particles_lifetime
        self.particles_size = particles_size
        self.size_variance = size_variance

        self.colour = list(colour)
        self.colour_variance = colour_variance
        self.size_change = size_change
        self.vel_keep = 0.9999

        # if the particles shrink, then see if we can see them off early
        if self.size_change < 0:
            max_calculated_lifetime = int(
                (self.particles_size + self.size_change) / -self.size_change
            )
            if max_calculated_lifetime < self.particles_lifetime:
                self.particles_lifetime = max_calculated_lifetime

        self.particles = np.empty([self.max_particles, 2])
        self.particles_v = np.empty([self.max_particles, 2])
        self.particles_r = np.full(self.max_particles, self.particles_size, dtype="float64")
        self.particles_timer = np.full(self.max_particles, self.particles_lifetime)
        self.particles_colour = np.empty([self.max_particles, 3])

        self.free_particles = [_ for _ in range(self.max_particles)]

        for _ in range(self.max_particles):
            self.add_particle()

    def add_particle(self):
        # add particles to free space
        if self.free_particles:
            free_index = self.free_particles[0]

            self.particles[free_index, 0] = self.center.x
            self.particles[free_index, 1] = self.center.y

            angle = self.angle + ((random() - 0.5) * self.spread)
            speed = self.speed + ((random() - 0.5) * self.speed_variance)

            self.particles_v[free_index, 0] = cos(angle) * speed
            self.particles_v[free_index, 1] = sin(angle) * speed

            self.particles_r[free_index] = self.particles_size + (
                (random() - 0.5) * self.size_variance
            )

            self.particles_timer[free_index] = self.particles_lifetime

            colour = self.colour[:]

            colour[0] = max(min(colour[0] + ((random() - 0.5) * self.colour_variance[0]), 255), 0)
            colour[1] = max(min(colour[1] + ((random() - 0.5) * self.colour_variance[1]), 255), 0)
            colour[2] = max(min(colour[2] + ((random() - 0.5) * self.colour_variance[2]), 255), 0)

            self.particles_colour[free_index] = colour

            del self.free_particles[0]

    def logic(self, **kwargs):
        Object.logic(self, **kwargs)

        self.particles += self.particles_v
        self.particles_v *= self.vel_keep
        self.particles_timer -= 1

        self.particles_r += self.size_change

    def draw(self, screen):
        drawn_particles = 0

        for i in range(self.max_particles):
            if self.particles_timer[i] > 0:
                drawn_particles += 1

                filled_circle(
                    screen,
                    int(self.particles[i, 0]),
                    int(self.particles[i, 1]),
                    max(int(self.particles_r[i]), 0),
                    (
                        int(self.particles_colour[i, 0]),
                        int(self.particles_colour[i, 1]),
                        int(self.particles_colour[i, 2]),
                    ),
                )

            elif self.particles_r[i] >= 0:
                self.particles_r[i] = -1
                self.free_particles.append(i)

        if not drawn_particles:
            self.alive = False
