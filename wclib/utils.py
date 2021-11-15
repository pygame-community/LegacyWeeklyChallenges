from functools import lru_cache
from typing import Tuple

import pygame

from wclib.constants import ASSETS

__all__ = ["font", "text", "load_image", "clamp", "overlay", "auto_crop", "chrange", "star"]


@lru_cache()
def font(size=20, name=None):
    """Load a font from the wclib/assets folder. Results are cached."""
    name = name or "regular"
    path = ASSETS / (name + ".ttf")
    return pygame.font.Font(path, size)


@lru_cache(5000)
def text(txt, color, size=20, font_name=None):
    """Render a text on a surface. Results are cached."""
    return font(size, font_name).render(str(txt), True, color)


@lru_cache(None)
def load_image(name: str, alpha=True):
    """Load an image from disk. Results are cached."""
    img = pygame.image.load(ASSETS / f"{name}.png")
    if alpha:
        return img.convert_alpha()
    else:
        return img.convert()


def clamp(value, mini, maxi):
    """Clamp value between mini and maxi"""
    if value < mini:
        return mini
    elif maxi < value:
        return maxi
    else:
        return value


@lru_cache()
def overlay(image: pygame.Surface, color, alpha=255):
    """Overlays a color on a surface."""
    img = pygame.Surface(image.get_size())
    img.set_colorkey((0, 0, 0))
    img.blit(image, (0, 0))

    mask = pygame.mask.from_surface(image)
    overlay = mask.to_surface(setcolor=color, unsetcolor=(255, 255, 0, 0))
    overlay.set_alpha(alpha)
    img.blit(overlay, (0, 0))

    return img


def auto_crop(surf: pygame.Surface):
    """Return the smallest subsurface of an image that contains all the visible pixels."""

    rect = surf.get_bounding_rect()
    return surf.subsurface(rect)


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


def outline(surf: pygame.Surface, color=(255, 255, 255), threshold=127):
    """Create an outline on the surface of the given color."""

    mask = pygame.mask.from_surface(surf, threshold)
    outline = mask.outline()
    output = pygame.Surface((surf.get_width() + 2, surf.get_height() + 2), pygame.SRCALPHA)

    for x, y in outline:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
            output.set_at((x + dx + 1, y + dy + 1), color)

    output.blit(surf, (1, 1))
    # output.set_colorkey(0)

    return output


@lru_cache()
def star(color):
    s = auto_crop(load_image("star")).copy()
    # s = pygame.transform.scale(s, (32, 32))

    s.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return outline(outline(s, "white"), "black")
