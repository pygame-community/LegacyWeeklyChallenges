import pygame as pg
from copy import copy

from pygame import key


class FogOfWar:

    def __init__(self, player_object: object, radius: int=250):

        # get player's class
        self.pl = player_object
        self.radius = 110  # -> radius of the player vision
        self.last_pl_pos = copy(self.pl.pos)
        self.fgs = 8

        # get screen's values
        self.screen = None
        self.w, self.h = (0, 0)

        self.initialized = False

        self.screen_values = []

    def init(self, screen: pg.Surface):
        if type(screen) is not pg.Surface:
            raise ValueError("The screen must be type : pygame.Surface")
        
        self.screen = screen
        self.w, self.h = screen.get_size()

        for row in range(0, self.h, self.fgs):
            new_row = []
            for col in range(0, self.w, self.fgs):
                new_row.append(FadeObj((col, row), (self.fgs, self.fgs)))  
            self.screen_values.append(new_row)

        self.initialized = True
        self.update_visible()

    def get_init(self):
        return self.initialized

    def update_visible(self):

        for row in self.screen_values:
            for obj in row:
                obj.update_visible(self.pl, self.radius)
        

    def update(self):

        if self.last_pl_pos != self.pl.pos:
            self.update_visible()
            self.last_pl_pos = copy(self.pl.pos)

        for row in self.screen_values:
            for col in row:
                col.update(self.screen)


class FadeObj:

    def __init__(self, pos, size):

        self.image = pg.Surface(size)
        self.pos = pg.Vector2(pos)
        self.visited = False

    def update(self, screen):
        screen.blit(self.image, self.pos)

    def update_visible(self, pl, r):
        d = self.pos.distance_to(pl.pos + pg.Vector2(20, 20))
        if d < r*1.3:
            self.visited = True
            self.image.set_alpha(150 + sum([10 if d > r * (i / 10) else 0 for i in range(0, 13, 2)]))
        else:
            if self.visited:
                self.image.set_alpha(240)
            else:
                self.image.set_alpha(255)