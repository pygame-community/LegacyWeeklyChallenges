# General Instructions

### Achievements

In each challenge, there are different stages of success, *Casual*, *Ambitious*
and *Adventurous*.

Succeeding in the casual stage is enough to complete the challenge,
however, in order to provide more challenge for the most adventurous
and ambitious of you, we provide two more puzzles.
The harder they are, the less point the reward,
as it is more important to always improve a bit that spend hours and hours
stuck on the same thing.

### Setup Code

The setup code in the challenge `base/` folder consists of a simple game prototype.
It is meant to be used as a starting point and for inspiration. However, you can
completely remove it and start something from scratch if you want to. 
If you want to, you can also use a small game that you were already developing,
but it should not have already solved the challenge: the part of the submission
that solves the challenge must be *new* work.

To get started, **duplicate** the whole `base` folder and rename the copy with your username
(will call it `yourname/` from now on). All your modifications should be inside the `yourname/` folder,
otherwise it would be impossible to have a showcase of all the submissions.

> Please do NOT modify the base folder. Copy and paste it instead.

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

### Using your own assets

Since you can only modify your own folder, you can only add your assets there.
However, when you want to load them, you need to be a bit careful, because your 
code will be run from different places (at least the showcase and on its own),
so you need to specify your paths well.

#### With the provided utilities

If you use the utility provided, for instance `load_image()`, you can always
configure the base path from which they search for the assets. 
Typically, to load an image stored in your submission folder, you would use

```python
image = load_image(..., base=SUBMISSION_DIR)
```
Where the `...` stand for all the other parametters that I... can't predict!
If you use a subfolder, for instance called `my_assets`, you could change the loading by
```python
image = load_image(..., base=SUBMISSION_DIR / "my_assets")
```

#### Manually

If you want to do that manually, the best way is to use the 
[`pathlib`](https://docs.python.org/3/library/pathlib.html#module-pathlib) module,
which is part of the standard python library, and has a simple interface for dealing with paths.

The first step is to get the path of your current directory, 
which is
```python
from pathlib import Path

current_file = Path(__file__)
current_directory = Path(__file__).parent
```

Then you can navigate up in the folder hierarchy by chaining `.parent.parent`..., 
and to go to a subfolder, you use the division operator `/`, so
if your structure is like this, 
```
root
├── assets
│   └── image.png
└── my_file.py
```
With your code is in `my_file.py` and you
want to access `image.png` reliably, you should use:j
```python
image = Path(__file__).parent / "assets" / "image.png"
```

### External modules

It is possible to use modules others than pygame in your submission.
However, please try to keep it as the minimum possible.
Keep in mind also that people may have trouble installing your requirements,
and then won't be able to play your entry.

In order to use external modules, you need to have a `requirements.txt` file
at the root of your submission. This file contains the name of the modules
that you need, one by line but without any version specified.

Users will be prompted to install them when running your entry (without just having the game crash).

### Submitting your entry

Before the deadline, make sure that your entry is runnable both via the showcase,
when you run the top level [`main.py`](main.py) and when you run it individually
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

Using relative imports means that if your folder looks like this:
```
yourname/
├── main.py
└── utils.py
```
And you want to import function `foo` from `utils.py` in your `main.py`,
you use
```python
from .utils import foo
```
Where the dot in front of `.utils` signifies that python needs to look inside the
same directory (here, the `yourname/` directory).

