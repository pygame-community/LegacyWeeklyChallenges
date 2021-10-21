from dataclasses import dataclass
from typing import Union

import numpy as np

__all__ = [
    "make_generator",
    "Generator",
    "Uniform",
    "Gauss",
    "Constant",
    "MousePosGenerator",
    "IntoGenerator",
]

import pygame


def make_generator(obj: "IntoGenerator") -> "Generator":
    if isinstance(obj, Generator):
        return obj
    return Constant(obj)


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


class Gauss(Generator):
    def __init__(self, center, spread=None):
        self.center = np.array(center)
        self.spread = np.array(spread) if spread is not None else self.center / 4

        assert self.center.size in {1, 2}
        assert self.center.shape == self.spread.shape

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
        if len(self.default) == 1:
            reps = (nb,)
        else:
            reps = (nb, 1)
        return np.tile(self.default, reps)


class MousePosGenerator(Generator):
    def __init__(self, initial=(0, 0)):
        self.mouse_pos = np.array(initial, float)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = np.array(event.pos, float)

    def gen(self, nb: int):
        return np.tile(self.mouse_pos, (nb, 1))


IntoGenerator = Union[Generator, float, tuple, list, np.array]
