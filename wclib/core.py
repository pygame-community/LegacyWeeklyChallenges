import importlib
import json
import subprocess
import sys
from collections import namedtuple
from functools import lru_cache
from time import time
from typing import Generator, List, Tuple, Iterator

import pygame

from .constants import SIZE, ROOT_DIR

MainLoop = Generator[None, Tuple[pygame.Surface, List[pygame.event.Event]], None]

__all__ = [
    "MainLoop",
    "run",
    "get_missing_requirements",
    "get_requirements",
    "install_missing_requirements",
    "get_mainloop",
    "get_challenges",
    "get_entries",
    "ChallengeData",
    "get_challenge_data",
]


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


def get_requirements(challenge: str, entry: str) -> List[str]:
    req_path = ROOT_DIR / challenge / entry / "requirements.txt"

    if not req_path.exists():
        return []

    # Can't use the := operator as we want python 3.6 compat.
    requirements = []
    for line in req_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            # Common possible mistakes
            assert not " " in line, f"Space in the requirements of {challenge}/{entry}."
            assert not "." in line, f"Package with '.' in the requirements of {challenge}/{entry}."
            requirements.append(line)
    return requirements


def get_missing_requirements(challenge: str, entry: str) -> List[str]:
    missing = []
    for req in get_requirements(challenge, entry):
        try:
            importlib.import_module(req)
        except ModuleNotFoundError:
            missing.append(req)
    return missing


def install_missing_requirements(challenge: str, entry: str) -> int:
    missing = get_missing_requirements(challenge, entry)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        *missing,
    ]
    print("Running:", command)
    ret_code = subprocess.check_call(command)
    importlib.invalidate_caches()
    return ret_code


def get_mainloop(challenge: str, entry: str) -> MainLoop:
    """Utility to import a mainloop."""

    name = f"{challenge}.{entry}.main"
    loop = importlib.import_module(name, f"{challenge}.{entry}").mainloop()
    return loop


def get_challenges():
    """Return all the challenges, from the more recent to the least."""
    # Challenges are the only files/folders that start with a digit
    # and contain a data.json file.
    return sorted(
        [c.stem for c in ROOT_DIR.glob("[0-9]*") if (c / "data.json").exists()], reverse=True
    )


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
