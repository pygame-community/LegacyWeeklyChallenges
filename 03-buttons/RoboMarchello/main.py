import sys
from pathlib import Path

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "03-buttons." + Path(__file__).absolute().parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "RoboMarchello#0570"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    "Adventurous",
]

import pygame, random

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

BACKGROUND = 0x0F2F2F2


def SplitSheet(surface, cellSize):
    surfSize = surface.get_size()
    cellsx = surfSize[0] // cellSize[0]
    cellsy = surfSize[1] // cellSize[1]

    cellSurfs = []

    for celly in range(cellsy):
        for cellx in range(cellsx):
            cellSurf = pygame.Surface((cellSize[0], cellSize[1]), pygame.SRCALPHA)
            cellSurf.blit(surface, (-cellx * cellSize[0], -celly * cellSize[1]))
            cellSurfs.append(cellSurf)

    return cellSurfs


# This is a suggestion of the interface of the button class.
# There are many other ways to do it, but I strongly suggest to
# at least use a class, so that it is more reusable.
class Button:
    def __init__(
        self,
        position,
        size,
        content: str,
        bgColor,
        nPath,
        cellSize,
        funcs,
        icon: pygame.Surface = None,
    ):  # Just an example!
        self.position = position
        self.size = size
        self.content = content

        self.bgColor = bgColor
        self.rect = pygame.Rect(self.position, self.size)

        # hover
        self.hovered = False
        self.hoverSurf = pygame.Surface(size, pygame.SRCALPHA)
        self.hoverSurf.set_colorkey((255, 255, 255))
        self.mousePos = (0, 0)

        # icon
        self.icon = None
        if icon != None:
            self.icon = pygame.transform.scale(icon, (32, 32))
            self.icon.set_colorkey((255, 0, 0))
            self.iconRect = icon.get_rect()

        #
        self.clickTimer = 0
        self.clicked = 0
        self.pressed = False

        self.functions = funcs

        # nine path
        self.nPath = nPath
        self.cellSize = cellSize
        self.tiles = [self.size[0] // cellSize[0], self.size[1] // cellSize[1]]

    def handle_event(self, event: pygame.event.Event):
        # Use this to update the state of the button according to user inputs.
        # It is usually a good idea to have this separated from the rest according
        # to the principle of separation of concerns.
        if event.type == pygame.MOUSEMOTION:
            self.mousePos = event.pos
            if self.rect.collidepoint(self.mousePos):
                self.hovered = True
            else:
                self.hovered = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hovered:
                    self.clickTimer = 15
                    self.clicked += 1
                    self.pressed = True

                    # self.ripple.append(ripple(self.mousePos,self.bgColor))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed = False

    def draw(self, screen: pygame.Surface):
        # Use this to draw the button on the screen
        # As a placeholder, I draw its content, but it may be more complex
        # when you do it. Maybe you use images, maybe likely some background,
        # maybe some border and even shadows?
        self.on_hover()

        if self.pressed == True:
            if self.rect.y < self.position[1] + 4:
                self.rect.y += 2
        elif self.rect.y > self.position[1] - 4:
            self.rect.y -= 2

        self.nine_path(screen)

        if self.clicked > 0:
            if self.clickTimer > 0:
                self.clickTimer -= 1
            else:
                if len(self.functions) >= self.clicked:
                    self.functions[self.clicked - 1]()
                else:
                    self.functions[-1]()
                self.clicked = 0

        # blit text
        t = text(self.content, "orange")
        t_rect = t.get_rect(center=self.rect.center)  # center text rect
        screen.blit(t, t_rect.topleft)  # blit text

        # blit icon
        if self.icon != None:
            self.iconRect.center = self.rect.center
            self.iconRect.right = t_rect.left - 7
            screen.blit(self.icon, self.iconRect.topleft)

    def nine_path(self, screen):
        # nine path. The code is really ugly:(
        # draw corners
        corner_x = self.rect.width - 15
        corner_y = self.rect.height - 15
        self.hoverSurf.blit(self.nPath[0], (0, 0))
        self.hoverSurf.blit(self.nPath[2], [corner_x, 0])
        self.hoverSurf.blit(self.nPath[6], [0, corner_y])
        self.hoverSurf.blit(self.nPath[8], [corner_x, corner_y])
        screen.blit(self.hoverSurf, self.rect.topleft)

        transWidth = self.rect.width - self.tiles[0] * 15
        transHeight = self.rect.height - self.tiles[1] * 15

        transx = pygame.transform.scale(self.nPath[4], (transWidth, self.cellSize[1]))
        transy = pygame.transform.scale(self.nPath[4], (self.cellSize[0], transHeight))
        for tilex in range(self.tiles[0] - 2):
            tileXPos = tilex * 15
            for tiley in range(self.tiles[1] - 2):
                tileYPos = tiley * 15 + 15
                screen.blit(self.nPath[4], (tileXPos + self.rect.x + 15, tileYPos + self.rect.y))
                screen.blit(self.nPath[3], (self.rect.left, self.rect.top + tileYPos))
                screen.blit(self.nPath[5], (self.rect.right - 15, self.rect.top + tileYPos))

                screen.blit(
                    transx, [self.rect.left + self.tiles[0] * 15 - 15, self.rect.top + tileYPos]
                )

            screen.blit(self.nPath[1], (self.rect.left + tileXPos + 15, self.rect.top))
            screen.blit(self.nPath[7], (self.rect.left + tileXPos + 15, self.rect.bottom - 15))

            # draw transformed tiles inside a button
            screen.blit(
                transy, [self.rect.left + tileXPos + 15, self.rect.top + self.tiles[1] * 15 - 15]
            )

        screen.blit(
            pygame.transform.scale(self.nPath[4], (transWidth, transHeight)),
            [self.rect.left + self.tiles[0] * 15 - 15, self.rect.top + self.tiles[1] * 15 - 15],
        )

        # draw transformed borders
        transBorderx = self.rect.left + self.tiles[0] * 15 - 15
        transBordery = self.rect.left + self.tiles[0] * 15 - 15
        screen.blit(
            pygame.transform.scale(self.nPath[3], (self.cellSize[0], transHeight)),
            [self.rect.left, self.rect.top + self.tiles[1] * 15 - 15],
        )
        screen.blit(
            pygame.transform.scale(self.nPath[5], (self.cellSize[0], transHeight)),
            [self.rect.right - 15, self.rect.top + self.tiles[1] * 15 - 15],
        )
        screen.blit(
            pygame.transform.scale(self.nPath[1], (transWidth, self.cellSize[1])),
            [self.rect.left + self.tiles[0] * 15 - 15, self.rect.top],
        )
        screen.blit(
            pygame.transform.scale(self.nPath[7], (transWidth, self.cellSize[1])),
            [self.rect.left + self.tiles[0] * 15 - 15, self.rect.bottom - 15],
        )

    def on_hover(self):
        pass


class ripple:
    def __init__(self, pos, color, ripps):
        self.radius = 0

        self.pos = pos

        self.color = [255 - color[0], 255 - color[1], 255 - color[2]]
        self.smoothStart = 0

        for col in self.color:
            self.color[self.color.index(col)] = (
                color[self.color.index(col)] + int(col * 0.2) * ripps
            )

    def draw(self, screen):
        self.radius += 0.2
        self.smoothStart = self.radius ** 2
        pygame.draw.circle(screen, self.color, self.pos, self.smoothStart, width=20)


class circleButton(Button):
    def __init__(
        self,
        position,
        size,
        content: str,
        bgColor,
        nPath,
        cellSize,
        funcs,
        icon: pygame.Surface = None,
    ):
        super().__init__(position, size, content, bgColor, nPath, cellSize, funcs, icon)

        self.hoverTime = 0
        self.hoverRadius = 0

        self.ripples = []
        self.rippleColor = -1

    def on_hover(self):
        self.hoverSurf.fill((0, 0, 0, 0))
        if self.hovered == True:
            if self.hoverRadius < self.size[0] + 200:
                self.hoverTime += 0.2

        else:
            if self.hoverRadius > 0:
                if self.hoverTime > 0:
                    self.hoverTime -= 0.2

        self.hoverRadius = self.hoverTime ** 3 + 2
        pygame.draw.circle(
            self.hoverSurf,
            self.bgColor,
            [self.mousePos[0] - self.position[0], self.mousePos[1] - self.position[1]],
            self.hoverRadius,
        )

        for ripp in self.ripples:
            ripp.draw(self.hoverSurf)
            if ripp.smoothStart > self.hoverRadius:
                self.ripples.pop(self.ripples.index(ripp))

    def handle_event(self, event: pygame.event.Event):
        # Use this to update the state of the button according to user inputs.
        # It is usually a good idea to have this separated from the rest according
        # to the principle of separation of concerns.
        if event.type == pygame.MOUSEMOTION:
            self.mousePos = event.pos
            if self.rect.collidepoint(self.mousePos):
                self.hovered = True
            else:
                self.hovered = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hovered:
                    self.clickTimer = 15
                    self.clicked += 1
                    self.pressed = True

                    self.ripples.append(
                        ripple(
                            [self.mousePos[0] - 16, self.mousePos[1] - 16],
                            self.bgColor,
                            self.rippleColor,
                        )
                    )
                    if self.rippleColor < 0:
                        self.rippleColor = 1
                    else:
                        self.rippleColor = -1

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed = False


class perlinButton(Button):
    def __init__(
        self,
        position,
        size,
        content: str,
        bgColor,
        nPath,
        cellSize,
        funcs,
        icon: pygame.Surface = None,
    ):
        super().__init__(position, size, content, bgColor, nPath, cellSize, funcs, icon)

        self.perlinNoise = pygame.image.load(
            "03-buttons/RoboMarchello/noise_transition.png"
        ).convert()
        self.crntCol = 100

    def on_hover(self):
        self.hoverSurf.fill((0, 0, 0, 0))
        if self.hovered == True:
            if self.crntCol < 200:
                self.crntCol += 2
        else:
            if self.crntCol > 100:
                self.crntCol -= 1.75

        mask = pygame.mask.from_threshold(
            self.perlinNoise, (0, 0, 0), (self.crntCol, self.crntCol, self.crntCol, 255)
        )
        maskSurf = mask.to_surface()
        maskSurf.set_colorkey((255, 255, 255))

        inv = pygame.Surface(maskSurf.get_rect().size)
        inv.fill(self.bgColor)
        inv.blit(maskSurf, (0, 0))
        inv.set_colorkey((0, 0, 0))

        self.hoverSurf.blit(inv, (0, 0))


eventText = "No events."


def func1():
    global eventText
    eventText = "Button was clicked!"


def func2():
    global eventText
    eventText = "Button was double clicked!"


def func3():
    global eventText
    eventText = "Triple click!"


def mainloop():
    pygame.init()

    buttons = [
        circleButton(
            (20, 20),
            (200, 100),
            "Click me!",
            (240, 138, 93),
            SplitSheet(
                pygame.image.load("03-buttons/RoboMarchello/nine_path.png").convert_alpha(),
                (15, 15),
            ),
            (15, 15),
            [func1, func2, func3],
            icon=pygame.image.load("03-buttons/RoboMarchello/icon.png").convert(),
        ),
        perlinButton(
            (20, 150),
            (200, 100),
            "Click me!",
            (184, 59, 94),
            SplitSheet(
                pygame.image.load("03-buttons/RoboMarchello/nine_path.png").convert_alpha(),
                (15, 15),
            ),
            (15, 15),
            [func1, func2, func3],
        ),
        Button(
            (250, 20),
            (100, 230),
            "Play!",
            (247, 228, 77),
            SplitSheet(
                pygame.image.load("03-buttons/RoboMarchello/grass_ninepath.png").convert_alpha(),
                (15, 15),
            ),
            (15, 15),
            [func1, func2, func3],
        ),
        # Define more buttons here when you have one working!
        # With different styles, behavior, or whatever cool stuff you made :D
    ]

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            for button in buttons:
                button.handle_event(event)

        screen.fill(BACKGROUND)
        screen.blit(text(eventText, "red"), (700, 15))
        for button in buttons:
            button.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
