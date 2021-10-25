"""
This file provides objects that can be used to make up
a basic playground for the challenges.

This code is provided so that you can focus on implementing
your particle system, without needing to implement a game that
goes with it too.
Feel free to modify everything in this file to your liking.
"""

import time
from collections import deque
from colorsys import hsv_to_rgb
from functools import lru_cache
from operator import attrgetter
from random import gauss, choices, uniform

from functools import partial

import pygame

# noinspection PyPackages
from .utils import *
from .effects import *

# custom
import numpy as np

global EFFECTS
EFFECTS = EffectManager(limit=3000)
args = partial(SimpleParticle, (512, 384), (512, 384), 150, (225, 225, 225), 4, 0, -0.05, -0.1)
EFFECTS.add_task(args, 1, -1)
global effects_num
effects_num = pygame.font.SysFont("Bold", 40)

class State:
	def __init__(self, *initial_objects: "Object"):
		self.objects = set()
		self.objects_to_add = set()

		for obj in initial_objects:
			self.add(obj)

	def add(self, obj: "Object"):
		# We don't add objects immediately,
		# as it could invalidate iterations.
		self.objects_to_add.add(obj)
		obj.state = self
		return obj

	def logic(self):
		to_remove = set()
		for obj in self.objects:
			obj.logic()
			if not obj.alive:
				to_remove.add(obj)
		self.objects.difference_update(to_remove)
		self.objects.update(self.objects_to_add)
		self.objects_to_add.clear()
		EFFECTS.run()

	def draw(self, screen):
		EFFECTS.draw(screen)
		for obj in sorted(self.objects, key=attrgetter("Z")):
			obj.draw(screen)
		text = effects_num.render(str(EFFECTS.length), 1, (0, 125, 125))
		screen.blit(text, (0, 80))

	def handle_event(self, event):
		for obj in self.objects:
			if obj.handle_event(event):
				break


class Object:
	"""
	The base class for all objects of the game.

	Controls:
	 - [d] Show the hitboxes for debugging.
	"""

	# Controls the order of draw.
	# Objects are sorted according to Z before drawing.
	Z = 0

	# All the objects are considered circles,
	# Their hit-box is scaled by the given amount, to the advantage of the player.
	HIT_BOX_SCALE = 1.2

	def __init__(self, pos, vel, sprite: pygame.Surface):
		# The state is set when the object is added to a state.
		self.state: "State" = None
		self.center = pygame.Vector2(pos)
		self.vel = pygame.Vector2(vel)
		self.sprite = sprite
		self.rotation = 0.0  # for the sprite
		self.alive = True
		# Cache it every frame, as it was taking 10% (!!) of the processing power.
		self.rect = self.get_rect()

	def __str__(self):
		return f"<{self.__class__.__name__}(center={self.center}, vel={self.vel}, rotation={int(self.rotation)})>"

	@property
	def radius(self):
		"""All objects are considered circles of this radius for collisions."""
		# The 1.2 is to be nicer to the player
		return self.sprite.get_width() / 2 * self.HIT_BOX_SCALE

	def collide(self, other: "Object") -> bool:
		"""Whether two objects collide."""
		# The distance must be modified because everything wraps
		dx = (self.center.x - other.center.x) % SIZE[0]
		dx = min(dx, SIZE[0] - dx)
		dy = (self.center.y - other.center.y) % SIZE[1]
		dy = min(dy, SIZE[1] - dy)
		return (dx ** 2 + dy ** 2) <= (self.radius + other.radius) ** 2

	@property
	def rotated_sprite(self):
		# We round the rotation to the nearest integer so that
		# the cache has a chance to work. Otherwise there would
		# always be cache misses: it is very unlikely to have
		# to floats that are equal.
		return rotate_image(self.sprite, int(self.rotation))

	def get_rect(self):
		"""Compute the rectangle containing the object."""
		return self.rotated_sprite.get_rect(center=self.center)

	def handle_event(self, event):
		"""Override this method to make an object react to events.
		Returns True if the event was handled and should not be given to other objects."""
		return False

	def draw(self, screen):
		screen.blit(self.rotated_sprite, self.rect)

		# Goal: wrap around the screen.
		w, h = SIZE
		tl = 0, 0
		tr = w, 0
		br = w, h
		bl = 0, h

		shifts = []
		for a, b, offset in [
			(tl, tr, (0, h)),
			(bl, br, (0, -h)),
			(tl, bl, (w, 0)),
			(tr, br, (-w, 0)),
		]:
			# For each side [a,b] of the screen that it overlaps
			if self.rect.clipline(a, b):
				shifts.append(offset)
				# Draw the spaceship at the other edge too.
				screen.blit(
					self.rotated_sprite,
					self.rotated_sprite.get_rect(center=self.center + offset),
				)

		# Take care of the corners of the screen.
		# Here I assume that no object can touch two sides of the screen
		# at the same time. If so, the code wouldn't be correct, but still
		# produce the expected result -.-'
		assert len(shifts) <= 2
		if len(shifts) == 2:
			screen.blit(
				self.rotated_sprite,
				self.rotated_sprite.get_rect(center=self.center + shifts[0] + shifts[1]),
			)

		# To see the exact size of the hitboxes
		if pygame.key.get_pressed()[pygame.K_d]:
			pygame.draw.circle(screen, "red", self.center, self.radius, width=1)

	def logic(self, **kwargs):
		# self.vel = clamp_vector(self.vel, self.MAX_VEL)
		self.center += self.vel

		self.center.x %= SIZE[0]
		self.center.y %= SIZE[1]

		self.rect = self.get_rect()

TRAIL_EFFECT = load_image("fire", 2, base=SUBMISSION_DIR)
TRAIL_EFFECT_2 = load_image("fire_2", 3, base=SUBMISSION_DIR)

class Player(Object):
	Z = 10
	HIT_BOX_SCALE = 0.7  # harder to touch the player
	ACCELERATION = 0.7
	FRICTION = 0.9
	ROTATION_ACCELERATION = 3
	INITIAL_ROTATION = 90
	FIRE_COOLDOWN = 25  # frames
	TRAIL = TRAIL_EFFECT_2

	def __init__(self, pos, vel):
		super().__init__(pos, vel, load_image("player", 3))

		self.speed = 0
		self.fire_cooldown = -1

	'''
	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				self.fire()'''

	def logic(self):
		self.fire_cooldown -= 1

		# Motion
		pressed = pygame.key.get_pressed()
		mouse_btns = pygame.mouse.get_pressed()
		rotation_acc = pressed[pygame.K_a] - pressed[pygame.K_d]
		raw_acceleration = 0.5 * pressed[pygame.K_s] - pressed[pygame.K_w]
		if raw_acceleration < 0:
			trail_position = self.rect.center
			EFFECTS.particles.add(TrailParticle(position=trail_position, offset=(3, 3), speed=0, lifetime=30, center_position=True,
											transparent=True, alpha=125, random_rotation=True, surface=self.TRAIL))

		if pressed[pygame.K_SPACE] or mouse_btns[0]:
			self.fire()

		self.speed += raw_acceleration * self.ACCELERATION
		self.speed *= self.FRICTION  # friction

		# The min term makes it harder to turn at slow speed.
		self.rotation += rotation_acc * self.ROTATION_ACCELERATION * min(1.0, 0.4 + abs(self.speed))
		center = self.rect.center
		#trail_position = ((center[0]+22)*self.rotation, (center[1]+22)*self.rotation)
		#player.center + Vector2(35,0).rotate(90-player.rotation)
		#print(self.rotation)

		self.vel.from_polar((self.speed, self.INITIAL_ROTATION - self.rotation))

		super().logic()

	def fire(self):
		if self.fire_cooldown >= 0:
			return

		self.fire_cooldown = self.FIRE_COOLDOWN
		rot = np.radians(self.rotation)
		cen = self.center
		for off in ((22, -22, 11, -11)):
			pos = (cen[0]+np.cos(-rot)*off, cen[1]+np.sin(-rot)*off)
			bullet = Bullet(pos, 270 - self.rotation)
			self.state.add(bullet)

		# You can add particles here too.
		...

	def on_asteroid_collision(self, asteroid: "Asteroid"):
		# For simplicity I just explode the asteroid, but depending on what you aim for,
		# it might be better to just loose some life or even reset the game...
		asteroid.explode(Bullet(self.center, self.rotation))

		# Add particles here (and maybe damage the ship or something...)
		...

class Bullet(Object):
	Z = 1
	SPEED = 10
	TIME_TO_LIVE = 60 * 2
	TRAIL = TRAIL_EFFECT

	def __init__(self, pos, angle):
		super().__init__(pos, from_polar(self.SPEED, angle), load_image("bullet", 2))
		self.rotation = 90 - angle
		self.time_to_live = self.TIME_TO_LIVE

	def logic(self, **kwargs):
		super().logic(**kwargs)
		EFFECTS.particles.add(SimpleParticle(position=self.rect.center, offset=(2, 2), lifetime=5, 
									color=(245, 125, 0), size=10, dark_over_time=-20, change_size_over_time=-1))
		self.time_to_live -= 1

		if self.time_to_live <= 0:
			self.alive = False
			EFFECTS.particles.add(CrashParticle(position=self.rect.center, pieces=random.randint(5, 10), lifetime=80, 
												speed=random.randint(10, 20), surface=TRAIL_EFFECT))

		# Maybe some trail particles here ? You can put particles EVERYWHERE. Really.
		...


class Asteroid(Object):
	AVG_SPEED = 1
	EXPLOSION_SPEED_BOOST = 1.8

	def __init__(self, pos, vel, size=4, color=None):
		assert 1 <= size <= 4
		self.level = size
		# We copy to change the color
		self.color = color or self.random_color()

		super().__init__(pos, vel, self.colored_image(size, self.color))

	@staticmethod
	@lru_cache(100)
	def colored_image(size, color):
		sprite = load_image(f"asteroid-{16*2**size}").copy()
		sprite.fill(color, special_flags=pygame.BLEND_RGB_MULT)
		return sprite

	def logic(self):
		super().logic()

		for obj in self.state.objects:
			if not obj.alive:
				continue

			if isinstance(obj, Bullet):
				# Detect if the bullet and asteroid collide.
				if self.collide(obj):
					self.explode(obj)
					break
			elif isinstance(obj, Player):
				if self.collide(obj):
					obj.on_asteroid_collision(self)

	def explode(self, bullet):
		EFFECTS.particles.add(CrashParticle(position=self.rect.center, pieces=random.randint(10, 20), lifetime=80, 
											   speed=random.randint(10, 20), surface=self.sprite))
		#EFFECTS.particles.add(CrashParticle(position=self.rect.center, pieces=random.randint(10, 20), lifetime=80, 
											   #speed=random.randint(10, 20), surface=self.sprite))
		bullet.alive = False
		self.alive = False
		if self.level > 1:
			# We spawn two smaller asteroids in the direction perpendicular to the collision.
			perp_velocity = pygame.Vector2(bullet.vel.y, -bullet.vel.x)
			perp_velocity.scale_to_length(self.vel.length() * self.EXPLOSION_SPEED_BOOST)
			for mult in (-1, 1):
				self.state.add(
					Asteroid(self.center, perp_velocity * mult, self.level - 1, self.color)
				)

		# You'll add particles here for sure ;)
		...

	def random_color(self):
		r, g, b = hsv_to_rgb(uniform(0, 1), 0.8, 0.8)
		return int(r * 255), int(g * 255), int(b * 255)

	@classmethod
	def generate_many(cls, nb=10):
		"""Return a set of nb Asteroids randomly generated."""
		objects = set()
		for _ in range(nb):
			angle = uniform(0, 360)
			distance_from_center = gauss(SIZE[1] / 2, SIZE[1] / 12)
			pos = SCREEN.center + from_polar(distance_from_center, angle)
			vel = from_polar(gauss(cls.AVG_SPEED, cls.AVG_SPEED / 6), gauss(180 + angle, 30))
			size = choices([1, 2, 3, 4], [4, 3, 2, 1])[0]
			objects.add(cls(pos, vel, size))

		return objects


class FpsCounter(Object):
	"""
	A wrapper around pygame.time.Clock that shows the FPS on screen.

	Controls:
	 - [F] Toggles the display of FPS
	 - [U] Toggles the capping of FPS
	"""

	Z = 1000
	REMEMBER = 30

	def __init__(self, fps):
		self.hidden = False
		self.cap_fps = True
		self.target_fps = fps
		self.clock = pygame.time.Clock()
		self.frame_starts = deque([time.time()], maxlen=self.REMEMBER)

		dummy_surface = pygame.Surface((1, 1))
		super().__init__((4, 8), (0, 0), dummy_surface)

	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				self.hidden = not self.hidden
			elif event.key == pygame.K_u:
				self.cap_fps = not self.cap_fps

	def logic(self, **kwargs):
		# Passing 0 to tick() removes the cap on FPS.
		self.clock.tick(self.target_fps * self.cap_fps)

		self.frame_starts.append(time.time())

	@property
	def current_fps(self):
		if len(self.frame_starts) <= 1:
			return 0
		seconds = self.frame_starts[-1] - self.frame_starts[0]
		return (len(self.frame_starts) - 1) / seconds

	def draw(self, screen):
		if self.hidden:
			return

		color = "#89C4F4"
		t = text(f"FPS: {int(self.current_fps)}", color)
		screen.blit(t, self.center)

			
