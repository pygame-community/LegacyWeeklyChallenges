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
__author__ = "CoopERR"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .objects import *

BACKGROUND = 0x0F1012


def mainloop():
    pygame.init()

    player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))
    # The state is just a collection of all the objects in the game
    state = State(player, FpsCounter(60), *Asteroid.generate_many())

    particle = Particle()
    PARTICLE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(PARTICLE_EVENT, 10)
    font = pygame.font.Font(None, 30)

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            else:
                state.handle_event(event)

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()

        screen.fill(BACKGROUND)
        if player.speed < -2:
            for event in events:
                if event.type == PARTICLE_EVENT:
                    x, y = player.thruster_position()
                    particle.add_particles(x, y)
        particle.draw(screen)
        state.draw(screen)

        # particle counter display
        partic_count = font.render("Particles: " + str(len(particle.particles)), True, pygame.Color('white'))
        screen.blit(partic_count, (0, 50))





if __name__ == "__main__":
    wclib.run(mainloop())
