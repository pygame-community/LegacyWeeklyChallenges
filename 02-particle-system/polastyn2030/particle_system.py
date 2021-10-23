# theoretically I could use system in 'objects.py', but the script must be independent
# and reusable in other projects, so I have to write it again...
# I'll remove this comment if I am going to re-use this code.

from __future__ import annotations


from typing import Callable, TypeVar as _TypeVar, Type
import random as rd

import pygame as pg


class BaseDynamicSurface(pg.Surface):
    # noinspection PyMissingConstructor
    def __init__(self, source_surface: pg.Surface, *arg_configs, **kwarg_configs):
        self.source_surface = source_surface
        self.arg_configs = arg_configs
        self.kwarg_configs = kwarg_configs
        self.__names__ = {"source_surface", "arg_configs", "kwarg_configs", "tick", "map_self_to_new"}

    def __getattribute__(self, item: str):
        if item.startswith("__") and item.endswith("__"):
            return object.__getattribute__(self, item)
        elif item in self.__names__:
            return object.__getattribute__(self, item)
        else:
            return getattr(self.source_surface, item)

    def tick(self):
        pass

    def map_self_to_new(self, surface: pg.Surface | None = None):
        return self.__cls__(
            surface if surface else self.source_surface, *self.arg_configs, **self.kwarg_configs
        )


class BaseParticleObject(pg.sprite.Sprite):
    def __init__(self, surface: pg.Surface | BaseDynamicSurface, size: pg.Vector2, position: pg.Vector2,
                 rotation: float, bounding_box: pg.Rect, life_time: int):
        super().__init__()
        self.source_surface = surface
        self.size = size
        self.position = position
        self.rotation = rotation
        self.source_rect = bounding_box
        self.life_time = life_time

        self._smooth_scale = True

    @property
    def alive(self):
        return self.life_time > 0

    @property
    def surface(self):
        copy = self.source_surface.copy()

        if self._smooth_scale:
            copy = pg.transform.smoothscale(copy, self.tuple_size)
        else:
            copy = pg.transform.smoothscale(copy, self.tuple_size)

        copy = pg.transform.rotate(copy, self.rotation)

        if isinstance(self.source_surface, BaseDynamicSurface):
            copy = self.source_surface.map_self_to_new(copy)

        return copy

    @property
    def image(self):
        return self.surface

    @property
    def rect(self):
        copy = self.source_rect.copy()
        copy.topleft = pg.Vector2(copy.topleft) + self.position
        return copy

    @property
    def tuple_size(self):
        return int(self.size.x), int(self.size.y)

    def update(self, *args, **kwargs) -> None:
        if not self.alive:
            self.kill()

        self.tick()

    def tick(self):
        pass


class DynamicParticle(BaseParticleObject):
    def __init__(
            self,
            surface: pg.Surface | BaseDynamicSurface, size: pg.Vector2,
            position: pg.Vector2, rotation: float,
            bounding_box: pg.Rect, life_time: int,
            speed: pg.Vector2,
            rotation_speed: float,
            scale_change: pg.Vector2
    ):

        super().__init__(surface, size, position, rotation, bounding_box, life_time)

        self.speed = speed
        self.rotation_speed = rotation_speed
        self.scale_change = scale_change

    def tick(self):
        if not self.alive:
            return

        self.life_time -= 1

        self.__change("position", self.speed)
        self.__change("rotation", self.rotation_speed)
        self.__change("size", self.scale_change)

        if isinstance(self.surface, BaseDynamicSurface):
            self.surface.tick()

    _T = _TypeVar("_T", bound=object)

    def __change(self, name: str, by: Callable[[_T], _T] | _T):
        self.__change_value(name, getattr(self, name, None), by)

    def __change_value(self, name: str, data: _T, by: Callable[[_T], _T] | _T):
        if getattr(by, "__call__", False):
            setattr(self, name, by(data))
        else:
            try:
                setattr(self, name, data + by)
            except TypeError:
                pass


class RandomPos:
    def __init__(self, center: pg.Vector2, pos_range: float | pg.Rect):
        self.center = center
        self.pos_range = pos_range

    def __get__(self, instance, owner):
        if instance is None:
            return self

    def get(self):
        if isinstance(self.pos_range, float):
            offset = pg.Vector2(1, 0)
            offset.rotate(rd.randint(0, 360))
            offset *= rd.randint(0, int(self.pos_range))
            return self.center + offset

        x = rd.randint(0, self.pos_range.w)
        y = rd.randint(0, self.pos_range.h)

        pos = pg.Vector2(x, y)
        pos += pg.Vector2(self.pos_range.topleft)

        return pos


class RandomFloat:
    def __init__(self, smallest: float, biggest: float):
        self.smallest = smallest
        self.biggest = biggest

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.get()

    def get(self):
        random = rd.random()
        diff = self.biggest - self.smallest
        random *= diff
        random += self.smallest
        return random


class RandomInt(RandomFloat):
    def get(self):
        ret = super(RandomInt, self).get()
        return int(ret)


class ParticleObjectInfo:
    def __init__(self,
                 surface: pg.Surface | BaseDynamicSurface,
                 size: pg.Vector2 | RandomPos,
                 size_change: pg.Vector2 | RandomPos,
                 rotation: float | RandomFloat,
                 rotation_speed: float | RandomFloat,
                 life_time: int | RandomInt,
                 bounding_box: pg.Rect,
                 speed: float | RandomFloat,
                 moving_angle: float | RandomFloat,
                 particle_class: Type[DynamicParticle] | None = None
                 ):
        self.surface = surface
        self.size = size
        self.size_change = size_change
        self.rotation = rotation
        self.rotation_speed = rotation_speed
        self.life_time = life_time
        self.bounding_box = bounding_box
        self.speed = speed
        self.angle = moving_angle
        self.particle_class = particle_class if particle_class is not None else DynamicParticle


class ParticleSpawnerInfo:
    def __init__(
            self,
            spawn_pos: pg.Vector2 | RandomPos,
            spawn_delay: int | RandomInt,
            object_info: ParticleObjectInfo
    ):
        self.spawn_pos = spawn_pos
        self.spawn_delay = spawn_delay
        self.object_info = object_info

    def generate(self):
        info = self.object_info
        speed = pg.Vector2(1, 0) * info.angle * info.speed
        obj = self.object_info.particle_class(
            info.surface, info.size, self.spawn_pos, info.rotation, info.bounding_box,
            info.life_time, speed, info.rotation_speed, info.size_change
        )
        return obj


class BaseParticleSpawner(pg.sprite.Group):
    def __init__(self, info: ParticleSpawnerInfo):
        super().__init__()
        self.info = info
        self.active = True
        self.next_spawn = 0

    def spawn(self):
        self.add(self.info.generate())

    def update(self, *args, **kwargs) -> None:
        if self.active:
            if self.next_spawn <= 0:
                self.spawn()
                self.next_spawn += self.info.spawn_delay
            self.next_spawn -= 1
        super(BaseParticleSpawner, self).update(*args, **kwargs)
