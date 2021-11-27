import importlib
import json
import subprocess
import sys
from collections import namedtuple
from dataclasses import dataclass
from functools import lru_cache
from time import time
from typing import Generator, List, Tuple, Iterator, Type, Optional

import pygame

from .constants import SIZE, ROOT_DIR

MainLoop = Generator[None, Tuple[pygame.Surface, List[pygame.event.Event]], None]

__all__ = [
    "MainLoop",
    "Entry",
    "run",
    "get_challenges",
    "get_entries",
    "ChallengeData",
    "get_challenge_data",
]

a = ["Casual", "Ambitious", "Adventurous"]


class Entry:
    challenge: str
    entry: str
    # Metadata
    discord_tag: str
    display_name: str
    achievements: List[str]
    min_python_version: Tuple[int, int]
    dependencies: List[str]

    def __init__(self, challenge: str, entry: str):
        """Load the metadata of an entry from the disk."""
        name = f"{challenge}.{entry}.metadata"
        module = importlib.import_module(name, f"{challenge}.{entry}")
        # noinspection PyUnresolvedReferences
        data: Entry = module.Metadata

        self.challenge = challenge
        self.entry = entry

        self.discord_tag = data.discord_tag
        self.display_name = data.display_name
        self.achievements = data.achievements
        self.min_python_version = data.min_python_version
        self.dependencies = data.dependencies

    def __str__(self):
        return f"{self.challenge}/{self.entry}"

    def get_missing_dependencies(self) -> List[str]:
        """Return the dependencies that are not found on import."""
        missing = []
        for req in self.dependencies:
            try:
                importlib.import_module(req)
            except ModuleNotFoundError:
                missing.append(req)
        return missing

    def install_missing_dependencies(self) -> int:
        """Install the missing dependecies via pip."""
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            *self.get_missing_dependencies(),
        ]
        print("Running:", command)
        ret_code = subprocess.check_call(command)
        importlib.invalidate_caches()
        return ret_code

    def get_mainloop(self) -> MainLoop:
        """Import and return the mainloop of the entry.
        This will fail if not all dependencies are installed."""
        name = f"{self.challenge}.{self.entry}.main"
        loop = importlib.import_module(name, f"{self.challenge}.{self.entry}").mainloop()
        return loop


def run(mainloop: MainLoop, screen_size=SIZE):
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


def get_challenges():
    """Return all the challenges, from the more recent to the least."""
    # Challenges are the only files/folders that start with a digit
    # and contain a data.json file.
    return sorted(
        [c.stem for c in ROOT_DIR.glob("[0-9]*") if (c / "data.json").exists()], reverse=True
    )


def get_entries(challenge: str) -> Iterator[Entry]:
    """Get all entries for a given challenge."""
    challenge_dir = ROOT_DIR / challenge
    for directory in challenge_dir.iterdir():
        if not ((directory / "main.py").exists() and (directory / "metadata.py").exists()):
            continue

        yield Entry(challenge, directory.stem)


ChallengeData = namedtuple("ChallengeData", "name entries_nb")


@lru_cache()
def get_challenge_data(challenge: str) -> ChallengeData:
    data: dict = json.loads((ROOT_DIR / challenge / "data.json").read_text())
    name = data.get("name", "No name")

    return ChallengeData(name, sum(1 for _ in get_entries(challenge)))
