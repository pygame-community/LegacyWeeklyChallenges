import pygame as pg


# theoretically I could use system in 'objects.py', but the script must be independent
# and reusable in other projects, so I have to write it again...
# I'll remove this comment if I am going to re-use this code.
class BaseParticleObject:
    def __init__(
                self, surface: pg.Surface,
                size: pg.Vector2, position: pg.Vector2,
                rotation: float, bounding_box: pg.Rect
            ):
        self.source_surface = surface
        self.size = size
        self.position = position
        self.rotation = rotation
        self.source_rect = bounding_box

        self._smooth_scale = True

    @property
    def surface(self):
        copy = self.source_surface.copy()

        if self._smooth_scale:
            copy = pg.transform.smoothscale(copy, self.tuple_size)
        else:
            copy = pg.transform.smoothscale(copy, self.tuple_size)

        copy = pg.transform.rotate(copy, self.rotation)

        return copy

    @property
    def rect(self):
        copy = self.source_rect.copy()
        copy.topleft = pg.Vector2(copy.topleft) + self.position
        return copy

    @property
    def tuple_size(self):
        return int(self.size.x), int(self.size.y)
