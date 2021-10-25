# particles.py
#
# particle system
# by AnDenixa, Fall 2021

# from collections import deque
from functools import lru_cache
from random import Random, choice, randint, random, shuffle

import pygame
from pygame import Color, Surface, Vector2
from pygame.draw import circle

from .objects import *


__all__ = ["Spawner", "InterpolatedColors", "Particles", "SimpleParticle", "Shardling", "SnowFlake"]


def InterpolatedColors(a_list, n_values):
    steps = n_values//len(a_list)
    res = []    
    for n in range(0,len(a_list),2):
        col1 = Color(a_list[n])
        col2 = Color(a_list[n+1])
        for step_no in range(steps):
            res.append(col1.lerp(col2, step_no/steps))
    return res


class Spawner:
    """ Particle spawner produces a specified number of particles
        every second
    """
    def __init__(self, rate_s, spawn_pos, spawn_vel, lifetime_ms, p_type, spawn_cb, **kwargs):
        self.rate = rate_s        
        self._kwargs = kwargs
        self.pos = pygame.Vector2(spawn_pos) 
        self.vel = pygame.Vector2(spawn_vel)
        self.p_lifetime_ms = lifetime_ms
        self.p_type = p_type    
        self._spawn_cb = spawn_cb
        self._particle_man = None
        self._to_spawn = 0

    @property
    def rate(self):
        return self._rate_s

    @rate.setter
    def rate(self, rate_s):
        self._rate_s = rate_s
        self._rate_ms = rate_s/1000

    def spawn(self, **kwargs):
        passed_ms = self._particle_man._get_passed()        
        self._to_spawn += self._rate_ms * passed_ms
        if (how_many:=int(self._to_spawn)):
            self._to_spawn -= how_many            
            self._particle_man.spawnMany(how_many, self.pos, self.vel, self.p_lifetime_ms, self.p_type, spawn_cb=self._spawn_cb, **self._kwargs, **kwargs)        

class Particles():
    """ a particle manager """
    TYPE_SIMPLE, TYPE_BUBBLE, TYPE_SNOWFLAKE, TYPE_SPRITE = range(4)
    def __init__(self, clock, target_fps):        
        self.clock = clock
        self.target_fps=target_fps
        self._time_quota = 1000 // target_fps
        self._get_passed = clock.get_time
        self._particles = []
        self._particles_to_add = []
        self._screen_size = pygame.display.get_window_size()        
        self._spawners = []
        self._update_iter = self._make_update_iter(2)

    def addCollision(self, obj):
        pass

    def spawn(self, spawn_pos, spawn_vel, lifetime_ms, p_type, **kwargs):
        if p_type==Particles.TYPE_SIMPLE:
            P = SimpleParticle
        elif p_type==Particles.TYPE_SNOWFLAKE:
            P = SnowFlake
        elif p_type==Particles.TYPE_SPRITE:
            P = Shardling
        p = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
        self._particles_to_add.append( p )      

    def spawnMany(self, how_many, spawn_pos, spawn_vel, lifetime_ms, p_type, spawn_cb=None, **kwargs):
        particles_to_add = self._particles_to_add
        rnd = random
        if p_type==Particles.TYPE_SIMPLE:
            P = SimpleParticle
        elif p_type==Particles.TYPE_SNOWFLAKE:
            P = SnowFlake
        elif p_type==Particles.TYPE_SPRITE:
            P = Shardling

        lots = how_many//5
        little = how_many%5

        if spawn_cb is None:            
            for n in range(lots):
                p1 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p2 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p3 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p4 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p5 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                particles_to_add.extend((p1,p2,p3,p4,p5))
        else:
            for n in range(lots):
                p1 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p2 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p3 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p4 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                p5 = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
                spawn_cb(p1); spawn_cb(p2); spawn_cb(p3); spawn_cb(p4);spawn_cb(p5)
                particles_to_add.extend((p1,p2,p3,p4,p5))

        for n in range(little):
            pos = Vector2(spawn_pos); vel = Vector2(spawn_vel)
            p = P(Vector2(spawn_pos), Vector2(spawn_vel), life=lifetime_ms, **kwargs)
            if spawn_cb is not None: spawn_cb(p)
            particles_to_add.append(p)                

    def addSpawner(self, rate_s, spawn_pos, spawn_vel, lifetime_ms, p_type, spawn_cb=None, **kwargs):
        spawner = Spawner(rate_s, spawn_pos, spawn_vel, lifetime_ms, p_type, spawn_cb=spawn_cb, **kwargs)        
        self._spawners.append(spawner)
        spawner._particle_man = self
        return spawner

    def draw(self, surf):
        surf.blits([(p.image, p.pos, None, 0) for p in self._particles], doreturn=0)      
        
    def _make_update_iter(self, batch_count):
        """ Chunked particle updater """
        get_passed = self._get_passed
        sceen_w, sceen_h = self._screen_size
        _particles = self._particles
        _particles_to_add = self._particles_to_add
        _particles_new = []
        batch_no = 0        
        while True:
            for spawner in self._spawners:
                spawner.spawn()
            if not batch_no:
                _particles[:] = _particles_new
                _particles_new = []
                bacth_size = len(_particles)//batch_count
            passed_ms = get_passed()
            _particles_new.extend([p.update(passed_ms) for p in _particles[batch_no*bacth_size:(batch_no+1)*bacth_size] if p.life>0])
            if _particles_to_add:            
                _particles_new.extend([p.update(passed_ms) for p in _particles_to_add])                
                _particles_to_add[:] = []            
            yield
            batch_no = (batch_no+1)%batch_count
            if not batch_no:
                _particles[:] = _particles_new
                _particles_new = []
                bacth_size = len(_particles)//batch_count
            passed_ms = get_passed()
            _particles_new.extend([p.update(passed_ms) for p in _particles[batch_no*bacth_size:(batch_no+1)*bacth_size] if (sceen_w>p.pos.x>0)])
            if _particles_to_add:            
                _particles_new.extend([p.update(passed_ms) for p in _particles_to_add if (sceen_w>p.pos.x>0)])                
                _particles_to_add[:] = []            
            yield
            batch_no = (batch_no+1)%batch_count
            if not batch_no:
                _particles[:] = _particles_new
                _particles_new = []
                bacth_size = len(_particles)//batch_count
            passed_ms = get_passed()
            _particles_new.extend([p.update(passed_ms) for p in _particles[batch_no*bacth_size:(batch_no+1)*bacth_size] if (sceen_h>p.pos.y>0)])
            if _particles_to_add:            
                _particles_new.extend([p.update(passed_ms) for p in _particles_to_add if (sceen_h>p.pos.y>0)])                
                _particles_to_add[:] = []            
            yield        
            batch_no = (batch_no+1)%batch_count
            
    def update(self):              
        next(self._update_iter)

    def count(self):
        return len(self._particles)+len(self._particles_to_add)        

class Particle:
    __slots__ = "pos", "speed", "image", "life"
    _randoms = Random(0), Random(1), Random(2), Random(3)
    _rnd = random
    @staticmethod
    @lru_cache(maxsize=None,typed=True)
    def _make_circle(color, size):
        size2, size2m = divmod(size, 2)
        circle_im = Surface((size, size))
        circle_im.set_colorkey((0,0,0))
        circle(circle_im, color, (size2, size2), size2+size2m)
        return circle_im

    @classmethod
    @lru_cache(maxsize=None,typed=False)
    def _make_snowflake(cls, rotation, seed):
        snowlake_img = pygame.Surface((32,32))
        snowlake_img.set_colorkey((0,0,0))
        center = (16,16)
        white = (255,255,255)            
        angles = list(range(0,360,45))
        cls._randoms[seed].shuffle(angles)
        stalk = Vector2(12)   
        rotum_m = Vector2(8)      
        for angle in angles:
            stalk.rotate_ip(angle) # rotate_ip broke snowflake
            pygame.draw.line(snowlake_img, white, stalk+center, center,width=2)
            rotum_m.rotate_ip(angle) # rotate_ip broke snowflake, but I like it better
            rotum_m_br = Vector2(4).rotate(angle+45)
            rotum_m_br2 = Vector2(4).rotate(angle-45)
            pygame.draw.line(snowlake_img, white, rotum_m+center, rotum_m+center+rotum_m_br, width=2)
            pygame.draw.line(snowlake_img, white, rotum_m+center, rotum_m+center+rotum_m_br2, width=2)
            snowlake_img.fill((15,15,15), special_flags=pygame.BLEND_SUB)         
        if rotation:
            snowlake_img = pygame.transform.rotate(snowlake_img, rotation)
        snowlake_img = pygame.transform.scale(snowlake_img, (16,16))
        return snowlake_img

    def __init__(self, pos, speed, life):
        self.life = life
        self.pos = pos
        self.speed = speed

    def draw(self, surf):
        surf.blit(self.image, self.pos)      

class SimpleParticle(Particle):    
    __slots__ = "_cycle_colors", '_last_cbin', '_color_bin_sz', 'size'
    _colors = list(set([(int(200+random()*55) & ~3, int(170+random()*10) & ~3, int(86+random()*12) & ~3) for i in range(100)]))
    def __init__(self, pos, speed, life, **kwargs):
        self.size = int(random()*3) + 3
        super().__init__(pos, speed, life)
        if (color := kwargs.get("color", None)) is None:
            color = self._colors[int(self._rnd()*len(self._colors))]
        if isinstance(color[0], (tuple, pygame.Color)):
            self.image = self._make_circle(tuple(color[0]), self.size)
            self._cycle_colors = list( reversed( color ) )
        else:
            self.image = self._make_circle(color, self.size)
            self._cycle_colors = False

    def update(self, passed):
        self.pos += self.speed * (passed/180)        

        if self._cycle_colors:
            try:
                _color_bin_sz = self._color_bin_sz    
                _last_cbin = self.life//_color_bin_sz            
            except AttributeError:
                _color_bin_sz = self.life//len(self._cycle_colors)
                self._color_bin_sz = _color_bin_sz
                self.life -= (self.life%len(self._cycle_colors))+1
                self._last_cbin = _last_cbin = self.life//_color_bin_sz
            if self._last_cbin!=_last_cbin and self.life>=0:
                color = self._cycle_colors[_last_cbin]
                self.image = self._make_circle(tuple(color), self.size)
                self._last_cbin = _last_cbin
        self.life -= passed
        return self        

class Shardling(Particle):
    """ a rotated particle with a predefined sprite image """
    __slots__ = "image", 'angle', 'torque', 'color', 'surf', '_fade'
    def __init__(self, pos, speed, life, surf, color, torque):
        super().__init__(pos, speed, life)
        self.surf = surf.convert_alpha()
        self.torque = torque
        self.angle = 0

    def update(self, passed):
        self.pos += self.speed * (delta:=passed/180)        
        self.angle = (angle:=(self.angle +(self.torque*delta)) % 360)
        self.life -= passed
        self.image = pygame.transform.rotate(self.surf, self.angle)        
        if self.life<256:
            self.image.set_alpha(self.life)

        return self        

    def draw(self, surf):
        surf.blit(self.image, self.pos)

class SnowFlake(Particle):
    """ a rotated particle shaped like a snowflake 
    """
    __slots__ = "torque", "angle", "_seed", "color", "_fade", "_cycle_colors", "_color_bin_sz", "_last_angle", "_last_cbin"
   
    _cls_seed = 0    
    _colors = list(set([((100+int(random()*50)) & ~3, (150+int(random()*10)) & ~3, (200+int(random()*55)) & ~3) for i in range(50)]))

    def __init__(self, pos, speed, life, torque=0, **kwargs):        
        self.life = life
        self.pos = pos
        self.speed = speed        
        self._seed = int(self._rnd()*4)
        if (color := kwargs.get("color", None)) is None:
            color = self._colors[int(self._rnd()*len(self._colors))]        
        if not isinstance(color[0], (tuple, list)):      
            self.image=self._make_snowflake(0, self._seed)
            self._cycle_colors = False                                    
        else:
            self._cycle_colors = tuple(reversed(color))
            self.image=self._make_snowflake(0, self._seed)
        size_w2 = self.image.get_height() // 2
        self.pos -= size_w2, size_w2
        self.torque = torque
        self.angle = self._fade = 0
        self._last_angle = None
        self.color = color
    
    def update(self, passed):        
        self.pos += self.speed * (delta:=passed/180)        
        self.angle = (angle:=(self.angle +(self.torque*delta)) % 360)
        angle = int(angle) & ~3
        if self._last_angle!=angle:
            self.image = self._make_snowflake(angle, self._seed).copy()
            self._last_angle = angle                    
        if self._cycle_colors:
            try:
                _color_bin_sz = self._color_bin_sz    
                _last_cbin = self.life//_color_bin_sz            
            except AttributeError:
                _color_bin_sz = self.life//len(self._cycle_colors)                
                self._color_bin_sz = _color_bin_sz
                self.life -= (self.life%len(self._cycle_colors))+1
                self._last_cbin = _last_cbin = self.life//_color_bin_sz
            if self._last_cbin!=_last_cbin and self.life>=0:
                try:
                    color = self._cycle_colors[_last_cbin]
                except Exception as e:                    
                    raise e

                self.image.fill(color, special_flags=pygame.BLEND_MULT)
                self._last_cbin = _last_cbin
        else:
            self.image.fill(self.color, special_flags=pygame.BLEND_MULT)
            
        self.life -= passed
        #sel
        # f._fade = int(512 - self.life)//2 if (0<self.life<512) else 0

        return self
