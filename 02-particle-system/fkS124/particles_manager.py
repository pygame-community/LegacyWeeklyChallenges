from math import log2
from types import NoneType
import pygame as pg
from pygame.locals import *
from random import randint, choice
from copy import copy
from .utils import load_image

class ParticleManager:

    def __init__(self, player_instance):

        self.screen = None

        self.particles = []

        self.smoke_generator = SmokeGenerator(self)
        self.explosion_generator = ExplosionGenerator(self)
        self.mini_explosion_generator = MiniExplosionGenerator(self)
        self.player = player_instance

        self.last_pl_pos = copy(self.player.rect.center) 

        self.waited = False

        """asteroid = pg.image.load(r"../assets/asteroid-32.png").convert_alpha()
        asteroid = pg.transform.scale(asteroid, (asteroid.get_width()*5, asteroid.get_height()*5))
        surfs = split_asteroid(asteroid)
        
        for i in surfs:
            self.particles.append(AsteroidParticle((500, 500), i[0], i[1]))"""

    def start_mini_explosion(self, pos):
        self.mini_explosion_generator.generate(pos, 200, 750, 0.2)

    def manage_smoke(self):
        if self.player.rect.center != self.last_pl_pos:
            self.smoke_generator.generate(self.player.rect.center, 5, 10, (12,12))
            self.last_pl_pos = copy(self.player.rect.center)

    def start_explosion(self, pos):
        self.explosion_generator.generate(pos, 1000, 1500, 0.6)

    def add_particle(self, particle):
        self.particles.append(particle)

    def update(self,
               screen:pg.Surface):


        self.screen = screen
        self.manage_smoke()

        if pg.time.get_ticks() > 1000:
            for particle in self.particles:
                kill = particle.update(self.screen)
                if kill == "kill":
                    self.particles.remove(particle)


class Particle:

    def __init__(self, 
                 dep_pos: tuple[int, int],
                 size: tuple[int, int],
                 color: tuple[int, int, int],
                 life_time: int,
                 shape: str,
                 moving:bool=False,
                 velocity:pg.Vector2 | NoneType=None,
                 alpha:int=255
                 ):
        
        self.appearance_time = pg.time.get_ticks()
        self.dep_pos = dep_pos
        self.size = size
        self.color = color
        self.life_time = life_time
        self.shape = shape
        self.moving = moving
        self.velocity = velocity
        self.alpha = alpha

        """if self.moving:
            if type(self.velocity) is not pg.Vector2:
                raise ValueError("Velocity must be a pygame.Vector2 object")"""
                
        self.image = pg.Surface(self.size)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.dep_pos)

        match self.shape:
            case "rect":
                self.image.fill(self.color)
            case "circle":
                self.image = pg.Surface(self.size, SRCALPHA)
                pg.draw.circle(self.image, self.color, (min(self.size)//2, min(self.size)//2), min(self.size)//2)
            
    def behavior(self):

        if self.moving:
            self.rect.center += self.velocity

    def update(self, screen):
        self.behavior()
        screen.blit(self.image, self.rect)

        if pg.time.get_ticks() - self.appearance_time > self.life_time:
            return "kill"


class SmokeParticle(Particle):

    def __init__(self,
                 pos:pg.Vector2,
                 radius:int,
                 color:tuple[int,int,int]):

        super().__init__(
            pos, radius, color, 2500, "circle" 
        )

    def behavior(self):
        super().behavior()
        self.size -= pg.Vector2(0.5, 0.5)
        if min(self.size) < 0:
            self.life_time = 0
            return

        self.image = pg.Surface(self.size, SRCALPHA)
        pg.draw.circle(self.image, self.color, (min(self.size)//2, min(self.size)//2), min(self.size)//2)


class SmokeGenerator:

    def __init__(self, particle_manager_instance: ParticleManager):
        self.particle_manager = particle_manager_instance

        self.colors = [
            (248,222,126),
            (250,218,94),
            (249,166,2),
            (255, 211, 0), 
            (252, 209, 42)
        ]

    def rd_coo(self, range_):
        return (randint(0, range_), randint(0, range_))

    def generate(self, pos, iterations, range_, size):
        if type(pos) is tuple:
            pos = pg.Vector2(pos)

        for i in range(iterations):
            new_pos = pos + pg.Vector2(self.rd_coo(range_))

            self.particle_manager.add_particle(SmokeParticle(new_pos, size, choice(self.colors)))


class ExplosiveParticle(Particle):

    def __init__(self, pos, vel, color, size, life_time):

        super().__init__(pos, size, color, life_time, "circle", moving=True, velocity=vel)
        vel_x, vel_y = self.velocity[0], self.velocity[1]
        self.d = pg.Vector2(0.005*-vel_x, 0.005*-vel_y)
        self.alpha_d = 255 / life_time * 2

    def behavior(self):
        self.image.set_alpha(self.image.get_alpha()-self.alpha_d)
        self.velocity += self.d
        return super().behavior()   


class ExplosionGenerator:

    def __init__(self, particle_manager_instance: ParticleManager):
        self.particle_manager = particle_manager_instance

        self.colors = [
            (99,166,159),
            (242,225,172),
            (242,131,107),
            (242,89,75),
            (205,44,36),

        ]

    def generate(self, pos, iterations, lf_t, coeficient):

        if type(pos) is tuple:
            pos = pg.Vector2(pos)

        sizes = [(i, i) for i in range(0, 25)]
        angles = range(0, 360)

        for i in range(iterations):
            vel = pg.Vector2(choice(range(1, 5)), choice(range(1, 5)))
            if randint(0, 100) > coeficient*100:
                ch = randint(-40, 40)
                ch += 1 if not ch else 0
                self.particle_manager.add_particle(ExplosiveParticle(pos, vel.rotate(choice(angles)), choice(self.colors), choice(sizes), lf_t))


# can handle only <4000 width
log2_points = [log2(i * 0.01 + 1) for i in range(4000)]

def split_asteroid(surf:pg.Surface):

    w, h = surf.get_size()
    surfaces = [pg.Surface(surf.get_size(), SRCALPHA) for _ in range(4)]
    for s in surfaces:
        s.blit(surf, (0, 0))

    direction = [
        ("down", "left"),  # top right
        ("down", "right"),  # top left
        ("up", "left"),  # down right
        ("up", "right")  # down left
    ]
    vel = pg.Vector2(1, 1)
    vectors = [
        pg.Vector2(0, -1),
        pg.Vector2(-1, 0),
        pg.Vector2(1, 0),
        pg.Vector2(0, 1)
    ]
    for index, surf_ in enumerate(surfaces):
        for dir_ in direction[index]:
            draw_log2(surf_, dir_)

    return [(surfaces[i], vectors[i]) for i in range(4)]


def draw_log2(surf:pg.Surface, direction:str) -> None:

    w,h = surf.get_size()
    k_side = w//log2_points[h]
    k_upside = h//log2_points[w]
    surf.set_colorkey((0, 0, 0))
    color = (0, 0, 0)

    match direction:

        case "up":
            pg.draw.polygon(
                surf,
                color,
                [
                    (0, 0),
                    (0, h),
                    *[(i, h-(log2_points[i]*k_upside)) for i in range(w)],
                    (w, 0),
                    (0, 0)
                ]
            )
        case "down":
            pg.draw.polygon(
                surf,
                color,
                [
                    (0, h),
                    *[(i, h-(log2_points[i]*k_upside)) for i in range(w)],
                    (w, h),
                    (0, h)
                ]
            )
        case "left":
            pg.draw.polygon(
                surf,
                color,
                [
                    (0, 0),
                    *[(log2_points[i]*k_side, i) for i in range(h)],
                    (0, h),
                    (0, 0)
                ]
            )
        case "right":
            pg.draw.polygon(
                surf,
                color,
                [
                    (w, 0),
                    (0, 0),
                    *[(log2_points[i]*k_side, i) for i in range(h)],
                    (w, h),
                    (w, 0)
                ]
            )


class AsteroidParticle(Particle):

    def __init__(self, pos, surf:pg.Surface, vector:pg.Vector2):

        super().__init__(pos, size=(surf.get_size()), color=(0, 0, 0), life_time=15000, shape="circle", moving=True)
        self.image = surf
        self.velocity=vector


class MiniExplosionGenerator:

    def __init__(self, particle_manager_instance: ParticleManager):
        self.particle_manager = particle_manager_instance

        self.colors = [
          
            (252, 108, 76),
            (244, 132, 148),
            (30, 70, 132),
            (84, 108, 156),
            (170, 184, 207),
            (64, 96, 148),

        ]

        """
        (51, 22, 15),
            (178, 34, 34),
            (255, 122, 0),
            (241, 198, 9),
            (255, 243, 71),
            (253, 255, 165),"""

    def generate(self, pos, iterations, lf_t, coeficient):

        if type(pos) is tuple:
            pos = pg.Vector2(pos)

        sizes = [(i, i) for i in range(0, 25)]
        angles = range(0, 360)

        for i in range(iterations):
            vel = pg.Vector2(choice(range(1, 3)), choice(range(1, 3)))
            if randint(0, 100) > coeficient*100:
                ch = randint(-40, 40)
                ch += 1 if not ch else 0
                self.particle_manager.add_particle(ExplosiveParticle(pos, vel.rotate(choice(angles)), choice(self.colors), choice(sizes), lf_t))
