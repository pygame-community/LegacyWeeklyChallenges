import importlib
from time import time
from typing import Generator, List, Tuple

import pygame

from .constants import SIZE

MainLoop = Generator[None, Tuple[pygame.Surface, List[pygame.event.Event]], None]


def run(
    mainloop: MainLoop,
    screen_size=SIZE,
):
    """Minimal utility that runs a mainloop generator."""

    screen = pygame.display.set_mode(screen_size)
    start = time()
    frames = 0
    next(mainloop)
    while True:
        frames += 1
        events = pygame.event.get()
        try:
            mainloop.send((screen, events))
        except StopIteration:
            break
        pygame.display.flip()

    end = time()
    print(f"App run for {end - start:02}s at {frames / (end - start)} FPS.")


def get_mainloop(challenge: str, entry: str) -> MainLoop:
    """Utility to import a mainloop."""

    name = f"{challenge}.{entry}.main"
    print(name)
    loop = importlib.import_module(name).mainloop()
    return loop
