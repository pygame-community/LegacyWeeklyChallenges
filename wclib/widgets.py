import sys
import time
import traceback
from itertools import accumulate
from threading import Thread
from typing import Optional, Callable

import pygame
import pygame.gfxdraw

from wclib.core import *
from wclib.utils import *
from wclib.constants import *

__all__ = [
    "ImageWidget",
    "BigButton",
    "EntryButton",
    "ChallengeButton",
    "Widget",
    "Container",
    "ScrollableWidget",
    "IconButton",
    "EmbeddedApp",
]


class Widget:
    """A simple UI widget archetype. Doesn't support resizing."""

    def __init__(self, pos, size):
        self.position = pygame.Vector2(pos)
        self.size = pygame.Vector2(size)

        self.mouse_over = None

    @property
    def rect(self):
        return pygame.Rect(self.position, self.size)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.mouse_over = self.rect.collidepoint(self.position)

    def logic(self):
        pass

    def draw(self, screen):
        pass


class Container(Widget):
    """A basic container that uses absolute positionning relative to itself."""

    def __init__(self, pos, size, *widgets: Widget):
        super().__init__(pos, size)
        self.widgets = list(widgets)

    def __iter__(self):
        return iter(self.widgets)

    def logic(self):
        for widget in self:
            widget.logic()

    def draw(self, screen):
        visible = self.rect.clamp(screen.get_rect())
        for widget in self:
            widget.draw(screen.subsurface(visible))

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)

        # Don't propagate events outside of the container.
        if hasattr(event, "pos") and not self.mouse_over:
            return False

        fixed_event = self.fix_event(event)
        for widget in self:
            if widget.handle_event(fixed_event):
                return True

        return False

    def fix_event(self, event):
        # We return new event to not interfere with other objects using events
        if hasattr(event, "pos"):
            event = pygame.event.Event(event.type, **event.__dict__)
            event.pos -= self.position
        return event


class ImageWidget(Widget):
    def __init__(self, image: pygame.Surface, pos):
        self.image = image
        super().__init__(pos[:2], image.get_size())

    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.image, self.position)


class IconButton(Widget):
    def __init__(self, pos, size, surf: pygame.Surface, callback: Callable[["IconButton"], None]):
        super().__init__(pos, size)
        self.callback = callback
        self.surf = surf

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback(self)
                return True

    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.surf, self.position)


class BigButton(Widget):
    """Button to select an entry or challenge."""

    NAME_HEIGHT = 32
    SIZE = (SIZE[0] // 5, SIZE[1] // 5)
    TOTAL_SIZE = (SIZE[0], SIZE[1] + NAME_HEIGHT)

    def __init__(self, entry, title, callback, position):
        super().__init__(position, self.TOTAL_SIZE)
        self.entry = entry
        self.title = title
        self.callback = callback
        self.mouse_over = False

        self.app = EmbeddedApp(self.entry, self.position, self.SIZE)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.entry})>"

    def draw(self, screen):
        background = "#222728" if self.mouse_over else "#212121"
        pygame.draw.rect(screen, background, self.rect, border_radius=4)

        self.app.draw(screen)

        offset = pygame.Vector2(0, -self.NAME_HEIGHT / 2)
        t = text(self.title, ACCENT)
        screen.blit(t, t.get_rect(center=self.rect.midbottom + offset))

    def logic(self):
        super().logic()
        if self.mouse_over:
            self.app.logic()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return

        if event.type == pygame.MOUSEMOTION:
            self.mouse_over = self.rect.collidepoint(event.pos)

        if self.mouse_over:
            self.app.handle_event(event)

    def move_to(self, new_pos):
        self.position = pygame.Vector2(new_pos)
        self.app.position = self.position


class EntryButton(BigButton):
    def __init__(self, entry: Entry, callback, position):
        super().__init__(entry, entry.display_name, callback, position)

    def draw(self, screen):
        super().draw(screen)

        stars = self.stars()
        r = stars.get_rect(midright=self.rect.topleft + pygame.Vector2(self.SIZE)).move(-4, -6)
        screen.blit(stars, r)

    def stars(self):
        all_stars = [
            star(color)
            for difficulty, color in DIFFICULY_COLOR.items()
            if difficulty in self.entry.achievements
        ]

        if not all_stars:
            return pygame.Surface((0, 0))

        padding = -10
        # x positions of each star on the final image
        xs = list(accumulate((s.get_width() + padding for s in all_stars), initial=0))
        height = all_stars[0].get_height()  # they all have the same height
        out = pygame.Surface((xs[-1] - padding, height), pygame.SRCALPHA)
        for x, s in zip(xs, all_stars):
            out.blit(s, (x, 0))

        return out


class ChallengeButton(BigButton):
    def __init__(self, challenge, callback, position):
        self.challenge_data = get_challenge_data(challenge)
        super().__init__(Entry(challenge, "base"), self.challenge_data.name, callback, position)

    def draw(self, screen):
        super().draw(screen)

        nb = self.challenge_data.entries_nb - 1
        t = auto_crop(text(nb, GREY))
        r = t.get_rect(bottomright=self.rect.bottomright)
        r.move_ip(-4, -4)
        r.inflate_ip(8, 8)

        # pygame.gfxdraw.box(screen, r, (255, 255, 255, 10))
        screen.blit(t, t.get_rect(center=r.center))


class EmbeddedApp(Widget):
    def __init__(self, entry: Entry, pos=(0, 0), size=SIZE):
        super().__init__(pos, size)
        self.entry = entry
        self.virtual_screen = pygame.Surface(SIZE)

        # This one is for performance improvement.
        # Most buttons are not to be redrawn nor scaled every frame,
        # So we keep the scaled surface if we can.
        # It is discarded every time there is a call to mainloop_next.
        self.scaled_virtual_screen: Optional[pygame.Surface] = None

        self.mainloop = None
        self.exited = False

        self.events_storage = []

    def load(self) -> bool:
        """Ensure the app is loaded. Return False if it was already loaded."""
        if self.mainloop is None:
            self.mainloop = self.load_mainloop()
            self.mainloop_next()
            return True

    def mainloop_next(self, events=(), _first=False):
        # Erase the cache
        self.scaled_virtual_screen = None

        try:
            if _first:
                next(self.mainloop)
            self.mainloop.send((self.virtual_screen, events))
        except StopIteration:
            # The app just quitted.
            self.mainloop = self.app_exited_mainloop()
        except TypeError as e:
            # Yuck!
            if e.args == ("can't send non-None value to a just-started generator",):
                return self.mainloop_next(events, True)
            else:
                self.mainloop = self.crashed_mainloop(e)
        except Exception as e:  # Or BaseException ?
            self.mainloop = self.crashed_mainloop(e)

    def load_mainloop(self):
        if self.entry.min_python_version > sys.version_info:
            loop = self.python_too_old_mainloop()
        elif self.entry.get_missing_dependencies():
            loop = self.install_mainloop()
        else:
            try:
                loop = self.entry.get_mainloop()
            except Exception as e:
                loop = self.crashed_mainloop(e)

        return loop

    def handle_event(self, event):
        self.events_storage.append(self.modify_event(event))

    def logic(self):
        if not self.mainloop:
            self.mainloop = self.load_mainloop()

        self.mainloop_next(self.events_storage)
        self.events_storage.clear()

    def modify_mouse_pos(self, pos):
        return (
            (pos[0] - self.rect.x) * self.virtual_screen.get_width() // self.rect.w,
            (pos[1] - self.rect.y) * self.virtual_screen.get_height() // self.rect.h,
        )

    def modify_mouse_rel(self, pos):
        return (
            (pos[0]) * self.virtual_screen.get_width() // self.rect.width,
            (pos[1]) * self.virtual_screen.get_height() // self.rect.height,
        )

    def modify_event(self, event):
        # We don't modify events as they may be used by other EmbeddedApps.
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return pygame.event.Event(
                event.type,
                button=event.button,
                pos=self.modify_mouse_pos(event.pos),
            )
        elif event.type == pygame.MOUSEMOTION:
            return pygame.event.Event(
                event.type,
                buttons=event.buttons,
                pos=self.modify_mouse_pos(event.pos),
                rel=self.modify_mouse_rel(event.rel),
            )
        return event

    def draw(self, screen: pygame.Surface):
        if not self.mainloop:
            return

        if self.rect.size != self.virtual_screen.get_size():
            if self.scaled_virtual_screen is None:
                self.scaled_virtual_screen = pygame.transform.smoothscale(
                    self.virtual_screen, self.rect.size
                )
            screen.blit(self.scaled_virtual_screen, self.rect)
        else:
            screen.blit(self.virtual_screen, self.rect)

    # Different states of the widget.

    def install_mainloop(self):
        w, h = SIZE
        install_rect = pygame.Rect(0, 0, 600, 100)
        install_rect.midbottom = (w / 2, h - 100)
        mouse = (0, 0)
        installing = False
        install_thread = None
        timer = 0
        clock = pygame.time.Clock()

        while True:
            timer += 1
            clock.tick(60)
            screen, events = yield

            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    mouse = event.pos
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and install_rect.collidepoint(mouse)
                    and not installing
                ):
                    installing = True
                    install_thread = Thread(target=self.entry.install_missing_dependencies)
                    install_thread.start()

            screen.fill("#272822")
            t = text("Missing requirements:", "white", 90)
            r = screen.blit(t, t.get_rect(midtop=(w / 2, 50)))

            for req in self.entry.get_missing_dependencies():
                t = text(req, "white", 72)
                r.top += 30
                r = screen.blit(t, t.get_rect(midtop=r.midbottom))

            # install button
            if install_rect.collidepoint(mouse):
                color = "#6B9BAC"
            else:
                color = "#4B7B8C"
            pygame.draw.rect(screen, color, install_rect, border_radius=10)
            # Button text
            txt = "Install via pip" if not installing else "Installing" + "." * (timer // 30 % 4)
            t = text(txt, "white", 80)
            screen.blit(t, t.get_rect(center=install_rect.center))

            # installation finished!
            if installing and not install_thread.is_alive():
                self.mainloop = None
                print("Still missing after install:", self.entry.get_missing_dependencies())
                return

    def crashed_mainloop(self, error):
        print("Error:", error, file=sys.stderr)
        traceback.print_tb(error.__traceback__, file=sys.stderr)
        screen, events = yield

        t = text(f"Crashed: {error}", "red", 30)
        r = screen.blit(t, t.get_rect(center=screen.get_rect().center))
        t = text("Check the console for details.", "red", 30)
        screen.blit(t, t.get_rect(midtop=r.midbottom))

        while True:
            # Do nothing.
            screen, events = yield

    def python_too_old_mainloop(self):
        text_version = ".".join(map(str, self.entry.min_python_version))
        needed_version = ".".join(map(str, sys.version_info[:3]))

        print("Python version too old for", self.entry, file=sys.stderr)
        print("Current:", needed_version, file=sys.stderr)
        print("Required:", text_version, file=sys.stderr)

        screen, events = yield

        t = text(f"You need Python {text_version} to run this entry,", "red", 30)
        r = screen.blit(t, t.get_rect(center=screen.get_rect().center))
        t = text(f"but you currently have Python {needed_version}.", "red", 30)
        screen.blit(t, t.get_rect(midtop=r.midbottom))

        while True:
            # Do nothing.
            screen, events = yield

    def app_exited_mainloop(self):
        screen, events = yield

        pygame.gfxdraw.box(screen, screen.get_rect(), OVERLAY)
        t = text(f"This app exited gracefully.", "#F6EDD4", 40)
        screen.blit(t, t.get_rect(center=screen.get_rect().center))

        start = time.monotonic()
        while True:
            # Do nothing.
            screen, events = yield

            if time.monotonic() - start > 1:
                self.exited = True


class ScrollableWidget(Container):
    SCROLL_SPEED = 10
    SCROLL_FRICTION = 0.8

    def __init__(
        self,
        pos,
        size,
        *widgets,
        top=BACKGROUND,
        bottom=BACKGROUND,
        bg=BACKGROUND,
        bottom_padding=20,
    ):
        super().__init__(pos, size, *widgets)
        self.top_color = pygame.Color(top)
        self.bottom_color = pygame.Color(bottom)
        self.bg_color = pygame.Color(bg)

        total_height = max(w.rect.bottom for w in widgets) + bottom_padding
        # total_height = self.widgets[-1].rect.bottom + self.GAPS * 2

        if total_height > SIZE[1]:
            self.scrollable_surf = pygame.Surface((SIZE[0], total_height))
        else:
            self.scrollable_surf = None

        self.scroll = 0
        self.scroll_momentum = 0

    @property
    def max_scroll(self):
        if self.scrollable_surf is None:
            return 0
        return self.scrollable_surf.get_height() - SIZE[1]

    def logic(self):
        super().logic()

        if self.scrollable_surf is None:
            return

        self.scroll_momentum *= self.SCROLL_FRICTION
        self.scroll += self.scroll_momentum

        t = 0.7
        if self.scroll <= 0:
            target = 0
        elif self.scroll >= self.max_scroll:
            target = self.max_scroll
        else:
            return

        self.scroll_momentum = self.scroll_momentum * t + (1 - t) * ((target - self.scroll) / 4)

    def _draw(self, screen):
        for widget in self:
            widget.draw(screen)

    def draw(self, screen: pygame.Surface):
        if self.scrollable_surf:
            # Draw everything on the larger surface
            self.scrollable_surf.fill(self.bg_color)
            self._draw(self.scrollable_surf)
            screen.blit(
                self.scrollable_surf,
                self.position,
                self.rect.move(0, self.scroll),
            )

            if self.scroll < 0:
                screen.fill(self.top_color, (*self.position, self.size.x, -self.scroll))
            elif self.scroll > self.max_scroll:
                bottom_blank = self.scroll - self.max_scroll
                screen.fill(
                    self.bottom_color,
                    (
                        self.position.x,
                        self.position.y + self.size.y - bottom_blank,
                        self.size.x,
                        bottom_blank,
                    ),
                )

            if self.scroll <= 100:
                t = text("Scroll down!", ACCENT)
                t.set_alpha(int((1 - self.scroll / 100) * 255))
                screen.blit(t, t.get_rect(bottomright=SIZE - pygame.Vector2(10, 10)))

        else:
            self._draw(screen)

    def handle_event(self, event):
        if super().handle_event(event):
            return True

        if (
            self.mouse_over is not False
            and event.type == pygame.MOUSEWHEEL
            and self.scrollable_surf
        ):
            self.scroll_momentum += event.y * self.SCROLL_SPEED
            return True

    def fix_event(self, event):
        if hasattr(event, "pos"):
            event = pygame.event.Event(event.type, **event.__dict__)
            event.pos = (event.pos[0], event.pos[1] + self.scroll)

        return super().fix_event(event)
