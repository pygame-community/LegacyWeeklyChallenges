import pygame
from .utils import *
import os

class Achievement(pygame.sprite.Sprite):
    def __init__(self, position, path):
        super(Achievement, self).__init__()
        size = (78, 48)
        self.position = position
        self.rect = pygame.Rect(position, size)
        self.images = self.load_frames(path)
        self.index = 0
        self.image = self.images[self.index]
        self.sprites = pygame.sprite.Group(self)

        self.animation_frames = len(self.images)
        self.step = -1
        self.play = False

    def update(self):
        SPEED = 2
        self.step += 1
        if self.step >= SPEED:
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]
            self.step = 0

        if self.index >= self.animation_frames - 1:
            self.play = False
            self.index = 0

    def load_frames(self, images):
        path = images
        frames = []

        for file_name in os.listdir(path):
            image = load_image(file_name, scale=3, base=path)
            frames.append(image)
        
        return frames