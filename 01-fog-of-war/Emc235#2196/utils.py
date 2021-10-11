from functools import lru_cache
from pathlib import Path
from random import uniform
from typing import Union, List, Tuple

import pygame

SUBMISSION_DIR = Path(__file__).parent
ASSETS = SUBMISSION_DIR.parent / "assets"

number_type = Union[int, float]
rect_type = Union[pygame.Rect, List[int], Tuple[int, int, int, int]]


@lru_cache()
def load_image(name: str, scale=1):
    image = pygame.image.load(ASSETS / f"{name}.png")
    if scale != 1:
        new_size = image.get_width() * scale, image.get_height() * scale
        image = pygame.transform.scale(image, new_size)
    return image.convert_alpha()


def clamp(value: number_type, mini: number_type, maxi: number_type) -> number_type:
    """Clamp value between mini and maxi"""
    return mini if value < mini else value if value < maxi else maxi


def random_in_rect(rect: rect_type) -> pygame.math.Vector2:
    """Return a random point uniformly in a rectangle."""
    rect = pygame.Rect(rect)
    return pygame.Vector2(uniform(rect.left, rect.right), uniform(rect.top, rect.bottom))


def from_polar(rho: float, theta: float) -> pygame.math.Vector2:
    """Create a Vector2 from its polar representation."""
    v = pygame.math.Vector2()
    v.from_polar((rho, theta))
    return v
