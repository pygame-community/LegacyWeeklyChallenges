from functools import lru_cache
from pathlib import Path
from typing import Tuple

import pygame

from wclib.constants import SIZE, ROOT_DIR

__all__ = [
    "SIZE",
    "SUBMISSION_DIR",
    "ASSETS",
    "SCREEN",
    "load_image",
    "text",
    "radius_to_cover_rectangle",
    "auto_crop",
    "ninepatch",
]

SUBMISSION_DIR = Path(__file__).parent
GLOBAL_ASSETS = SUBMISSION_DIR.parent / "assets"
ASSETS = SUBMISSION_DIR / "assets"
SCREEN = pygame.Rect(0, 0, *SIZE)


@lru_cache()
def load_image(name: str, scale=1, alpha=True):
    """Load an image from the global assets folder given its name.

    If [base] is given, load a n image from this folder instead.
    For instance you can pass SUBMISSION_DIR to load an image from your own directory.

    If [scale] is not one, scales the images in both directions by the given factor.

    The function automatically calls convert_alpha() but if transparency is not needed,
    one can set [alpha] to False to .convert() the image instead.

    The results are cached, so this function returns the same surface every time it
    is called with the same arguments. If you want to modify the returned surface,
    .copy() it first.
    """

    try:
        print(ASSETS / f"{name}.png")
        image = pygame.image.load(ASSETS / f"{name}.png")
    except (TypeError, FileNotFoundError):
        image = pygame.image.load(GLOBAL_ASSETS / f"{name}.png")

    if scale != 1:
        new_size = int(image.get_width() * scale), int(image.get_height() * scale)
        image = pygame.transform.scale(image, new_size)

    if alpha:
        return image.convert_alpha()
    else:
        return image.convert()


@lru_cache()
def font(size=20, name=None):
    """
    Load a font from its name in the wclib/assets folder.

    If a Path object is given as the name, this path will be used instead.
    This way, you can use custom fonts that are inside your own folder.
    Results are cached.
    """

    name = name or "regular"
    if isinstance(name, Path):
        path = name
    else:
        path = ROOT_DIR / "wclib" / "assets" / (name + ".ttf")
    return pygame.font.Font(path, size)


@lru_cache(5000)
def text(txt, color, size=20, font_name=None):
    """Render a text on a surface. Results are cached."""
    return font(size, font_name).render(str(txt), True, color)


def radius_to_cover_rectangle(center, rect):
    """Minimum size of a a circle that covers completely a given rectangle."""
    center = pygame.Vector2(center)
    return max(
        center.distance_to(corner)
        for corner in (rect.topleft, rect.topright, rect.bottomright, rect.bottomleft)
    )


def auto_crop(surf: pygame.Surface):
    """Return the smallest subsurface of an image that contains all the visible pixels."""

    rect = surf.get_bounding_rect()
    return surf.subsurface(rect)


@lru_cache(1000)
def ninepatch(surf: pygame.Surface, size: Tuple[int, int]):
    """
    Stretch the surface to [size] by using a ninepatch technique.

    The surface should have black guidelines at the top and left that indicates
    the parts of the image, that can be stretched.
    """

    w = surf.get_width() - 2
    h = surf.get_height() - 2

    assert w <= size[0] and h <= size[1], "Cannot downscale ninepatches."

    top_guide = surf.subsurface(1, 0, w, 1).get_bounding_rect()
    left_guide = surf.subsurface(0, 1, 1, h).get_bounding_rect()
    surf = surf.subsurface((1, 1, w, h))

    def get_rects(center_rect, total_size):
        center_rect = pygame.Rect(center_rect)
        left = center_rect.left
        right = center_rect.right

        top = center_rect.top
        bottom = center_rect.bottom

        h_points = [0, left, right]
        h_sizes = [left, right - left, total_size[0] - right]
        v_points = [0, top, bottom]
        v_sizes = [top, bottom - top, total_size[1] - bottom]

        return [
            pygame.Rect(x, y, w, h)
            for (x, w) in zip(h_points, h_sizes)
            for (y, h) in zip(v_points, v_sizes)
        ]

    in_rects = get_rects(
        (top_guide.left, left_guide.top, top_guide.width, left_guide.height), (w, h)
    )
    out_rects = get_rects(
        (
            top_guide.left,
            left_guide.top,
            size[0] - (w - top_guide.right) - top_guide.left,
            size[1] - (h - left_guide.bottom) - left_guide.top,
        ),
        size,
    )

    out = pygame.Surface(size, pygame.SRCALPHA)
    out.fill((0, 0, 0, 0))
    for input, output in zip(in_rects, out_rects):
        s = surf.subsurface(input)
        if input.size != output.size:
            s = pygame.transform.scale(s, output.size)
        out.blit(s, output)

    return out
