import sys
from pathlib import Path

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "01-fog-of-war." + Path(__file__).parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "Ghast#4475"
__achievements__ = [
    "Casual",
    "Ambitious",
    "Adventurous",
]


from operator import attrgetter
import pygame
import math

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject


def luminance(rgb):
    # yoinked from some website
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def blend(rgbs):
    if len(rgbs) == 0:
        return 0, 0, 0
    else:
        total_sum = [0, 0, 0]
        max_luminosiy = 0
        for rgb in rgbs:
            max_luminosiy = max(max_luminosiy, luminance(rgb))
            for i in range(3):
                total_sum[i] += rgb[i]

        if max_luminosiy == 0:
            return 0, 0, 0
        else:
            avg_color = mult(total_sum, 1 / len(rgbs))
            avg_luminosity = luminance(avg_color)

            # scale it up to the correct brightness
            return mult(avg_color, max_luminosiy / avg_luminosity)


def bound(v, lower, upper):
    return min(max(v, lower), upper)


def intify(rgb):
    return tuple(bound(int(255 * rgb[i]), 0, 255) for i in range(3))


def floatify(rgb):
    return tuple(bound(rgb[i] / 255, 0, 1) for i in range(3))


def mult(rgb, v):
    return tuple(rgb[i] * v for i in range(3))


BG = (0.4, 0.5, 0.42)  # 0x66856C
RV_BG = mult(BG, 0.3)
UNRV_BG = mult(BG, 0.2)

REVEAL_THRESH = 0.1  # luminosity required to reveal a cell

RV_BG_AS_INTS = intify(RV_BG)
UNRV_BG_AS_INTS = intify(UNRV_BG)

LIGHTING_GRID_DIMS = 30, 18


class LightGrid:

    def __init__(self, dims):
        self.grid = pygame.Surface(dims)

    def dims(self):
        return self.grid.get_size()

    def get_grid_cell(self, screen_size, xy):
        return (int(xy[0] / screen_size[0] * self.dims()[0]),
                int(xy[1] / screen_size[1] * self.dims()[1]))

    def compute_lighting(self, screen_size, light_sources, revealed_cells):
        SW, SH = screen_size
        GW, GH = self.dims()

        all_colors = {}  # xy -> list of colors to blend
        visible_cells = set()

        for o in light_sources:
            is_player = isinstance(o, Player)

            oX, oY = o.rect.midbottom
            radius, rgb = o.get_lighting()

            xy1 = self.get_grid_cell(screen_size, (oX - radius, oY - radius))
            xy2 = self.get_grid_cell(screen_size, (oX + radius, oY + radius))

            for x in range(max(0, xy1[0]), min(GW, xy2[0] + 1)):
                for y in range(max(0, xy1[1]), min(GW, xy2[1] + 1)):
                    xy = x, y
                    # this assumes Player will be first in the list
                    if is_player or xy in revealed_cells:
                        sX = (x + 0.5) * SW / GW
                        sY = (y + 0.5) * SH / GH
                        dist = math.sqrt((sX - oX) ** 2 + (sY - oY) ** 2)
                        if dist < radius:
                            c = mult(rgb, (1 - dist / radius) ** 2)
                            if is_player and luminance(c) > REVEAL_THRESH:
                                revealed_cells.add(xy)
                                visible_cells.add(xy)
                            if xy not in all_colors:
                                all_colors[xy] = [RV_BG if xy in revealed_cells else UNRV_BG]
                            all_colors[xy].append(c)

        self.grid.fill(UNRV_BG_AS_INTS)

        for x in range(GW):
            for y in range(GH):
                xy = x, y
                if xy in all_colors:
                    # calling set_at is sorta ok here because the grid is small (-_-)
                    self.grid.set_at(xy, intify(blend(all_colors[xy])))
                elif xy in revealed_cells:
                    self.grid.set_at(xy, RV_BG_AS_INTS)

        return visible_cells

    def draw_bg(self, surface):
        pygame.transform.scale(self.grid, surface.get_size(), surface)


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = [player] + trees + ghosts
    objects_that_emit_light = [o for o in all_objects if o.get_lighting()[0] > 0]

    light_grid = LightGrid(LIGHTING_GRID_DIMS)
    revealed_cells = set()

    clock = pygame.time.Clock()

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)

        vis_cells = light_grid.compute_lighting(screen.get_size(), objects_that_emit_light, revealed_cells)

        light_grid.draw_bg(screen)

        for object in sorted(all_objects, key=attrgetter("rect.bottom")):
            cell_xy = light_grid.get_grid_cell(screen.get_size(), object.rect.midbottom)
            if cell_xy in vis_cells or (isinstance(object, SolidObject) and cell_xy in revealed_cells):
                object.draw(screen)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
