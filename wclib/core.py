import importlib
import json
from collections import namedtuple
from functools import lru_cache
from time import time
from typing import Generator, List, Tuple, Iterator

import pygame

from .constants import SIZE, ROOT_DIR

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
    loop = importlib.import_module(name, f"{challenge}.{entry}").mainloop()
    return loop


def get_challenges():
    """"""
    # Challenges are the only files/folders that start with digits
    return [c.stem for c in ROOT_DIR.glob("[0-9]*")]


def get_entries(challenge: str) -> Iterator[str]:
    """Get all entries for a given challenge."""
    challenge_dir = ROOT_DIR / challenge
    for directory in challenge_dir.iterdir():
        main = directory / "main.py"
        if not main.exists():
            continue

        yield directory.stem


ChallengeData = namedtuple("ChallengeData", "name entries_nb")


@lru_cache()
def get_challenge_data(challenge: str) -> ChallengeData:
    data: dict = json.loads((ROOT_DIR / challenge / "data.json").read_text())
    name = data.get("name", "No name")

    return ChallengeData(name, sum(1 for _ in get_entries(challenge)))
