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
import numpy

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


def blend_arrays(arr1, arr2):
    lumin1 = arr1[:, :, 0] * 0.2126 + arr1[:, :, 1] * 0.7152 + arr1[:, :, 2] * 0.0722
    lumin1 = numpy.repeat(lumin1[:, :, numpy.newaxis], 3, axis=2)

    lumin2 = arr2[:, :, 0] * 0.2126 + arr2[:, :, 1] * 0.7152 + arr2[:, :, 2] * 0.0722
    lumin2 = numpy.repeat(lumin2[:, :, numpy.newaxis], 3, axis=2)

    return (arr1 * lumin1 + arr2 * lumin2) / (lumin1 + lumin2)


def bound(v, lower, upper):
    return min(max(v, lower), upper)


def intify(rgb):
    return tuple(bound(int(255 * rgb[i]), 0, 255) for i in range(3))


def floatify(int_rgb):
    return tuple(bound(int_rgb[i] / 255, 0, 1) for i in range(3))


def hexify(int_rgb):
    return 0xFF000000 + 0x010000 * int_rgb[0] + 0x000100 * int_rgb[1] + 0x000001 * int_rgb[2]


def mult(rgb, v):
    return tuple(rgb[i] * v for i in range(3))


BG = (0.4, 0.5, 0.42)  # 0x66856C
RV_BG = mult(BG, 0.5)
UNRV_BG = mult(BG, 0.3)

REVEAL_THRESH = 0.1
GHOST_VIS_THRESH = REVEAL_THRESH / 8

RV_BG_AS_INTS = intify(RV_BG)
UNRV_BG_AS_INTS = intify(UNRV_BG)

LIGHTING_GRID_DIMS = 64, 48
LIGHT_RADIUS = int(min(LIGHTING_GRID_DIMS) / 2) - 1
GAUSSIAN_STD_DEV = 0.12

PLAYER_DIM = 0.9
GHOST_DIM = 0.55

TINT_RESOLUTION = 16
COLORS_TO_TINT = ((102, 133, 108), (70, 102, 85))


def get_1d_gaussian_kernel(n_points, std_dev=GAUSSIAN_STD_DEV, _cache={}):
    key = (n_points, std_dev)
    if key not in _cache:
        raw_values = []
        for i in range(n_points):
            x = ((i + 0.5) - n_points / 2) / (n_points / 2)
            y = 1 / math.sqrt(2 * math.pi * std_dev) * math.exp(-0.5 * x**2 / std_dev)
            raw_values.append(y)
        total_sum = sum(raw_values)
        normalized_values = [y / total_sum for y in raw_values]

        _cache[key] = numpy.array(normalized_values)

    return _cache[key]


def blur_array(array, radius: int):
    kernel = get_1d_gaussian_kernel(radius * 2 + 1)

    # XXX these calls are dreadfully slow on large surfaces
    # yoinked from https://stackoverflow.com/a/65804973
    array = numpy.apply_along_axis(lambda x: numpy.convolve(x, kernel, mode='same'), 0, array)
    array = numpy.apply_along_axis(lambda x: numpy.convolve(x, kernel, mode='same'), 1, array)

    return array


def blur_surface(surface: pygame.Surface, radius: int, dest=None) -> pygame.Surface:
    """Applies a Gaussian blur to the surface and returns the result.
    """
    array = pygame.surfarray.pixels3d(surface)
    array = blur_array(array, radius)

    if dest is None:
        dest = surface.copy()

    pygame.surfarray.blit_array(dest, array)

    return dest


class LightGrid:

    def __init__(self, dims):
        self.surf = pygame.Surface(dims)

        self.grass = numpy.zeros([dims[0], dims[1], 3], dtype=numpy.float)
        for i in range(3):
            self.grass[:, :, i] = UNRV_BG[i]

        self.lighting = numpy.zeros([dims[0], dims[1], 3], dtype=numpy.float)

        self.luminance = numpy.zeros([dims[0], dims[1]], dtype=numpy.float)
        self.revealed = self.lighting[:, :, 0] > REVEAL_THRESH
        self.visible = self.lighting[:, :, 0] > REVEAL_THRESH

    def dims(self):
        return self.surf.get_size()

    def get_grid_cell(self, screen_size, xy, force_inside=False):
        x = int(xy[0] / screen_size[0] * self.dims()[0])
        y = int(xy[1] / screen_size[1] * self.dims()[1])
        if not force_inside:
            return x, y
        else:
            dims = self.dims()
            return bound(x, 0, dims[0] - 1), bound(y, 0, dims[1] - 1)

    def is_revealed_at(self, screen_size, xy):
        cell_xy = self.get_grid_cell(screen_size, xy, force_inside=True)
        return self.revealed[cell_xy[0], cell_xy[1]]

    def is_visible_at(self, screen_size, xy):
        cell_xy = self.get_grid_cell(screen_size, xy, force_inside=True)
        return self.visible[cell_xy[0], cell_xy[1]]

    def get_luminance_at(self, screen_size, xy):
        cell_xy = self.get_grid_cell(screen_size, xy, force_inside=True)
        return self.luminance[cell_xy[0], cell_xy[1]]

    def get_color_at(self, screen_size, xy):
        cell_x, cell_y = self.get_grid_cell(screen_size, xy, force_inside=True)
        return tuple(self.lighting[cell_x, cell_y, i] for i in range(3))

    def compute_lighting(self, screen_size, light_sources):
        self.lighting[...] = 0
        self.luminance[...] = 0

        max_kernel_val_pow2 = max(get_1d_gaussian_kernel(LIGHT_RADIUS * 2 + 1)) ** 2

        for o in light_sources:
            is_player = isinstance(o, Player)

            obj_color = o.get_light_color()

            xy = self.get_grid_cell(screen_size, o.rect.midbottom, force_inside=True)

            if is_player:
                obj_color = mult(obj_color, PLAYER_DIM)
                self.luminance[xy] = luminance(obj_color) / max_kernel_val_pow2
            else:
                obj_color = mult(obj_color, GHOST_DIM)
                pass

            for i in range(3):
                self.lighting[xy[0]][xy[1]][i] += obj_color[i] / max_kernel_val_pow2

        self.lighting = blur_array(self.lighting, LIGHT_RADIUS)
        self.lighting[self.lighting > 1] = 1.0
        self.lighting[self.lighting < 0] = 0.0

        self.luminance = blur_array(self.luminance, LIGHT_RADIUS)
        self.luminance[self.luminance > 1] = 1.0
        self.luminance[self.luminance < 0] = 0.0

        dimming = self.luminance * 0.3 + 0.7

        for i in range(3):
            self.lighting[:, :, i] *= dimming

        self.visible = self.luminance > REVEAL_THRESH
        self.revealed |= self.luminance > REVEAL_THRESH

        for i in range(3):
            self.lighting[:, :, i][self.revealed == False] = 0
            self.grass[:, :, i][self.revealed] = RV_BG[i]

    def draw_bg(self, surface):
        res = blend_arrays(self.lighting, self.grass)

        pygame.surfarray.blit_array(self.surf, res * 255)
        pygame.transform.scale(self.surf, surface.get_size(), surface)


def tint_image(base_img, img_key, color, colors_to_tint, _cache={}):
    int_color = intify(color)
    tint_color = floatify([round(int_color[i] / TINT_RESOLUTION) * TINT_RESOLUTION for i in range(3)])

    key = (tint_color, img_key, colors_to_tint)

    if key not in _cache:
        res = base_img.copy()
        array = pygame.surfarray.pixels2d(res)
        for c in colors_to_tint:
            orig_color_as_hex = hexify(c)
            tinted_color_as_hex = hexify(intify(blend([floatify(c), tint_color])))
            array[array == orig_color_as_hex] = tinted_color_as_hex

            _cache[key] = res

    return _cache[key]


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = [player] + trees + ghosts
    objects_that_emit_light = [o for o in all_objects if o.get_light_color() is not None]

    light_grid = LightGrid(LIGHTING_GRID_DIMS)

    clock = pygame.time.Clock()

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)

        light_grid.compute_lighting(screen.get_size(), objects_that_emit_light)

        light_grid.draw_bg(screen)

        for obj in sorted(all_objects, key=attrgetter("rect.bottom")):
            is_visible = light_grid.is_visible_at(screen.get_size(), obj.rect.midbottom)
            is_revealed = light_grid.is_revealed_at(screen.get_size(), obj.rect.midbottom)

            force_showing = False
            force_image = None
            if isinstance(obj, Ghost) or isinstance(obj, Player):
                if is_visible:
                    obj.sprite.set_alpha(255)
                elif is_revealed:
                    lumin = light_grid.get_luminance_at(screen.get_size(), obj.rect.midbottom)
                    if lumin >= REVEAL_THRESH:
                        obj.sprite.set_alpha(255)
                    elif lumin <= GHOST_VIS_THRESH:
                        obj.sprite.set_alpha(0)
                    else:
                        a = (lumin - GHOST_VIS_THRESH) / (REVEAL_THRESH - GHOST_VIS_THRESH)
                        obj.sprite.set_alpha(int(a * 255))
                    force_showing = True
            elif isinstance(obj, SolidObject) and is_revealed:
                force_showing = True
                tint_color = light_grid.get_color_at(screen.get_size(), obj.rect.midbottom)
                tint_color = mult(tint_color, 0.8)
                force_image = tint_image(obj.sprite, obj.my_sheet_rect, tint_color, COLORS_TO_TINT)

            if is_visible or force_showing:
                obj.draw(screen, with_sprite=force_image)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
