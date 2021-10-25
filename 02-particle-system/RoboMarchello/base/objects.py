"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
your particle system, without needing to implement a game that
goes with it too.
Feel free to modify everything in this file to your liking.
"""

import time,random
from collections import deque
from colorsys import hsv_to_rgb
from functools import lru_cache
from operator import attrgetter
from random import gauss, choices, uniform

import pygame
import math
import random as rd

# noinspection PyPackages
from .utils import *


class State:
    def __init__(self, *initial_objects: "Object"):
        self.objects = set()
        self.objects_to_add = set()

        for obj in initial_objects:
            self.add(obj)

    def add(self, obj: "Object"):
        # We don't add objects immediately,
        # as it could invalidate iterations.
        self.objects_to_add.add(obj)
        obj.state = self
        return obj

    def logic(self):
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

    def collide(self, other: "Object") -> bool:
        """Whether two objects collide."""
        # The distance must be modified because everything wraps
        dx = (self.center.x - other.center.x) % SIZE[0]
        dx = min(dx, SIZE[0] - dx)
        dy = (self.center.y - other.center.y) % SIZE[1]
        dy = min(dy, SIZE[1] - dy)
        return (dx ** 2 + dy ** 2) <= (self.radius + other.radius) ** 2

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

def drawPoints(points,pos,addAngle):
    Points = []

    for point in points:
        pointAngle = point[0]-addAngle
        cosi = math.cos(pointAngle)
        sinu = math.sin(pointAngle)

        Points.append([int(-cosi*point[1]+pos[0]),int(sinu*point[1]+pos[1])])
        
    return Points

class explodeParticle():
    def __init__(self,pos):
        self.pos = pos

        self.life_time = 60

        self.points = [[0.4048917862850834, 137], [0.024686342055599386, 81], [-0.4007934485752347, 128], [-0.5382217016114783, 78], [-0.8496871288406961, 165], [-1.2832204960144495, 74], [-1.546410917622178, 123], [-1.9295669970654687, 68], [-2.2061120795182037, 146], [-2.402033916073462, 77], [-2.7136441572683108, 125], [-3.4507915659168678, 75], [-3.737377201212852, 142], [-4.267969770483591, 69], [1.151145464659793, 142], [1.0960994437147216, 80]]
        self.color = [75,75,75]

        self.rotateDir = rd.randint(-1,1)*5

        self.angle = 0

    def draw(self,screen):
        for point in self.points:
            if point[1] < 2 and point[1] > -2:
                point[1] = 0
            else:
                point[1] -= 3

        self.life_time -= 1
            
        pygame.draw.polygon(screen,self.color,drawPoints(self.points,self.pos,math.radians(self.angle)))

class ExplodeMan():
    def __init__(self):
        self.particles = []

    def draw(self,screen):
        for part in self.particles:
            part.draw(screen)

            if part.life_time < 0:
                self.particles.pop(self.particles.index(part))
Expm = ExplodeMan()

class FireParticle():
    def __init__(self,pos,angle):
        self.angle = 0
        self.moveAngle = angle
        self.moveSpeed = math.sin(math.radians(self.moveAngle))*2

        self.pos = pos

        self.life_time = 70

        self.points = rd.choice([[[-0.6162969373, 13], [-1.570796326794, 26], [-3.2891607249, 29], [-4.22894197881, 45], [-4.6919836496, 4], [0.94200004037, 23], [0.041642579, 27]],
                                 [[-0.44441920990109884, 28], [-1.4019644247837757, 24], [-2.782821983319221, 20], [-3.6682199250235437, 4], [-3.9926856185397064, 12], [1.433730152484709, 12], [0.6828183109791537, 21], [0.1891990220999682, 15]],
                                 [[-0.48296887585656134, 27], [-0.9173699856141346, 15], [-1.6313283465770037, 8], [-2.8523216479806512, 22], [-3.564446579722734, 22], [-3.9269908169872414, 41], [1.5707963267948966, 12], [0.8431849941683862, 20]],
                                 [[-0.26211984126547283, 19], [-1.4876550949064553, 13], [-2.1086318534883253, 21], [-3.036103345064703, 20], [1.0074800653029286, 22]]])
        self.color = [255,255,0]
        self.EndColor = [255,0,0]
        self.addRGB = []
    
        for color in range(3):
            self.addRGB.append((self.color[color]-self.EndColor[color])//255*1.5)

        self.rotateDir = rd.randint(-1,1)*5
        self.moveDir = [math.cos(self.moveAngle)*2,math.sin(self.moveAngle)*2]

    def draw(self,screen):
        self.pos[0] += self.moveDir[0]
        self.pos[1] += self.moveDir[1]
        self.angle += self.rotateDir#rotation

        self.life_time -= 1

        #changing color
        for color in range(3):
            if self.color[color] < self.EndColor[color]:
                if self.color[color] < self.EndColor[color]:
                    self.color[color] += self.addRGB[color]
            else:
                if self.color[color] > self.EndColor[color]:
                    self.color[color] -= self.addRGB[color]
        self.color = list(map(int, self.color))

        for point in self.points:
            if point[1] != 0:
                point[1] -= 0.5
            
        pygame.draw.polygon(screen,self.color,drawPoints(self.points,self.pos,math.radians(self.angle)))

class ShootParticle():
    def __init__(self,pos,angle):
        self.pos = pos
        self.angle = angle

        self.moveDir = [math.cos(angle),math.sin(angle)]
        self.life_time = 60

        self.radius = 5
    def draw(self,screen):
        pygame.draw.circle(screen,(255,0,0),self.pos,self.radius)

        self.pos[0] += self.moveDir[0]
        self.pos[1] += self.moveDir[1]

        self.radius -= 0.1

        self.life_time -= 1

class Player(Object):
    Z = 10
    HIT_BOX_SCALE = 0.7  # harder to touch the player
    ACCELERATION = 0.7
    FRICTION = 0.9
    ROTATION_ACCELERATION = 3
    INITIAL_ROTATION = 90
    FIRE_COOLDOWN = 15  # frames

    def __init__(self, pos, vel):
        super().__init__(pos, vel, load_image("player", 3))

        self.speed = 0
        self.fire_cooldown = -1

        self.thousand_test = False
        
        self.RadRot = -math.radians(self.rotation-90)
        self.particles = []
        

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.fire()

                #132 ADD PARTICLE HERE
                
            if event.key == pygame.K_t:
                if self.thousand_test == False:
                    self.thousand_test = True
                else:
                    self.thousand_test = False

    def logic(self):
        self.fire_cooldown -= 1

        # For continuous shooting:
        # if pressed[pygame.K_SPACE]:
        #     self.fire(new_objects)

        # Motion
        pressed = pygame.key.get_pressed()
        rotation_acc = pressed[pygame.K_LEFT] - pressed[pygame.K_RIGHT]
        raw_acceleration = 0.5 * pressed[pygame.K_DOWN] - pressed[pygame.K_UP]
        if raw_acceleration < 0:
            self.bottomPos = [self.rect.center[0]+math.cos(self.RadRot)*(self.rect.width//2),self.rect.center[1]+math.sin(self.RadRot)*(self.rect.height//2)]
            if len(self.particles) < 1000:
                self.RadRot = -math.radians(self.rotation-90)
                if self.thousand_test == False:
                    self.particles.append(FireParticle(self.bottomPos,self.RadRot))
                else:
                    for part in range(25):
                        self.particles.append(FireParticle(self.bottomPos,self.RadRot))
        
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
        bullet = Bullet(self.center, 270 - self.rotation)
        self.state.add(bullet)
        
        
        self.frontPos = [self.rect.center[0]+math.cos(math.radians(270 - self.rotation))*(self.rect.width//2),self.rect.center[1]+math.sin(math.radians(270 - self.rotation))*(self.rect.height//2)]
        
        # You can add particles here too.
        for part in range(10):
            addDir = rd.randint(-45,45)
            self.frontPos = [self.rect.center[0]+math.cos(math.radians(270 - self.rotation+addDir))*(self.rect.width//2),self.rect.center[1]+math.sin(math.radians(270 - self.rotation+addDir))*(self.rect.height//2)]
        
            self.particles.append(ShootParticle(self.frontPos, math.radians(270 - self.rotation+addDir)))

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


class Asteroid(Object):
    AVG_SPEED = 1
    EXPLOSION_SPEED_BOOST = 1.8

    def __init__(self, pos, vel, size=4, color=None, points=None):
        assert 1 <= size <= 4
        self.level = size
        # We copy to change the color
        self.color = color or self.random_color()

        self.points = points


        super().__init__(pos, vel, self.colored_image(size, self.color,self.points))

    @staticmethod
    def colored_image(size, color, points):
        sprite = load_image(f"asteroid-{16*2**size}").copy()
        sprite.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        sprite.set_colorkey((0,0,0))

        if points != None:
            pygame.draw.polygon(sprite,(0,0,0,0),points)
          
        return sprite

    def logic(self):
        super().logic()

        for obj in self.state.objects:
            if not obj.alive:
                continue

            if isinstance(obj, Bullet):
                # Detect if the bullet and asteroid collide.
                if self.collide(obj):
                    self.explode(obj)
                    break
            elif isinstance(obj, Player):
                if self.collide(obj):
                    obj.on_asteroid_collision(self)

    def explode(self, bullet):
        bullet.alive = False
        self.alive = False

        
        if self.level > 1:
            # We spawn two smaller asteroids in the direction perpendicular to the collision.
            perp_velocity = pygame.Vector2(bullet.vel.y, -bullet.vel.x)
            perp_velocity.scale_to_length(self.vel.length() * self.EXPLOSION_SPEED_BOOST)

            size = 16*2**(self.level-1)
            rect_points = [[0,0],[size,0],[size,size],[0,size]]
            intersectPoint = [rd.randint(0+size//3,size-size//3),rd.randint(0+size//3,size-size//3)]
            
            for mult in (-1, 1):
                points = [rect_points[0],rect_points[1*mult],rect_points[2*mult],intersectPoint]
                self.state.add(

                    Asteroid(self.center, perp_velocity * mult, self.level - 1, self.color,points)
                    
                )

        # You'll add particles here for sure ;)
        Expm.particles.append(explodeParticle([self.center[0],self.center[1]]))

    def random_color(self):
        r, g, b = hsv_to_rgb(uniform(0, 1), 0.8, 0.8)
        return int(r * 255), int(g * 255), int(b * 255)

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
        self.cap_fps = True
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
        self.clock.tick(self.target_fps * self.cap_fps)

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
        screen.blit(t, self.center)

class ParticleCounter(Object):
    def __init__(self,*args):
        self.color = "#89C4F4"

        self.args = args

        self.particleCount = 0

        dummy_surface = pygame.Surface((1, 1))
        super().__init__((4, 8), (0, 0), dummy_surface)

    def particle_count(self,*args):
        self.particleCount = 0
        
        for arg in args[0]:
            self.particleCount += len(arg)
        return self.particleCount
    def draw(self,screen):
        color = "#89C4F4"
        t = text(f"PARTICLES: {self.particle_count(self.args)}", color)
        screen.blit(t, (5,25))
