import random
from dataclasses import dataclass
from typing import Union, Callable

import numpy as np

__all__ = [
    "make_generator",
    "Generator",
    "Uniform",
    "UniformInRect",
    "UniformInImage",
    "Gauss",
    "Constant",
    "Lambda",
    "MousePosGenerator",
    "IntoGenerator",
]

import pygame


def make_generator(obj: "IntoGenerator") -> "Generator":
    if isinstance(obj, Generator):
        return obj
    return Constant(obj)


def call_me_maybe(f_or_value, dtype=lambda _: _):
    if callable(f_or_value):
        return dtype(f_or_value())
    return dtype(f_or_value)


class Generator:
    def __call__(self, nb: int):
        return self.gen(nb)

    def gen(self, nb: int):
        return np.zeros(nb)


@dataclass
class Uniform(Generator):
    start: float
    end: float
    integer: bool = False

    def gen(self, nb: int):
        if self.integer:
            return np.random.randint(self.start, self.end, nb)
        else:
            return np.random.uniform(self.start, self.end, nb)


class UniformInRect(Generator):
    def __init__(self, rect, on_edge=False):
        self.on_edge = on_edge
        self.rect = pygame.Rect(rect)

    def gen(self, nb: int):
        pos = np.random.uniform(self.rect.topleft, self.rect.bottomright, (nb, 2))
        if self.on_edge:
            rect = np.array([self.rect.topleft, self.rect.bottomright])
            axis = np.random.randint(0, 2, nb)
            side = np.random.randint(0, 2, nb)
            pos[np.indices((nb,)), axis] = rect[side, axis]

        return pos


class UniformInImage(Generator):
    def __init__(self, image: pygame.Surface, shift=(0, 0)):
        self.shift = np.array(shift)
        alpha = pygame.surfarray.pixels_alpha(image)
        self.possible = np.array(np.nonzero(alpha), float).T

    def gen(self, nb: int):
        indices = np.random.randint(0, self.possible.shape[0], nb)
        return self.possible[indices] + self.shift


class Gauss(Generator):
    def __init__(self, center, spread=None):
        self._center = center
        self._spread = spread

        assert self.center.size in {1, 2}
        assert self.center.shape == self.spread.shape

    @property
    def center(self):
        return call_me_maybe(self._center, np.array)

    @property
    def spread(self):
        spread = call_me_maybe(self._spread)
        if spread is None:
            return self.center / 4
        return np.array(spread)

    def gen(self, nb: int):
        if self.center.size == 2:
            shape = (nb, 2)
        else:
            shape = (nb,)
        return np.random.normal(self.center, self.spread, shape)


class Constant(Generator):
    def __init__(self, default, dtype=float):
        self.default = np.array(default, dtype)

    def gen(self, nb: int):
        if self.default.size == 1:
            reps = (nb,)
        else:
            reps = (nb, 1)
        return np.tile(self.default, reps)


class Lambda(Constant):
    def __init__(self, f: Callable):
        super().__init__(f())
        self.f = f

    def gen(self, nb: int):
        super().__init__(self.f())
        return super().gen(nb)


class MousePosGenerator(Generator):
    def __init__(self, initial=(0, 0)):
        self.mouse_pos = np.array(initial, float)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = np.array(event.pos, float)

    def gen(self, nb: int):
        return np.tile(self.mouse_pos, (nb, 1))


IntoGenerator = Union[Generator, float, tuple, list, np.array]
