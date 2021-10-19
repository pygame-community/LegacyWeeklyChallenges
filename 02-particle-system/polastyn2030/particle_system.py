# theoretically I could use system in 'objects.py', but the script must be independent
# and reusable in other projects, so I have to write it again...
# I'll remove this comment if I am going to re-use this code.

from __future__ import annotations


from typing import Callable, TypeVar as _TypeVar

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


class BaseParticleObject:
    def __init__(
                self, surface: pg.Surface | BaseDynamicSurface,
                size: pg.Vector2, position: pg.Vector2,
                rotation: float, bounding_box: pg.Rect
            ):
        self.source_surface = surface
        self.size = size
        self.position = position
        self.rotation = rotation
        self.source_rect = bounding_box

        self._smooth_scale = True

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
    def rect(self):
        copy = self.source_rect.copy()
        copy.topleft = pg.Vector2(copy.topleft) + self.position
        return copy

    @property
    def tuple_size(self):
        return int(self.size.x), int(self.size.y)


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

        super().__init__(surface, size, position, rotation, bounding_box)
        self.life_time = life_time

        self.speed = speed
        self.rotation_speed = rotation_speed
        self.scale_change = scale_change

    @property
    def alive(self):
        return self.life_time > 0

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
