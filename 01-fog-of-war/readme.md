# 01 - Fog of War

The goal of this challenge is to implement a Fog of War mechanic
similar to Age of empires.

### Achievements

There are different stages of success for the challenge. 
Succeeding in the casual stage is enough to complete the challenge,
however, in order to provide more challenge for the most adventurous 
and ambitious of you, we provide two more puzzles. 
The harder they are, the less point the reward, 
as it is more important to always improve a bit that spend hours and hours
stuck on the same thing.

Here a more detailed description of the different levels and the amount of 
`C`hallenger `P`oints they provide:

- Casual `+3 CP`: The world around the player is visible but the rest of the map 
    is hidden in complete darkness.
- Ambitious `+2 CP`: The world is visible around the player and softly fades to dark, as if the player had a light.
    In the distance, everything is black.
- Adventurous `+1 CP`: Like in Age of Empires the map starts all dark. The world around the player is visible, 
    the parts already explored are darker and the unexplored parts are totally dark.
    Additionally, in the explored parts the player sees only the static objects (Trees, Houses…)
    but not the moving ghosts.

### Setup

The setup code in [`base/`](arosso17) consists of a simple top down game with trees and ghosts moving around.
To get started, duplicate the whole `base` folder and rename the copy with your username 
(will call it `yourname/` from now on). All your modifications should be inside the `yourname/` folder,
otherwise it would be impossible to have a showcase of all the submissions.

In this `yourname/` folder, you'll find a `main.py` file. This is the entry point of your submission and where 
most of your code will go. 
In this file, you will find a `mainloop` function, which is the only thing that is required so that the submission 
appears in the showcase. The showcase needs to have the control of the events and the display, so they are
passed down to `mainloop` in a surprising way: the `send` mechanism of generators. 
Don't be afraid if that looks like black magic to you,
you can participate without understanding it.
You may be used to a main loop that looks like this:

```python
import pygame
def mainloop():
    screen = pygame.display.set_mode((800, 500))
    # More setup...
    while True:
        for event in pygame.event.get():
            ...  # Event handling
        
        # Logic and rendering of your game...
        screen.blit(...)
        pygame.display.update()
```

But now it will look like this:
```python
def mainloop():
    # Setup, but without setting up the screen
    while True:
        screen, events = yield
        for event in events:
            ...  # Event handling
        # Logic and rendering of your game, on the screen variable
        screen.blit(...)
        # No need to call pygame.display.update() it is done by the showcase.
```

If you are used to classes, you can also have all your code in a class, for instance `App`,
then you only need a statement like `mainloop = App.run` if the `run()` method is your main loop,
to have your submission discovered.

### Submitting your entry

Before the deadline, make sure that your entry is runnable both via the showcase, 
when you run the top level [`main.py`](../main.py) and when you run it individually
from you own `yourname/main.py`.

There are two ways to submit an entry:
 - send a zip of your code in the discord
 - make a pull request directly on this repository

In either case, you need to post a screenshot of your entry in `#challenge-submission`
with your files if you don't do a PR, and with some comment if you want. 
Sharing your code will help others learn, and you may receive good advice too!

Have fun !

### Tips

##### Use relative imports

You can structure your code the way you like, but if you use multiple files, 
it is very recommended that you use *relative imports*, as it is the simplest way to 
make the import system work both in the showcase and when run directly.

### Credits

 - Tileset: [GameBoy Style Dark Forest Tileset by Cluly](https://cluly.itch.io/gameboy-style-dark-forest-tileset)
 - Ghosts: [Free 16x16 Pixel Art 8-Directional Characters by Maytch](https://maytch.itch.io/free-16x16-pixel-art-8-directional-characters)
 - Setup code: [CozyFractal](https://cozyfractal.com)

### Legal stuff

By submitting your game, you agree that we add its code to the repository 
and that it can be:
- used (for instance in the showcase), 
- modified (for instance to work with a future version of the showcase),
- shared (for instance as a mean to illustrate the capabilities of pygames).

But all those uses must be for the good of the community, and never for any individual.
This concerns for instance any profits that could be made: they have to be used for the 
benefit of the whole community.
