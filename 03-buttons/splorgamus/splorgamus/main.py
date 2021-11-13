import sys
from pathlib import Path

try:
    import wclib
except ImportError:

    ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

__package__ = "03-buttons." + Path(__file__).absolute().parent.name


__author__ = "splorgamus#0257"
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    # "Adventurous",
]

import pygame

pygame.init()
from .utils import *

# File paths
current_directory = Path(__file__).parent

# Settings for the window
capt = pygame.display.set_caption("Button showcase")
BACKGROUND = (173, 216, 255)

# Images
start_img = pygame.image.load(f"{current_directory}/assets/start_img.png")
start_img = pygame.transform.scale(start_img, (50, 50))

exit_img = pygame.image.load(f"{current_directory}/assets/exit_img.png")
exit_img = pygame.transform.scale(exit_img, (50, 50))

# Text
title_font = pygame.font.Font(None, 100)
title_text = title_font.render("Splorgamus' buttons", True, (0, 0, 0))


class Button:
    def __init__(
        self,
        text,
        colour,
        darker_colour,
        rect,
        icon,
        is_double_click,
        border_thickness=2,
        text_colour=(0, 0, 0),
        border_colour=(0, 0, 0),
        button_x=120,
        button_y=35,
        confirm_txt="Are you sure?",
    ):
        # Button properties
        self.text_colour = text_colour
        self.colour = colour
        self.darker_colour = darker_colour
        self.original_colour = self.colour
        self.border_colour = border_colour
        self.border_thickness = border_thickness
        self.icon = icon

        # Button rectangles
        self.inside = pygame.Rect(rect)
        self.border = pygame.Rect(rect)

        self.original_x = rect[0]
        self.original_y = rect[1]

        self.button_x = button_x
        self.button_y = button_y

        # Text
        self.font = pygame.font.Font(None, 50)
        self.scaled_font = pygame.font.Font(None, 60)
        self.text = self.font.render(text, True, text_colour)
        self.scaled_text = self.scaled_font.render(text, True, text_colour)
        self.text_rect = self.text.get_rect(center=self.inside.center)
        self.scaled_text_rect = self.scaled_text.get_rect(center=self.inside.center)

        self.confirm_text = self.font.render(confirm_txt, True, text_colour)
        self.confirm_rect = self.confirm_text.get_rect(center=self.inside.center)

        # Button clicks
        self.clicked = False
        self.doubleClick = False
        self.clicks = 0
        self.timer = 0
        self.is_double_click = is_double_click  # To check if the button is a double click

    # Function for the animation when the first button is clicked
    def single_click(self):
        if self.clicked:

            self.inside.y -= 5
            self.border.y -= 5

            if self.inside.bottom < 0:
                self.inside.y = self.original_y
                self.border.y = self.original_y

                self.clicked = False

    # Function for button double click
    def double_click(self, screen: pygame.Surface):
        if self.doubleClick:

            screen.blit(self.confirm_text, (self.confirm_rect))

            self.timer += 0.05

            if self.timer >= 1:
                self.timer = 0
                self.doubleClick = False
                self.clicks = 0

    # Update() function for button
    def update(self, screen: pygame.Surface):
        self.mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.colour, self.inside)
        pygame.draw.rect(screen, self.border_colour, self.border, self.border_thickness)

        # To change the colour if you hover your cursor over the button
        if self.inside.collidepoint(self.mouse_pos) and not self.clicked and not self.doubleClick:
            self.colour = self.darker_colour
            screen.blit(self.scaled_text, (self.scaled_text_rect))

        # Setting the button colour to normal if the cursor isn't over the button
        elif not self.doubleClick:
            self.colour = self.original_colour
            self.text_rect = self.text.get_rect(center=self.inside.center)
            screen.blit(self.text, (self.text_rect))
            screen.blit(
                self.icon, (self.inside.right - self.button_x, self.inside.y + self.button_y)
            )

        # Blitting the button icons
        if self.inside.collidepoint(self.mouse_pos) and not self.clicked and not self.doubleClick:
            screen.blit(
                self.icon, (self.inside.right - self.button_x, self.inside.y + self.button_y)
            )


# Button objects
button1 = Button("Start", (100, 255, 100), (0, 255, 0), [300, 300, 350, 125], start_img, 0)
button2 = Button("Quit", (255, 100, 100), (255, 50, 50), [300, 450, 350, 125], exit_img, 1)


def mainloop():
    pygame.init()

    buttons = [button1, button2]

    clock = pygame.time.Clock()

    run = True
    while run:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            # If the button is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:

                for button in buttons:
                    # Checking for button being clicked
                    if button.inside.collidepoint(button.mouse_pos) and button.is_double_click == 0:
                        button.clicked = True

                    # Checking for button being double clicked
                    if button.inside.collidepoint(button.mouse_pos) and button.is_double_click == 1:
                        button.doubleClick = True
                        button.clicks += 1

                        # Ending program if second button double clicked
                        if button.doubleClick and button.timer < 1 and button.clicks == 2:
                            return  # I've also tried putting run = False but it still doesn't work in the showcase

        screen.fill(BACKGROUND)
        screen.blit(title_text, (150, 100))

        for button in buttons:
            button.update(screen)

            # Running function if button is clicked
            if button.clicked:
                button.single_click()

            # Running function if button is double clicked
            if button.doubleClick:
                button.double_click(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
