import pygame
import json
from typing import Union


class NinePatchImage:
    def __init__(self, img, img_config):
        self.img = pygame.image.load(img)
        self.img_config = {}
        with open(img_config, "r") as f:
            self.img_config = json.loads(f.read())
        self.x = self.img_config["x"]
        self.y = self.img_config["y"]
        self.patches = {}
        self.img_surf: Union[pygame.Surface, None] = None
        self.get_patches()
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.generate_img(self.w, self.h)

    def update_image(self, w, h):
        self.generate_img(w, h)

    def get_patches(self):
        """
        image is divided up as follows
        a b c
        d e f
        g h i
        """
        x = self.x
        y = self.y
        w = self.img.get_width()
        h = self.img.get_height()
        # extracting corners in order a, c, i, g
        corner_rectangles = [(0, 0, x, y), (w - x, 0, x, y), (w - x, h - y, x, y), (0, h - y, x, y)]
        order = ("a", "c", "i", "g")
        for i in order:
            self.patches[i] = corner_rectangles[order.index(i)]
        # extracting edges
        self.patches["b"] = (x, 0, w - 2 * x, y)
        self.patches["h"] = (x, h - y, w - 2 * x, y)
        self.patches["d"] = (0, y, x, h - 2 * y)
        self.patches["f"] = (w - x, y, x, h - 2 * y)
        # extracting center
        self.patches["e"] = (x, y, w - 2 * x, h - 2 * y)

    def generate_img(self, width, height):
        self.img_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # placing all corners
        x = self.x
        y = self.y
        # corners in order a, c, i, g
        corner_start = [(0, 0), (width - x, 0), (width - x, height - y), (0, height - y)]
        order = ("a", "c", "i", "g")
        for i in range(len(corner_start)):
            rect = self.patches[order[i]]
            self.img_surf.blit(self.img, corner_start[i], rect)
        # placing edges
        # edges will be scaled along 1 direction
        # b and h along x axis
        # and d and f along y axis
        corner_start = [(x, 0), (x, height - y)]
        order = ("b", "h")
        for i in range(len(order)):
            rect = pygame.Rect(self.patches[order[i]])
            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            surf.blit(self.img, (0, 0), rect)
            surf = pygame.transform.scale(surf, (width - 2 * x, surf.get_height()))
            self.img_surf.blit(surf, corner_start[i])

        corner_start = [(0, y), (width - x, y)]
        order = ("d", "f")
        for i in range(len(order)):
            rect = pygame.Rect(self.patches[order[i]])
            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            surf.blit(self.img, (0, 0), rect)
            surf = pygame.transform.scale(surf, (surf.get_width(), abs(height - 2 * y)))
            self.img_surf.blit(surf, corner_start[i])

        # placing center
        rect = pygame.Rect(self.patches["e"])
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        surf.blit(self.img, (0, 0), rect)
        surf = pygame.transform.scale(surf, (abs(width - 2 * x), abs(height - 2 * y)))
        self.img_surf.blit(surf, (x, y))

    def draw(self, surf: pygame.Surface, pos, grid=False, zoom=1):
        if self.img_surf is None:
            return
        img = self.img_surf.copy()
        if zoom != 1:
            img = pygame.transform.scale(img, (img.get_width() * zoom, img.get_height() * zoom))
        img_rect = img.get_rect(center=pos)
        if grid:
            x = self.x
            y = self.y
            w = img_rect.w
            h = img_rect.h
            lines = [
                [(x, 0), (x, h)],
                [(w - x, 0), (w - x, h)],
                [(0, y), (w, y)],
                [(0, h - y), (w, h - y)],
            ]
            for i in lines:
                pygame.draw.line(img, (0, 0, 0), i[0], i[1], zoom * 3)
        surf.blit(img, img_rect)
