import random
import sys
from pathlib import Path

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "02-particle-system." + Path(__file__).parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "Emc235#2196"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    "Adventurous"
]

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .objects import *

BACKGROUND = 0x0F1012

# for the Casual challenge
# added thrusters particles
# bullet trail
# asteroid destroying particles

# for the Adventurous challenge
# Images as well as drawn particles
# Change colors overtime with multistep gradients
# Ability to spawn a burst of particles but also spawn some over time


def mainloop():
    pygame.init()

    FPS = 60

    player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))
    # The state is just a collection of all the objects in the game
    state = State(player, FpsCounter(FPS), *Asteroid.generate_many(10))

    dt = 1
    last_time = time.time()

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            else:
                state.handle_event(event)
        # print(len(particles.particles))

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()

        screen.fill(BACKGROUND)
        state.draw(screen)

        particles.burst(
            pygame.math.Vector2(random.randint(0, SIZE[0]), random.randint(0, SIZE[0])),
            pygame.math.Vector2(3, 0),
            30,
            3,
            pygame.Color(int(random.random()*255), int(random.random()*255), int(random.random()*255)),
            n=40
        ).logic(dt).draw(screen)

        dt = time.time() - last_time
        dt *= FPS
        last_time = time.time()


if __name__ == "__main__":
    wclib.run(mainloop())
