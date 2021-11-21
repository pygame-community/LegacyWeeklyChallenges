import sys
from dataclasses import dataclass
from pathlib import Path
from random import gauss, uniform, randint
from typing import List

import pygame

# This line tells python how to handle the relative imports
# when you run this file directly. Don't modify this line.
__package__ = "04-bouncing-bubbles." + Path(__file__).absolute().parent.name

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .utils import *

BACKGROUND = 0x0F1012
NB_BUBBLES = 42


class Bubble:
    MAX_VELOCITY = 7

    def __init__(self, position=None):
        self.radius = int(gauss(25, 5))

        if position is None:
            # Default position is random.
            self.position = pygame.Vector2(
                randint(self.radius, SIZE[0] - self.radius),
                randint(self.radius, SIZE[1] - self.radius),
            )
        else:
            self.position = position

        # Set a random direction and a speed of around 3.
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((gauss(3, 0.5), uniform(0, 360)))

        # Pick a random color with high saturation and value.
        self.color = pygame.Color(0)
        self.color.hsva = uniform(0, 360), 80, 80, 100

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def move_away_from_mouse(self, mouse_pos: pygame.Vector2):
        """Apply a force on the bubble to move away from the mouse."""
        bubble_to_mouse = mouse_pos - self.position
        distance_to_mouse = bubble_to_mouse.length()
        if 0 < distance_to_mouse < 200:
            strength = chrange(distance_to_mouse, (0, 200), (1, 0), power=2)
            self.velocity -= bubble_to_mouse.normalize() * strength

    def move(self):
        """Move the bubble according to its velocity."""
        # We first limit the velocity to not get bubbles that go faster than what we can enjoy.
        if self.velocity.length() > self.MAX_VELOCITY:
            self.velocity.scale_to_length(self.MAX_VELOCITY)

        self.position += self.velocity
        debug.vector(self.velocity, self.position, scale=10)

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

    def collide(self, other):
        pass


@dataclass
class Collision:
    center: pygame.Vector2
    normal: pygame.Vector2
    first: "Bubble"
    second: "Bubble"


class World(List[Bubble]):
    def __init__(self, nb):
        super().__init__(Bubble() for _ in range(nb))

    def logic(self, mouse_position: pygame.Vector2):
        for bubble in self:
            bubble.move()
            bubble.collide_borders()
            bubble.move_away_from_mouse(mouse_position)

        # We collect all collisions
        collisions = []
        for i, b1 in enumerate(self):
            for b2 in self[i + 1 :]:
                collision = b1.collide(b2)
                if collision:
                    collisions.append(collision)

        # Then resolve them all at once.
        # Indeed, if we resolve them at the same time as we find them, we may not get all collisions
        for collision in collisions:
            # TODO: Resolve the collision.
            pass

    def draw(self, screen):
        for bubble in self:
            bubble.draw(screen)


def mainloop():
    pygame.init()

    world = World(NB_BUBBLES)

    mouse_position = pygame.Vector2()

    fps_counter = FpsCounter(60, Bubbles=world)
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEMOTION:
                mouse_position.xy = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                world.append(Bubble(event.pos))
            debug.handle_event(event)
            fps_counter.handle_event(event)

        # Handle the collisions
        world.logic(mouse_position)
        fps_counter.logic()

        # Drawing the screen
        screen.fill(BACKGROUND)
        world.draw(screen)
        fps_counter.draw(screen)
        debug.draw(screen)


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
