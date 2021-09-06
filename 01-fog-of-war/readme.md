# 01 - Fog of War

The goal of this challenge is to implement a Fog of War mechanic
similar to Age of empires.

### Achievements

- Casual `3 CP`: The world around the player is visible but the rest of the map is hidden in darkness.
- Ambitious `2 CP`: The world is visible around the player and softly fades to dark, as if the player had a light.
    In the distance, everything is black.
- Adventurous `1 CP`: Like in Age of Empires the map starts all dark. The world around the player is visible, 
    the parts already explored are darker and the unexplored parts are totally dark.
    Additionnaly, in the explored parts the player sees only the static objects (Trees, House..)
    but not the moving ghosts.

### Setup

The setup code in [`base/`](./base) consists of a simple top down game with trees and ghosts moving around.
To get started, duplicate the whole `base` folder and rename the copy with your username 
(will call it `yourname/` from now on). All your modifications should be inside the `yourname/` folder,
otherwise it would be impossible to have a showcase of all the submissions.

In this `yourname/` folder, you'll find a `main.py` file. This is the entry point of your submission and where 
most of your code will go. 
In this file, you will find a `mainloop` function, which is the only thing that is required so that the submission 
apprears in the showcase. The showcase needs to have the control of the events and the display, so they are
passed down to `mainloop` in an suprising way: the `send` mechanism of generators. Do be afraid if that seems like black magic,
you can particpate without understanding it. In practice, a simple main loop looks like this:

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


### Credits

 - Tileset: [GameBoy Style Dark Forest Tileset by Cluly](https://cluly.itch.io/gameboy-style-dark-forest-tileset)
 - Ghosts: [Free 16x16 Pixel Art 8-Directional Characters by Maytch](https://maytch.itch.io/free-16x16-pixel-art-8-directional-characters)
 - Setup code: [CozyFractal](https://cozyfractal.com)
