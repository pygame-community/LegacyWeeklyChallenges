import sys, os
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
__author__ = 'await ctx.send("Miku")#7006'  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
	# "Adventurous",
]

import pygame, random

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *
from .utils import random_color
from .ui import *

BACKGROUND = 0x0F1012
BOT = False
#SIZE = (1024, 768)

def generate_button(sounds, action):
	pos = (random.randint(0, 950), random.randint(0, 690))
	rect = pygame.Rect(pos[0], pos[1], random.randint(20, 1024-pos[0]), random.randint(20, 768-pos[1]))
	text = None
	if rect.w > 30 and rect.h > 30:
		txt = random.choice(("Noob", "Press me!", "Cringe", "Lol", "You're still trying?", "Boring"))
		text = pygame.font.SysFont("Bold", random.randint(30, 80)).render(txt, 1, random_color())
	colors = [random_color() for _ in range(3)]
	bold = [random_color(), random.randint(0, 5)]
	button = SimpleButton(rect=rect, bold=bold, colors=colors, text=text, click=random.randint(1, 3), sounds=sounds, action=action)
	return(button)


def run_something(arg):
	global buttons, score, time
	if arg == "play_button":
		global part
		part = 1
		pygame.mixer.music.play(-1)
		btn = generate_button(sounds, (run_something, "click_button"))
		buttons = [btn]
	if arg == "click_button":
		btn = generate_button(sounds, (run_something, "click_button"))
		buttons = [btn]
		score += 1
		time += 30

def mainloop():
	pygame.init()
	global score, time, sounds, buttons, part 
	part = 0
	score, time = 0, 600
	sounds = (pygame.mixer.Sound("btn_sound.mp3"), pygame.mixer.Sound("btn_sound1.mp3"))
	music = pygame.mixer.music.load("cute_music.mp3")
	buttons = [
		SimpleButton(pygame.Rect(0, 0, 300, 120),
					 text=pygame.font.SysFont("Bold", 80).render("Button!", 1, (255, 255, 255)),
					 centered=(512, 768//2), sounds=sounds, action=(run_something, "play_button"),
					 )
		# Define more buttons here when you have one working!
		# With different styles, behavior, or whatever cool stuff you made :D
	]

	clock = pygame.time.Clock()
	while True:
		screen, events = yield
		for event in events:
			if event.type == pygame.QUIT:
				return

		mouse_btn = pygame.mouse.get_pressed()
		mouse_pos = pygame.mouse.get_pos()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			print(f"You're score: {score}")
			return
		if part:
			time -= 1
			if time <= 0:
				print(f"You're score: {score}")
				return
			if BOT:
				center = buttons[0].rect.center
				pygame.mouse.set_pos(center)
				if time % 2 == 0:
					mouse_btn = (True, False, False)

		for button in buttons:
			button.logic(m_btn=mouse_btn, m_pos=mouse_pos)

		screen.fill(BACKGROUND)
		for button in buttons:
			button.draw(screen)
		if part:
			score_txt = text(f"Score: {score}", (255, 255, 255), size=35)
			time_txt = text(f"Time left: {round(time/60, 1)}", (255, 255, 255), size=35)
			screen.blit(score_txt, (0, 0))
			screen.blit(time_txt, (0, 35))

		clock.tick(60)


if __name__ == "__main__":
	wclib.run(mainloop())
