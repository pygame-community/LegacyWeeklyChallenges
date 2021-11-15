import sys
from dataclasses import dataclass
from pathlib import Path

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "04-bouncing-bubbles." + Path(__file__).absolute().parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "CozyFractal#0042"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

from random import gauss, uniform, randint
from typing import List

import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

BACKGROUND = 0x0F1012
NB_BUBBLES = 42


@dataclass
class Collision:
    """ """

    center: pygame.Vector2
    normal: pygame.Vector2
    first: "Bubble"
    second: "Bubble"


# This is a suggestion of the interface of the button class.
# There are many other ways to do it, but I strongly suggest to
# at least use a class, so that it is more reusable.
class Bubble:
    def __init__(self):  # Just an example!
        self.radius = 25
        # For variable size, uncomment the next line
        # But then you also need to take the size of the bubbles in the collisions!
        # self.radius = int(gauss(25, 5))
        self.position = pygame.Vector2(
            randint(self.radius, SIZE[0] - self.radius),
            randint(self.radius, SIZE[1] - self.radius),
        )

        self.velocity = pygame.Vector2()
        self.velocity.from_polar((gauss(3, 0.5), uniform(0, 360)))

        self.color = pygame.Color(0)
        self.color.hsva = uniform(0, 360), 80, 80, 100

        self.collisions = []

    def logic(self, mouse_pos):
        self.collide_borders()
        acceleration = self.move_away_from_mouse(mouse_pos)
        acceleration += self.solve_collisions()

        self.velocity += acceleration
        self.position += self.velocity

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def solve_collisions(self):
        acceleration = pygame.Vector2()

        for collision in self.collisions:
            pass

        self.collisions.clear()
        return acceleration

    def move_away_from_mouse(self, mouse_pos):
        """Return the acceleration to make the bubble move away from the mouse.
        This acceleration can then just be added to the velocity."""
        bubble_to_mouse = mouse_pos - self.position
        distance_to_mouse = bubble_to_mouse.length()
        if distance_to_mouse > 0:
            direction = -bubble_to_mouse.normalize()
            return direction * 10 / max(10, distance_to_mouse)
        return pygame.Vector2()

    def collide_borders(self):
        # We treat differently the borders, but if you do the ambitious challenge
        # you can replace this code with the collisions with rectangles,
        # using one large rectangle for each edge.

        # Here notice that we don't always invert the velocity,
        # we invert the velocity only if it would push the bubble
        # more inside the wall. Otherwise, the bubble is already
        # going "out" of the wall, so we let it do so!
        # You should try to use the same principle when doing
        # bubble-bubble collisions.
        if self.position.x - self.radius <= 0 and self.velocity.x < 0:
            self.velocity.x *= -1
        elif self.position.x + self.radius >= SIZE[0] and self.velocity.x > 0:
            self.velocity.x *= -1

        if self.position.y - self.radius <= 0 and self.velocity.y < 0:
            self.velocity.y *= -1
        elif self.position.y + self.radius >= SIZE[1] and self.velocity.y > 0:
            self.velocity.y *= -1

    @classmethod
    def update_all(cls, bubbles: "List[Bubble]"):
        for bubble in bubbles:
            bubble.position += bubble.velocity
            bubble.collide_borders()

        collisions = []
        for i, b1 in enumerate(bubbles):
            for b2 in bubbles[i + 1 :]:
                pass


def mainloop():
    pygame.init()

    bubbles = [Bubble() for _ in range(NB_BUBBLES)]

    mouse_position = (0, 0)

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEMOTION:
                mouse_position = event.pos

        Bubble.update_all(bubbles)

        # Drawing the screen
        screen.fill(BACKGROUND)
        for button in bubbles:
            button.draw(screen)

        clock.tick(60)


# ---- Recommended: don't modify anything bellow this line ---- #
if __name__ == "__main__":
    try:
        # Note: your editor might say that this is an error, but it's not.
        # Most editors can't understand that we are messing with the path.
        import wclib
    except ImportError:
        # wclib may not be in the path because of the architecture
        # of all the challenges and the fact that there are many
        # way to run them (through the showcase, or on their own)
        ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
        sys.path.append(str(ROOT_FOLDER))
        import wclib

    wclib.run(mainloop())
