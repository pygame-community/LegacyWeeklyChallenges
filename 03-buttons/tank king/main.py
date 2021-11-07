import math
import os.path
import random
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
__author__ = "CozyFractal#0042"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    # "Adventurous",
]

import pygame

if not pygame.get_init():
    pygame.init()

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *
from .buttons import NinePatchedButton
from .events_manager import *

BACKGROUND = 0x0F1012


class Text:
    size = 50

    def __init__(self, msg):
        self.x = SIZE[0] // 2 + 250
        self.y = SIZE[1] // 2 + 150
        self.original_y = self.y
        self.msg = msg
        self.text = text(msg, (255, 255, 255), Text.size)
        self.alpha = 255

    def update(self):
        self.y -= 1
        self.alpha -= 2
        if self.alpha < 10:
            self.alpha = 10
        self.text.set_alpha(self.alpha)

    def draw(self, display: pygame.Surface):
        display.blit(self.text, self.text.get_rect(center=(self.x, self.y)))


text_list: list[Text] = []


def mainloop():
    pygame.init()
    asset_path = os.path.join(os.path.dirname(__file__), 'assets')
    image_path = os.path.join(asset_path, 'images')
    print(image_path)

    modes = ['retry', 'start', 'game']
    current_mode = modes[1]

    rate = 0.01

    def start():
        nonlocal modes, current_mode, target_number, current_number, timer, lives, score, rate
        target_number = random.randint(1, 10) * 10
        current_number = target_number - random.randint(1, 9)
        timer = 100
        lives = 5
        score = 0
        rate = 0.1
        current_mode = modes[-1]
        EventsManager.clear_all_events()
        text_list.clear()

    button1 = NinePatchedButton(os.path.join(image_path, 'button.9.png'),
                                os.path.join(image_path, 'button_selected.9.png'),
                                rect=pygame.Rect(SIZE[0] // 2 - 100, SIZE[1] // 2, 200, 100), zoom=1, msg='Retry', action=start)
    button2 = NinePatchedButton(os.path.join(image_path, 'button2.9.png'),
                                os.path.join(image_path, 'button4.9.png'),
                                rect=pygame.Rect(100, SIZE[1] // 2, 200, 100), zoom=1, msg='Click me!')
    button3 = NinePatchedButton(os.path.join(image_path, 'button.9.png'),
                                os.path.join(image_path, 'button_selected.9.png'),
                                rect=pygame.Rect(SIZE[0] // 2 - 100, SIZE[1] // 2, 200, 100), zoom=1, msg='Start', action=start)
    # current_button = random.choice([button1, button2])
    clock = pygame.time.Clock()

    target_number = random.randint(1, 10) * 10
    current_number = target_number - random.randint(1, 9)
    timer = 100
    lives = 5
    score = 0

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
        if current_mode == 'game':
            button2.update(events)
            for i in range(len(EventsManager.get_all_events())):
                name = EventsManager.get_next_event().name
                if current_mode == 'game':
                    if 'released' in name:
                        if int(name.split(':')[1]) == target_number - current_number:
                            target_number = random.randint(1, 10) * 10
                            current_number = target_number - random.randint(1, 9)
                            score += 10
                            timer = 100
                            rate += 0.02
                            if rate > 0.6:
                                rate = 0.6
                        continue
                    for j in text_list:
                        j.y -= Text.size
                    text_list.append(Text(name))
        elif current_mode == 'retry':
            button1.update(events)
        elif current_mode == 'start':
            button3.update(events)

        screen.fill(BACKGROUND)
        if current_mode == 'game':
            button2.draw(screen)
            for i in text_list:
                i.update()
                i.draw(screen)
                if i.alpha <= 10:
                    text_list.remove(i)
                    del i
            screen.blit(text('Lives: ' + str(lives), (0, 150, 255), 50), (50, 50))
            screen.blit(text('Score: ' + str(score), (0, 150, 255), 50), (50, 125))
            t = text(str(current_number), (255, 255, 255), 150)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, 150)))
            timer -= rate
            if timer <= 0:
                lives -= 1
                timer = 100
                if lives <= 0:
                    current_mode = 'retry'
            pygame.draw.line(screen, (0, 255, 0), (50, 210), (50 + timer * 8, 210), 10)
        elif current_mode == 'retry':
            button1.draw(screen)
            t = text('Score: ' + str(score), (255, 255, 255), 75)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, 250)))

        elif current_mode == 'start':
            button3.draw(screen)
            t = text('NumClic!', (255, 255, 255), 75)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, 250)))
            t = text('Keep clicking to reach the nearest greatest integer', (255, 255, 255), 25)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, SIZE[1] - 150)))
            t = text('Press m to mute/unmute', (255, 255, 255), 25)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, SIZE[1] - 100)))

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
