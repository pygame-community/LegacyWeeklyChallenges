from functools import lru_cache
from pathlib import Path

import pygame

from wclib.constants import SIZE, ROOT_DIR

__all__ = [
    "SIZE",
    "SUBMISSION_DIR",
    "ASSETS",
    "SCREEN",
    "load_image",
    "text",
]

SUBMISSION_DIR = Path(__file__).parent
ASSETS = SUBMISSION_DIR.parent / "assets"
SCREEN = pygame.Rect(0, 0, *SIZE)


@lru_cache()
def load_image(name: str, scale=1, alpha=True, base: Path = ASSETS):
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

    image = pygame.image.load(base / f"{name}.png")
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
