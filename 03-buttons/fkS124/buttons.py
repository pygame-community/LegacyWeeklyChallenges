import pygame as pg
from pygame.locals import *
from .utils import *


class Button:
    def __init__(
        self,
        pos: pg.Vector2,
        size: tuple[int, int],
        icon: pg.Surface = None,  # shown instead of a background
        icon_hover: pg.Surface = None,  # shown instead of a background when mouse hovers the button
        on_click=None,  # func that will be executed when button clicked : form -> exemple_func (according to def exemple_func())
        on_click_args: tuple = None,  # arguments that will be passed inside the function executed
        on_mouse_hover=None,  # same from "on_click" but when the mouse hovers the button
        on_mouse_hover_args: tuple = None,  # same from "on_click" but when the mouse hovers the button
        font: pg.font.Font = None,
        text: str = None,  # text displayed on the button
        text_color: tuple = None,  # default text color
        text_color_hover: tuple = None,  # text color when mouse hovers button
        bg_color: tuple = (0, 0, 0),  # default background color
        bg_color_hover: tuple = (0, 0, 0),  # background color when hoverd by the mouse
        double_click: bool = False,  # allow double click
        db_click_func=None,  # func played when double click
        db_click_f_args: tuple = None,  # args of func double click
        border_radius: int = 0,  # border radius if needed
        shadow_on_click: int = 0,  # feels like the button is really pressed
        execute="down",  # can either be "down" or "up" -> decides when it does execute the func (on mousebuttondown or mousebuttonup)
    ):

        self.rect = pg.Rect(*pos, *size)

        # ------------- SETTINGS ---------------------
        self.bg_color = bg_color
        self.bg_color_hover = bg_color_hover

        self.has_text = text is not None
        self.execution = execute

        self.border_radius = border_radius
        self.shadow_on_click = shadow_on_click

        # ------------- TEXT -------------------------
        self.text = text
        self.text_color = text_color
        self.text_color_hover = text_color_hover

        if self.has_text and font is None:
            return ValueError("No font have been initialized.")

        self.font = font
        self.rendered_text = self.font.render(self.text, True, self.text_color)
        self.rendered_hover_text = self.font.render(self.text, True, self.text_color_hover)

        # ------------------ ICONS -------------------
        self.has_icon = icon is not None and icon_hover is not None
        if self.has_icon:
            self.icon = pg.transform.scale(icon, size)  # TODO : Replace with 9patch thing
            self.icon_hover = pg.transform.scale(icon, size)
            self.rect = self.icon.get_rect(topleft=pos)

        # ------------ FUNCTIONS ---------------------
        self.functions = {
            "on_click": on_click,
            "on_mouse_hover": on_mouse_hover,
            "on_db_click": db_click_func,
        }
        self.args = {
            "on_click": on_click_args,
            "on_mouse_hover": on_mouse_hover_args,
            "on_db_click": db_click_f_args,
        }

        # ----------------- STATES -------------------
        self.hovering = False
        self.clicking = False

        # ------------- DOUBLE CLICK -----------------
        self.double_click = double_click
        self.waiting_for_second_click = False
        self.last_click = 0

    def decide_state(self, click_pos):
        if self.rect.collidepoint(click_pos):

            if not self.waiting_for_second_click:
                self.waiting_for_second_click = True
                self.last_click = pg.time.get_ticks()
                self.clicking = True
                if self.execution == "down":
                    self.execute("on_click")

            else:
                if pg.time.get_ticks() - self.last_click < 500:
                    self.waiting_for_second_click = False
                    self.execute("on_db_click")
                    print("double clicked")

    def handle_events(self, event: pg.event.Event):
        if event.type == MOUSEBUTTONDOWN:
            self.decide_state(event.pos)

        elif event.type == MOUSEBUTTONUP:
            if self.clicking and self.execution == "up":
                self.execute("on_click")
            self.clicking = False

    def execute(self, state):
        func = self.functions[state]
        args = self.args[state]

        if func is not None:
            if args is not None:
                if type(args) is list:
                    return func(*args)
                else:
                    return func(args)
            return func()

    def draw(self, screen):

        self.update_states()

        if not self.has_icon:
            if not self.clicking:
                pg.draw.rect(
                    screen,
                    (self.bg_color if not self.hovering else self.bg_color_hover),
                    self.rect,
                    border_radius=self.border_radius,
                )
            else:
                pg.draw.rect(screen, (50, 50, 50), self.rect, border_radius=self.border_radius)
                pg.draw.rect(
                    screen,
                    (self.bg_color if not self.hovering else self.bg_color_hover),
                    pg.Rect(self.rect.x, self.rect.y + self.shadow_on_click, *self.rect.size),
                    border_radius=self.border_radius,
                )
        else:
            screen.blit((self.icon if not self.hovering else self.icon_hover), self.rect)

        rect = (
            pg.Rect(self.rect.x, self.rect.y + self.shadow_on_click, *self.rect.size)
            if self.clicking
            else self.rect
        )
        if self.hovering:
            screen.blit(
                self.rendered_hover_text, self.rendered_hover_text.get_rect(center=rect.center)
            )
        else:
            screen.blit(self.rendered_text, self.rendered_text.get_rect(center=rect.center))

    def change_text(self, new_text: str):
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.text_color)
        self.rendered_hover_text = self.font.render(self.text, True, self.text_color_hover)

    def update_states(self):
        if pg.time.get_ticks() - self.last_click > 500:
            self.waiting_for_second_click = False
        self.hovering = self.rect.collidepoint(pg.mouse.get_pos())
