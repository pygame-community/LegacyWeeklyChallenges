import pygame
import random


class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.pos = pygame.Vector2(self.x, self.y)
		self.color = "black"
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
		self.alpha = 128

	def draw(self, win, player_pos):
		s = pygame.Surface((self.width, self.width))
		s.set_alpha(get_dist(self.pos, player_pos) + 50)
		s.fill((0, 0, 0))
		win.blit(s, self.pos)
		# pygame.draw.rect(win, self.color, (self.pos, (self.width, self.width)))


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)
	return grid


def draw(win, grid, player_pos):
	for row in grid:
		for spot in row:
			spot.draw(win, player_pos)


def get_dist(pos1, pos2):
	return pos1.distance_to(pos2)
