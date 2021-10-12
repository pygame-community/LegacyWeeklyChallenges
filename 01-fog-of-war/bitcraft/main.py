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
# aka bitcraft
__author__ = "thecornboss#2284"
__achievements__ = [
    "Casual",
    "Ambitious",
    "Adventurous",
]

"""
improvements to be made:
* smarter management of the blocked cells table
* faster mask creation 
* scale the cells to a higher resolution buffer
* gaussian blur
* needs code cleanup
* faster FOV -- not suitable for large light radius
* current FOV doesn't handle arbitrary shapes
* figure out method for light bleeding besides using `circle`

-- bitcraft, 2021

"""

from functools import partial
from operator import attrgetter
from random import randint
import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C

MULT = [
    [1, 0, 0, -1, -1, 0, 0, 1],
    [0, 1, -1, 0, 0, -1, 1, 0],
    [0, 1, 1, 0, 0, -1, -1, 0],
    [1, 0, 0, 1, -1, 0, 0, -1],
]


def get_visible_points(vantage_point, get_allows_light, max_distance=30):
    """
    Returns a set of all points visible from the given vantage point.

    Adopted from https://raw.githubusercontent.com/irskep/clubsandwich/afc79ed/clubsandwich/line_of_sight.py
    Adapted from `this RogueBasin article <http://www.roguebasin.com/index.php?title=Python_shadowcasting_implementation>`_.
    """
    x, y = vantage_point
    los_cache = set()
    los_cache.add(vantage_point)
    blocked_set = set()
    distance = dict()
    distance[vantage_point] = 0
    for region in range(8):
        _cast_light(
            los_cache,
            blocked_set,
            distance,
            get_allows_light,
            x,
            y,
            1,
            1.0,
            0.0,
            max_distance,
            MULT[0][region],
            MULT[1][region],
            MULT[2][region],
            MULT[3][region],
        )
    return los_cache, blocked_set, distance


def _cast_light(
    los_cache,
    blocked_set,
    distance,
    get_allows_light,
    cx,
    cy,
    row,
    start,
    end,
    radius,
    xx,
    xy,
    yx,
    yy,
):
    if start < end:
        return

    radius_squared = radius ** 2

    for j in range(row, radius + 1):
        dx, dy = -j - 1, -j
        blocked = False
        while dx <= 0:
            dx += 1
            X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
            point = X, Y
            l_slope, r_slope = (dx - 0.5) / (dy + 0.5), (dx + 0.5) / (dy - 0.5)
            if start < r_slope:
                continue
            elif end > l_slope:
                break
            else:
                d = dx ** 2 + dy ** 2
                if d < radius_squared:
                    los_cache.add(point)
                    distance[point] = d
                if blocked:
                    if not get_allows_light(point):
                        new_start = r_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if not get_allows_light(point) and j < radius:
                        blocked = True
                        blocked_set.add(point)
                        distance[point] = d
                        _cast_light(
                            los_cache,
                            blocked_set,
                            distance,
                            get_allows_light,
                            cx,
                            cy,
                            j + 1,
                            start,
                            l_slope,
                            radius,
                            xx,
                            xy,
                            yx,
                            yy,
                        )
                        new_start = r_slope
        if blocked:
            break


def mainloop():
    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + ghosts + [player]

    ## configurable parameters
    # smaller cells are slower but gives higher resolution mask
    cell_size_px = 4
    # light radius in pixels
    light_radius_px = 140
    # darkness of the explored areas
    explored_value = 64
    # min expose radius when light touches a sprite
    blocked_expose_min_px = 48
    # max expose radius when light touches a sprite
    blocked_expose_max_px = 64
    # min expose radius when light doesn't touch a sprite
    unblocked_expose_min_px = 8
    # max expose radius when light doesn't touch a sprite
    unblocked_expose_max_px = 24
    # radius of cast light around source
    cast_light_px = 32
    # values greater than 1 will result in color bands and faster/retro rendering
    # setting it to 1 will result in a smooth light cast.  must be changed with cell
    # size and light radius, or light won't render at correct brightness.
    # table for known values:
    # cell    value  notes
    # 4       400    3 color bands
    # 4       17     higher values create noticeable moire pattern
    # 4       3      no artifacts, some caching
    light_mod_value = 400

    light_radius = int(light_radius_px // cell_size_px)
    light_radius2 = light_radius ** 2
    light_radius_px2 = light_radius_px ** 2

    new_points = set()
    cast_light = None
    blocked_light_min = None
    blocked_light_max = None
    unblocked_light_min = None
    unblocked_light_max = None
    old_screen = None
    work_surface = None
    fog_tiles = None
    fog_table = None
    fog_surface = None
    light_surface = None

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        sw, sh = screen.get_size()
        stw = sw // cell_size_px
        sth = sh // cell_size_px

        # init fog stuff
        if old_screen is not screen:
            old_screen = screen
            fog_size = sw // cell_size_px, sh // cell_size_px
            work_surface = pygame.surface.Surface((sw, sh))
            fog_surface = pygame.surface.Surface(fog_size)
            light_surface = pygame.surface.Surface(fog_size)
            blocked_light_min = max(1, blocked_expose_min_px // cell_size_px)
            blocked_light_max = max(1, blocked_expose_max_px // cell_size_px)
            unblocked_light_min = max(1, unblocked_expose_min_px // cell_size_px)
            unblocked_light_max = max(1, unblocked_expose_max_px // cell_size_px)
            cast_light = max(1, cast_light_px // cell_size_px)
            fog_table = dict()
            fog_tiles = list()
            for y in range(0, sth * cell_size_px, cell_size_px):
                row = list()
                fog_tiles.append(row)
                for x in range(0, stw * cell_size_px, cell_size_px):
                    row.append(False)

        for obj in all_objects:
            obj.logic(objects=all_objects)

        # clear collision mask
        for row in fog_tiles:
            for x in range(len(row)):
                row[x] = True

        # set collision mask
        for obj in all_objects:
            if obj is player:
                continue
            # cast shadow using bbox of image
            rect = obj.bbox.move(obj.rect.topleft)
            left = rect.left // cell_size_px
            top = rect.top // cell_size_px
            right = rect.right // cell_size_px
            bottom = rect.bottom // cell_size_px
            for y in range(top, bottom + 1):
                for x in range(left, right + 1):
                    try:
                        fog_tiles[y][x] = False
                    except IndexError:
                        pass
            # cast shadow with mask - very glitchy
            # rect = obj.rect
            # left = rect.left // cell_size_px
            # top = rect.top // cell_size_px
            # for point in obj.outline:
            #     x, y = point
            #     x += left
            #     y += top
            #     try:
            #         fog_tiles[y][x] = False
            #     except IndexError:
            #         pass

        # smooth fade and hide ghosts
        x1, y1 = player.rect.center
        for ghost in ghosts:
            x2, y2 = ghost.rect.center
            d2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
            if d2 < light_radius_px2:
                opacity = 1 - (d2 / light_radius_px2)
                opacity = int(out_quad(opacity) * 255)
                opacity = min(255, max(0, opacity))
                ghost.hidden = False
                ghost.opacity = opacity
            else:
                ghost.hidden = True

        # get visible and blocked cells, with the distance for them
        px = player.rect.centerx // cell_size_px
        py = player.rect.centery // cell_size_px
        func = partial(light, fog_tiles)
        visible, blocked, distance = get_visible_points((px, py), func, light_radius)

        # update the fog table, order of update is important; blocked first, then visible
        new_points.clear()
        for point in blocked:
            if point not in fog_table:
                size = randint(blocked_light_min, blocked_light_max)
                fog_table[point] = size
                new_points.add((point, size))
        for point in visible:
            if point not in fog_table:
                size = randint(unblocked_light_min, unblocked_light_max)
                fog_table[point] = size
                new_points.add((point, size))

        draw_fog(
            fog_surface,
            light_surface,
            visible,
            distance,
            new_points,
            explored_value,
            light_radius2,
            cast_light,
            light_mod_value,
        )

        screen.fill(BACKGROUND)
        for obj in sorted(all_objects, key=attrgetter("rect.bottom")):
            obj.draw(screen)

        pygame.transform.scale(light_surface, work_surface.get_size(), work_surface)
        screen.blit(work_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        clock.tick(60)


def draw_fog(
    fog_surface,
    light_surface,
    visible,
    distance,
    new_points,
    explored_value,
    light_radius2,
    cast_light_radius,
    light_mod_value,
):
    """
    * draw circles to expose explored map areas on fog surface
    * clear light surface to black
    * draw visible light on light surface:
      - ordered from furthest to closest...
      - calculate color value
      - draw circle to expose/brighten map

    """
    explored_color = explored_value, explored_value, explored_value
    white = 255, 255, 255
    circle = pygame.draw.circle
    fog_surface.lock()
    light_surface.lock()
    # draw explored cells
    for point, size in new_points:
        circle(fog_surface, white, point, size)
    # make list of visible cells for sorting
    draw_list = list()
    for point in visible:
        draw_list.append((distance[point], point))
    draw_list.sort(reverse=True)
    # draw cells in the light radius
    # avoid too many calculations, also enable color banding
    cache = dict()
    light_surface.fill(explored_color)
    value_range = 255 - explored_value
    for d, point in draw_list:
        token = d // light_mod_value
        try:
            color = cache[token]
        except KeyError:
            value0 = 1 - (d / light_radius2)
            value = int(out_quad(value0) * value_range) + explored_value
            value = min(255, max(0, value))
            color = value, value, value
            cache[token] = color
        circle(light_surface, color, point, cast_light_radius)
    fog_surface.unlock()
    light_surface.unlock()
    light_surface.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_MULT)


def light(fog_tiles, point):
    try:
        return fog_tiles[point[1]][point[0]]
    except IndexError:
        return False


def out_quad(progress):
    return -1.0 * progress * (progress - 2.0)


if __name__ == "__main__":
    wclib.run(mainloop())
