import os.path

from .ninepatch import NinePatchImage
from .events_manager import *
from .utils import text

import pygame

asset_path = os.path.join(os.path.dirname(__file__), "assets")
image_path = os.path.join(asset_path, "images")
sounds_path = os.path.join(asset_path, "sounds")


class NinePatchedButton:
    def __init__(
        self,
        inactive_img_name,
        active_img_name=None,
        rect: pygame.Rect = None,
        zoom=1,
        msg="button",
        action=None,
    ):
        self.action = action
        self.inactive_img = NinePatchImage(inactive_img_name, inactive_img_name + ".npj")
        if active_img_name is not None:
            self.active_img = NinePatchImage(active_img_name, active_img_name + ".npj")
        else:
            self.active_img = None
        self.rect = rect
        self.msg = text(msg, (0, 0, 0), 25)
        if self.rect is None:
            self.rect = text(msg, (0, 0, 0), 25).get_rect().inflate(25, 25)
        if self.active_img is not None:
            self.active_img.generate_img(self.rect.w, self.rect.h)
        self.inactive_img.generate_img(self.rect.w, self.rect.h)
        self.img_rect = self.inactive_img.img_surf.get_rect(center=self.rect.center)
        self.img_rect = self.img_rect.inflate(self.rect.w * (zoom - 1), self.rect.h * (zoom - 1))
        self.click_delay = 0.5
        self.active = False
        self.last_clicked = time.time()
        self.clicks = 0
        self.zoom = zoom
        self.y_offset = 0
        self.push_timer = time.time()
        self.muted = False

    @staticmethod
    def get_click_count_name(clicks: int):
        names = [
            "single",
            "double",
            "triple",
            "quad",
            "penta",
            "hexa",
            "hepta",
            "octa",
            "nona",
            "deca",
        ]
        try:
            return names[clicks]
        except IndexError:
            return "multi"

    def update(self, events):
        if time.time() - self.last_clicked > self.click_delay:
            if self.clicks > 0:
                EventsManager.add_event(Event("released:" + str(self.clicks)))
            self.clicks = 0
        self.active = False
        if time.time() - self.push_timer > 0.1:
            if self.y_offset != 0:
                self.y_offset = 0
                if not self.muted:
                    pygame.mixer.music.load(os.path.join(sounds_path, "mouserelease1") + ".ogg")
                    pygame.mixer.music.play()

        mx, my = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    self.muted = not self.muted
        if self.img_rect.collidepoint(mx, my):
            self.active = True
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if not self.muted:
                            pygame.mixer.music.load(
                                os.path.join(sounds_path, "mouseclick1") + ".ogg"
                            )
                            pygame.mixer.music.play()
                        self.last_clicked = time.time()
                        self.clicks += 1
                        self.y_offset = -10
                        self.push_timer = time.time()
                        message = self.get_click_count_name(self.clicks - 1) + "-click!"
                        EventsManager.add_event(Event(message))
                        if self.action is not None:
                            self.action()

    def draw(self, display):
        # pygame.draw.rect(display, (0, 255, 0), self.img_rect, 10)
        if self.active and self.active_img is not None:
            self.active_img.draw(display, self.rect.move(0, self.y_offset).center, zoom=self.zoom)
        else:
            self.inactive_img.draw(display, self.rect.move(0, self.y_offset).center, zoom=self.zoom)

        display.blit(self.msg, self.msg.get_rect(center=self.rect.move(0, self.y_offset).center))
