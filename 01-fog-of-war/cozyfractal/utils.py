from functools import lru_cache
from pathlib import Path
from random import uniform
from typing import Tuple

import pygame

SUBMISSION_DIR = Path(__file__).parent
ASSETS = SUBMISSION_DIR.parent / "assets"


@lru_cache()
def load_image(name: str, scale=1):
    image = pygame.image.load(ASSETS / f"{name}.png")
    if scale != 1:
        new_size = image.get_width() * scale, image.get_height() * scale
        image = pygame.transform.scale(image, new_size)
    return image.convert_alpha()


def clamp(value, mini, maxi):
    """Clamp value between mini and maxi"""
    if value < mini:
        return mini
    elif maxi < value:
        return maxi
    else:
        return value


def random_in_rect(rect):
    """Return a random point uniformly in a rectangle."""
    rect = pygame.Rect(rect)
    return pygame.Vector2(uniform(rect.left, rect.right), uniform(rect.top, rect.bottom))


def from_polar(rho, theta):
    """Create a Vector2 from its polar representation."""
    v = pygame.Vector2()
    v.from_polar((rho, theta))
    return v


def chrange(
    x: float,
    initial_range: Tuple[float, float],
    target_range: Tuple[float, float],
    power=1,
    flipped=False,
):
    """Change the range of a number by mapping the initial_range to target_range using a linear transformation."""
    normalised = (x - initial_range[0]) / (initial_range[1] - initial_range[0])
    normalised **= power
    if flipped:
        normalised = 1 - normalised
    return normalised * (target_range[1] - target_range[0]) + target_range[0]


def fill_outside_rect(surf: pygame.Surface, color, rect: pygame.Rect):
    rect = surf.get_rect().clip(rect)
    if rect.width == 0:
        return  # Rect was outside the surface

    w, h = surf.get_size()
    # Two vertical bars
    surf.fill(color, (0, 0, rect.left, h))
    surf.fill(color, (rect.right, 0, w - rect.right, h))
    # Two small horizontal bar
    surf.fill(color, (rect.left, 0, rect.width, rect.top))
    surf.fill(color, (rect.left, rect.bottom, rect.width, h - rect.bottom))
