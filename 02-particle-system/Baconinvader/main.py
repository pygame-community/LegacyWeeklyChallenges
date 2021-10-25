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
__author__ = "Baconinvader#2781"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .objects import *
from .particles import Particles
import math as m

BACKGROUND = 0x0F1012


def mainloop():
    pygame.init()

    player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))

    particles_list = []
    part = Particles(player.center, #pos
                     player.vel, #vel

                     player.rotation, #angle
                     2, #spread
                     0.6, #speed
                     0.25, #speed var
                     
                     150, #max
                     10, #size
                     3, #size var
                     60*20, #lifetime

                     (128,128,128), #colour
                     (256,256,256), #colour var

                     -0.02 #size change
                     )
    # The state is just a collection of all the objects in the game
    state = State(player, FpsCounter(60), *Asteroid.generate_many())

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            else:
                state.handle_event(event)

        if player.vel.magnitude() > 0.1:
            part = Particles(player.center, #pos
                         player.vel, #vel

                         -m.radians(player.rotation-90), #angle
                         0.9, #spread
                         1, #speed
                         0.2, #speed var
                         
                         40, #max
                         4, #size
                         3, #size var
                         60*5, #lifetime

                         (256,128,0), #colour
                         (128,64,0), #colour var

                         -0.1#size change
                         )
            state.add(part)

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()

        screen.fill(BACKGROUND)
        state.draw(screen)


if __name__ == "__main__":
    wclib.run(mainloop())
