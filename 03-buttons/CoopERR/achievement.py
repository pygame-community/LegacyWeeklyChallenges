import pygame

class Achievement(pygame.sprite.Sprite):
    def __init__(self, position, images):
        super(Achievement, self).__init__()
        size = (78, 48)
        self.position = position
        self.rect = pygame.Rect(position, size)
        self.images = images
        self.index = 0
        self.image = images[self.index]

        self.animation_frames = len(self.images)
        self.current_frame = 0

    def update(self):
        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.current_frame]
