from typing import Union, List, Tuple, Sequence, Iterable, Optional, Callable
from .utils import font

import pygame


# totally didn't take it from here https://github.com/Emc2356/PygameHelper/blob/main/PygameHelper/types.py
Number = Union[int, float]
VectorType = Union["Vector", pygame.math.Vector2]
CoordsType = Union[Tuple[Number, Number], List[Number], pygame.math.Vector2, Sequence[int]]
ColorType = Union[
    pygame.Color,
    str,
    Tuple[Number, Number, Number],
    List[Number],
    int,
    Tuple[Number, Number, Number, Number],
]
RectType = Union[
    pygame.Rect,
    Tuple[Number, Number, Number, Number],
    Tuple[Tuple[Number, Number], Tuple[Number, Number]],
    List[pygame.math.Vector2],
    Tuple[pygame.math.Vector2, pygame.math.Vector2],
    Iterable[pygame.math.Vector2],
    List[Union["Vector"]],
    Tuple[Union["Vector"], Union["Vector"]],
    Iterable[Union["Vector"]],
    List[Number],
]


class Button:
    def __init__(
        self,
        position: CoordsType,
        size: CoordsType,
        anchor: str = "topleft",
        bg_clr: ColorType = (255, 255, 255),
        hover_bg_clr: ColorType = (200, 200, 200),
        text: Optional[str] = "",
        font_name: Optional[str] = "regular",
        font_size: int = 30,
        text_clr: ColorType = (255, 255, 255),
        aa: bool = True,
        border_radius=0,
        on_click: Callable = None,
        sprite: Optional[pygame.surface.Surface] = None,
        hover_sprite: Optional[pygame.surface.Surface] = None,
        double_click: bool = False,
        double_click_limit: int = 300,
    ):
        # auto-completion is important so i pre-type hinted it
        self._x: Number
        self._y: Number
        self._w: Number
        self._h: Number
        self.font: Optional[pygame.font.Font]

        self._x, self._y = position
        self._w, self._h = size
        self.anchor: str = anchor
        self._text: Optional[str] = text
        self.bg_clr: ColorType = bg_clr
        self.text_clr: ColorType = text_clr
        self.aa: bool = aa
        self.border_radius: int = border_radius
        self.hover_bg_clr: ColorType = hover_bg_clr

        self.sprite: Optional[pygame.surface.Surface] = sprite
        self.hover_sprite: Optional[pygame.surface.Surface] = hover_sprite

        self.rect: pygame.Rect
        self.rendered_text: Optional[pygame.surface.Surface] = None
        self.rendered_text_rect: pygame.Rect

        self.on_click: Callable = on_click

        self.double_click: bool = double_click
        self.msC: Optional[int] = None
        if double_click:
            self.first_click: bool = False
            self.msC: Optional[int] = 0
            self.double_click_limit: int = double_click_limit

        if font_name is not None:
            self.font = font(font_size, font_name)
        else:
            self.font = None

        self._update()

    def event_handler(
        self, events: List[pygame.event.Event], clock: Optional[pygame.time.Clock] = None
    ) -> "Button":
        if self.double_click and clock is None:
            raise TypeError("clock was expected to function with double-click(s)")
        if self.double_click:
            self.msC += clock.get_rawtime()
            if self.msC > self.double_click_limit:
                self.msC = 0
                self.first_click = False
        for event in events:
            if (
                self.on_click
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos)
            ):
                if not self.double_click:
                    self.on_click()
                else:
                    if self.first_click:
                        if self.msC <= self.double_click_limit:
                            self.msC = 0
                            self.on_click()
                            self.first_click = False
                    else:
                        self.first_click = True

        return self

    def draw(self, surface: pygame.surface.Surface) -> "Button":
        # Use this to draw the button on the screen
        # As a placeholder, I draw its content, but it may be more complex
        # when you do it. Maybe you use images, maybe likely some background,
        # maybe some border and even shadows ?
        if self.sprite is None:
            bg_clr = (
                self.hover_bg_clr if self.rect.collidepoint(pygame.mouse.get_pos()) else self.bg_clr
            )
            pygame.draw.rect(surface, bg_clr, self.rect, border_radius=self.border_radius)
        else:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                surface.blit(self.hover_sprite, self.rect)
            else:
                surface.blit(self.sprite, self.rect)
        if self.rendered_text:
            surface.blit(self.rendered_text, self.rendered_text_rect)
        return self

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, val: Number) -> None:
        self._x = val
        self._update()

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, val: Number) -> None:
        self._y = val
        self._update()

    @property
    def w(self) -> int:
        return self._w

    @w.setter
    def w(self, val: Number) -> None:
        self._w = val
        self._update()

    @property
    def h(self) -> int:
        return self._h

    @h.setter
    def h(self, val: Number) -> None:
        self._h = val
        self._update()

    @property
    def text(self) -> Optional[str]:
        return self._text

    @text.setter
    def text(self, text: Optional[str]) -> None:
        self._text = text
        self._update()

    def _update(self) -> None:
        self.rect = pygame.Rect(0, 0, self._w, self._h)
        try:
            self.rect.__setattr__(self.anchor, (self._x, self._y))
        except AttributeError:
            raise TypeError("unknown value passed as the anchor")
        txt = self.text
        if txt is not None and txt != "" and self.font is not None:
            self.rendered_text = self.font.render(txt, self.aa, self.text_clr)
            self.rendered_text_rect = self.rendered_text.get_rect(center=self.rect.center)
        else:
            self.rendered_text = None
