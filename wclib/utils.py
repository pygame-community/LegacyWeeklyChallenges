from functools import lru_cache

import pygame

from wclib.constants import ASSETS


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
