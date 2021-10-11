# General Instructions

### Achievements

In each challenge, there are different stages of success, *Casual*, *Ambitious*
and *Adventurous*
Succeeding in the casual stage is enough to complete the challenge,
however, in order to provide more challenge for the most adventurous
and ambitious of you, we provide two more puzzles.
The harder they are, the less point the reward,
as it is more important to always improve a bit that spend hours and hours
stuck on the same thing.

### Setup Code

The setup code in [`base/`](./base) consists of a simple top down game with trees and ghosts moving around.
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

### Tips

##### Use relative imports

You can structure your code the way you like, but if you use multiple files,
it is very recommended that you use *relative imports*, as it is the simplest way to
make the import system work both in the showcase and when run directly.

