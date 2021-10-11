import math
import os
import random
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
__author__ = "andenixa#2251"
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    # "Ambitious",
    "Adventurous",
]

from operator import attrgetter

import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
from .objects import Ghost, Player, SolidObject

BACKGROUND = 0x66856C


TILE_POS_NONE = 0
TILE_POS_NW = 1
TILE_POS_NE = 2
TILE_POS_SW = 4
TILE_POS_SE = 8
TILE_POS_ALL = 15
TILE_POS_W = 5
TILE_POS_E = 10
TILE_POS_N = 3
TILE_POS_S = 12

# matches (relative) positional flags to tile/sprite numbers
# Note: numbers don't mean anything, they are just pic position in the sprite sheet
tset_flag_to_graph = {
    TILE_POS_ALL: 8,
    TILE_POS_W: 2,
    TILE_POS_S: 7,
    TILE_POS_N: 4,
    TILE_POS_E: 6,
    TILE_POS_SW: 1,
    TILE_POS_SE: 9,
    TILE_POS_NW: 3,
    TILE_POS_NE: 5,
    TILE_POS_NONE: 0,
    TILE_POS_W | TILE_POS_S: 12,
    TILE_POS_W | TILE_POS_N: 13,
    TILE_POS_E | TILE_POS_N: 10,
    TILE_POS_E | TILE_POS_S: 11,
    TILE_POS_NE | TILE_POS_SW: 14,
    TILE_POS_SE | TILE_POS_NW: 15,
}


class Grid:
    """represent a grid, to be accessed via grid[x, y]"""

    def __init__(self, ncols, nrows, size, value=0):
        self.ncols = ncols
        self.size = size
        self.nrows = nrows
        self._items = [[value for n in range(ncols)] for m in range(nrows)]

    def cell_at_pos(self, pos):
        x, y = pos
        col = x // self.size[0]
        row = y // self.size[1]
        return col, row

    def __setitem__(self, where, value):
        col, row = where
        self._items[row][col] = value

    def __getitem__(self, where):
        col, row = where
        return self._items[row][col]

    def __len__(self):
        return self.nrows * self.ncols


class LightSpot:
    """Prepares light spot picture"""

    def __init__(self, size, fog_color, noise_str=7, light_frames=5, fps=15):
        self._light_sphere = pygame.Surface(size).convert()
        self._radius = radius = (size[0] // 2) - 8
        self._fog_color = fog_color
        self._light_sphere_w = self._light_sphere.get_size()[0]
        self.x = 0
        self.y = 0
        self._light_sphere.fill(self._fog_color)
        self._delay = 1000 // fps
        self._lights = []

        print("Generating lights bulbs ..")
        for _ in range(light_frames):
            s = self._light_sphere.copy()
            self._draw_spot(s)
            self._render_noise(s, noise_str)
            self._lights.append(s)

    @property
    def light_color(self):
        return self._lights[0].get_at((self._light_sphere_w // 2, self._light_sphere_w // 2))

    def _draw_spot(self, surf):
        pos = (self._light_sphere_w // 2, self._light_sphere_w // 2)
        c = 0
        for r in range(self._radius, 10, -1):
            c += 1
            c = max(c, 0)
            c1 = min(self._fog_color[0] + c, 255)
            c2 = min(self._fog_color[1] + c + 25, 255)
            c3 = min(self._fog_color[2] + c, 255)
            pygame.draw.circle(surf, (c1, c2, c3), pos, r)

    def _render_noise(self, surf, severity):
        r = 3
        for x in range(r, self._light_sphere_w, r):
            for y in range(r, self._light_sphere_w, r):
                color = surf.get_at((x, y))
                c1 = color.r
                c2 = color.g
                c3 = color.b
                if (c1, c2, c3) == self._fog_color:
                    continue
                noise_add = random.randint(0, severity)
                noise_c = (
                    min(c1 + noise_add, 255),
                    min(c2 + noise_add, 255),
                    min(c3 + noise_add, 255),
                )
                radius = random.randint(1, r)
                pygame.draw.circle(surf, noise_c, (x - radius, y - radius), radius)
                # pixel noise doesn't work with soft shadows
                # surf.set_at((x,y), )
                #

    def draw(self, surf, special_flags=0):
        surf.blit(
            self._lights[(pygame.time.get_ticks() // self._delay) % len(self._lights)],
            (self.x, self.y),
            special_flags=special_flags,
        )


def in_circle(c_x, c_y, radius, x, y):
    """check if point x, y is inside circle c_x, c_y with specified radius"""
    dx = x - c_x
    dy = y - c_y
    return (dx * dx + dy * dy) <= radius * radius


def tile_paint(graph_grid, flag_grid, pos, paint_flag=TILE_POS_ALL):
    """tile drawing
    used to find adjucent edges for seamless tile coverage (like a map editor)
    """
    res = False
    col, row = pos
    pos_idx = 0
    pbrush = [
        TILE_POS_SE,
        TILE_POS_S,
        TILE_POS_SW,
        TILE_POS_E,
        paint_flag,
        TILE_POS_W,
        TILE_POS_NE,
        TILE_POS_N,
        TILE_POS_NW,
    ]

    for y in range(row - 1, row + 2):
        for x in range(col - 1, col + 2):
            if x < -1 or y < -1:  # the edge is till a little glitchty
                continue
            pb_flag = pbrush[pos_idx]
            try:
                if paint_flag != TILE_POS_NONE:
                    tile_flag = flag_grid[x, y] | pb_flag
                else:
                    tile_flag = flag_grid[x, y] & ~pb_flag
            except IndexError:  # takes care of the edge if a map ;(
                continue
            sprite_no = tset_flag_to_graph[tile_flag]
            old_sprite = graph_grid[x, y]
            if old_sprite != sprite_no:
                res = True
            graph_grid[x, y] = sprite_no
            flag_grid[x, y] = tile_flag

            pos_idx += 1
    return res


def rect_dist(r1, r2):
    return max(abs(r1.centerx - r2.centerx), abs(r1.centery - r2.centery))


def measure_angle_vec(vec2, vec1):
    return (vec2 - vec1).as_polar()[1]


def load_tiles(fn, size, colorkey=None, scale=None, verbose=True):
    """load all sprites of size in image file fn
    return: subsurfaces of all sprites
    """
    if verbose:
        print("Loading:", fn)
    sheet = pygame.image.load(fn).convert()
    if colorkey is not None:
        sheet.set_colorkey(colorkey)
    tiles = []
    for row in range(0, sheet.get_size()[1], size[1]):
        for col in range(0, sheet.get_size()[0], size[0]):
            tile = sheet.subsurface((col, row, *size))
            if scale is not None:
                tile = pygame.transform.scale(tile, (int(size[0] * scale), int(size[1] * scale)))
            tiles.append(tile)
    return tiles


def mainloop():
    screen, events = yield
    width, height = screen.get_size()

    DEBUG_DRAW = False
    BLUR_SHADOWS = 2
    LIGHT_SPOT_SIZE = 320
    FOG_TILE_WIDTH = 64
    FOG_GRID_SIZE = (width // FOG_TILE_WIDTH + 2, height // FOG_TILE_WIDTH + 2)
    COLOR_MAGENTA = (114, 89, 151)
    DISCOVERY_TILES_RADIUS = (LIGHT_SPOT_SIZE // FOG_TILE_WIDTH) // 2
    angle_step = 3  # for raycasting
    shadow_divider = 6
    Vector2 = pygame.Vector2
    discovery_tile_offsets = []

    for y in range(-DISCOVERY_TILES_RADIUS, DISCOVERY_TILES_RADIUS + 1):
        for x in range(-DISCOVERY_TILES_RADIUS, DISCOVERY_TILES_RADIUS + 1):
            if in_circle(0, 0, DISCOVERY_TILES_RADIUS, x, y):
                discovery_tile_offsets.append((x, y))

    # discovery_tile_offsets = ((0,0), (-1,0), (0,-1), (1,0), (0,1),(-1,1),(1,1),(0,2))
    tile_scale = None
    if FOG_TILE_WIDTH != 32:
        tile_scale = FOG_TILE_WIDTH / 32
    fog_tiles = load_tiles("fog_of_war.png", (32, 32), scale=tile_scale)
    t_size = fog_tiles[0].get_size()
    fog_t_graph = Grid(*FOG_GRID_SIZE, t_size, tset_flag_to_graph[TILE_POS_NONE])
    fog_t_flags = Grid(*FOG_GRID_SIZE, t_size, TILE_POS_NONE)
    fog_t_visited = Grid(*FOG_GRID_SIZE, t_size, False)

    fog_size_w, fog_size_h = fog_tiles[0].get_size()
    fog_color = COLOR_MAGENTA

    light_spot = LightSpot((LIGHT_SPOT_SIZE, LIGHT_SPOT_SIZE), fog_color)

    fog_surface = pygame.Surface(screen.get_size())
    screen.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_MULT)

    light_color = screen.get_at((0, 0))
    lighto = pygame.Surface((LIGHT_SPOT_SIZE, LIGHT_SPOT_SIZE))

    obj_rects = {}  # object rects cache (in case I want to alter those)
    obj_srects = {}  # objects subrect/"texels" cache

    cull_distance = light_spot._light_sphere_w // 2  # for sahdow generation
    ray_length = light_spot._radius + 15  # raycasting ray length

    player = Player((100, 100))
    trees = SolidObject.generate_many(36)
    ghosts = [Ghost() for _ in range(16)]

    all_objects = trees + [player] + ghosts
    old_tile_col, old_tile_row = -1, -1

    clock = pygame.time.Clock()
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

        for obj in all_objects:
            obj.logic(objects=all_objects)

        tile_col, tile_row = fog_t_graph.cell_at_pos((player.rect.centerx, player.rect.centery))

        if (tile_col != old_tile_col or tile_row != old_tile_row) and not fog_t_visited[
            tile_col, tile_row
        ]:
            for xoff, yoff in discovery_tile_offsets:
                col = tile_col + xoff
                row = tile_row + yoff
                tile_paint(fog_t_graph, fog_t_flags, (col, row))
            fog_t_visited[tile_col, tile_row] = True

        old_tile_col, old_tile_row = fog_t_graph.cell_at_pos(
            (player.rect.centerx, player.rect.centery)
        )

        screen.fill(BACKGROUND)

        radius = light_spot._radius
        for object in tuple(sorted(all_objects, key=attrgetter("rect.bottom"))):
            if isinstance(object, Ghost):
                if not in_circle(
                    object.rect.x, object.rect.y, radius, player.rect.x, player.rect.y
                ):
                    continue
            object.draw(screen)

        fog_surface.fill(light_spot._fog_color)

        pygame.draw.rect(
            fog_surface,
            light_spot.light_color,
            (
                player.rect.centerx - LIGHT_SPOT_SIZE // 2,
                player.rect.centery - LIGHT_SPOT_SIZE // 2,
                LIGHT_SPOT_SIZE,
                LIGHT_SPOT_SIZE,
            ),
        )

        p_rect = player.rect

        all_objects_filtered = sorted(
            (
                obj
                for obj in all_objects
                if not obj is player
                and not obj.rect.colliderect(p_rect)
                and rect_dist(player.rect, obj.rect) < cull_distance
            ),
            key=lambda obj: player.pos.distance_squared_to(obj.pos),
            reverse=True,
        )

        if not DEBUG_DRAW:
            surf = fog_surface
        else:
            surf = screen

        player_c_pos = player.rect.center
        color = light_spot._fog_color

        rays_cache = {}  # current frame rays cache

        for obj in all_objects_filtered:
            obj_rect = obj_rects.get(obj, None)
            if obj_rect is None:
                obj_rect = obj.sprite.get_bounding_rect()
                obj_rects[obj] = obj_rect
            obj_rect.center = obj.rect.center
            shadow_len = int(
                obj.rect.height * 0.15 + Vector2(obj_rect.center).distance_to(player_c_pos) // 3
            )
            subrects = obj_srects.get(obj, None)
            # building a sprite cell-grid "a with minimal box that contains data"
            # pygame functinality
            if subrects is None:
                subrects = []
                subdivs = obj_rect.width // shadow_divider
                v_subdivs = obj_rect.height // shadow_divider
                cell_w = obj_rect.width // subdivs
                cell_h = obj_rect.height // v_subdivs
                for row in range(v_subdivs):
                    for col in range(subdivs):
                        x = col * cell_w
                        y = row * cell_h
                        ss = obj.sprite.subsurface((x, y, cell_w, cell_h))
                        s_rect = ss.get_bounding_rect()
                        if not all(s_rect[2:]):
                            continue
                        subrects.append((s_rect, (x, y)))
                obj_srects[obj] = subrects

            # moving rects to object's position
            for s_rect, (x, y) in subrects:
                s_rect.x = obj.rect.x + x
                s_rect.y = obj.rect.y + y
                if DEBUG_DRAW:
                    pygame.draw.rect(surf, (22, 132, 211), s_rect, 1)

            # sort by distance to player for "tracing" effect
            subrects1 = sorted(
                [sr for sr, _ in subrects],
                key=lambda r: Vector2(r.center).distance_squared_to(player_c_pos),
            )
            # sort by distance to "camera" lighting effect
            subrects2 = sorted(subrects1, key=attrgetter("bottom"))

            # Vector2(player.rect.center)
            # get angle from player to object to trace it
            angle = (
                int(measure_angle_vec(Vector2(obj_rect.center), player_c_pos)) // angle_step
            ) * angle_step

            pts1 = []
            pts2 = []
            ray_v = Vector2(ray_length, 0)
            # objects are taced in both clockwise and cc directions
            # to create a shadow polygon
            raycast_ended_r = False
            raycast_ended_l = False
            for a_i in range(0, 360, angle_step):
                if not raycast_ended_r:
                    ang1 = a_i + angle + angle_step
                    # create light ray to clollide with sprites' "pixels"
                    line_v = ray_v.rotate(ang1)
                    line = tuple(player_c_pos), player_c_pos + line_v
                    # "pixel" colisions
                    for s_rect in subrects2:
                        colis = s_rect.clipline(*line)  # the actual tracing happens here
                        # we stop as long as we found a single pixel that collides
                        # which is usally the pixel we want because pixel/texel rectc are sorted
                        if colis:
                            if DEBUG_DRAW:
                                pygame.draw.rect(surf, (22, 232, 111), s_rect, 1)
                            # subrects2.remove(s_rect)
                            break
                    if colis:
                        pt1 = colis[1]  # second, further, point
                        line_bk = (
                            line[1],
                            line[0],
                        )  # backwards light ray to create shadow outer contour
                        for s_rect in reversed(subrects1):
                            # texels are sorter in reverse order so backlight will touch the first one
                            colis2 = s_rect.clipline(*line_bk)
                            if colis2:
                                p2 = colis2[0]
                                # move backlight collision point away from player to exend
                                # shadow length
                                p2_off = Vector2(shadow_len, 0).rotate(
                                    ang1
                                )  # easier and faster rotation with vectors
                                p2 = tuple(p2 + p2_off)
                                cached = rays_cache.get(ang1, None)
                                if cached is not None:
                                    pt1_dist = Vector2(pt1).distance_squared_to(player_c_pos)
                                    pt2_dist = Vector2(p2).distance_squared_to(player_c_pos)
                                    cached_p1_dist = Vector2(cached[0]).distance_squared_to(
                                        player_c_pos
                                    )
                                    cached_p2_dist = Vector2(cached[1]).distance_squared_to(
                                        player_c_pos
                                    )
                                    is_inside = (
                                        pt1_dist > cached_p1_dist and pt2_dist < cached_p2_dist
                                    )
                                    is_outside = (
                                        pt2_dist < cached_p1_dist or pt1_dist > cached_p2_dist
                                    )
                                    if not is_inside and not is_outside:
                                        if pt1_dist > cached_p1_dist:
                                            pt1 = cached[0]
                                            cache_dirty = True
                                        if pt2_dist < cached_p2_dist:
                                            p2 = cached[1]
                                            cache_dirty = True
                                else:
                                    cache_dirty = True
                                if cache_dirty:
                                    rays_cache[ang1] = pt1, p2
                                pts1.append(pt1)
                                # insert points rather then append for proper
                                # polygon drawing ---> [insert, append] <---
                                pts2.insert(0, p2)  # that is of course not optimal for lists

                                if DEBUG_DRAW:
                                    pygame.draw.line(surf, (162, 194, 126), p2, colis2[0])
                                    pygame.draw.rect(surf, (22, 232, 111), s_rect, 1)
                                break
                        if DEBUG_DRAW:
                            pygame.draw.line(surf, (254, 222, 156), colis[0], colis[1])
                            pygame.draw.line(surf, (152, 184, 156), player_c_pos, colis[0])

                    else:
                        if DEBUG_DRAW:
                            pygame.draw.line(surf, (254, 222, 156), line[0], line[1])
                        raycast_ended_r = True
                if not raycast_ended_l:
                    ang2 = angle - a_i
                    line_v = ray_v.rotate(ang2)
                    line = tuple(player_c_pos), player_c_pos + line_v
                    for s_rect in subrects2:
                        colis = s_rect.clipline(*line)
                        if colis:
                            if DEBUG_DRAW:
                                pygame.draw.rect(surf, (22, 232, 111), s_rect, 1)
                            break
                    if colis:
                        pt1 = colis[1]
                        line_bk = line[1], line[0]
                        for s_rect in reversed(subrects1):
                            colis2 = s_rect.clipline(*line_bk)
                            if colis2:
                                p2 = colis2[0]
                                p2_off = Vector2(shadow_len, 0).rotate(ang2)
                                p2 = tuple(p2 + p2_off)
                                cached = rays_cache.get(ang2, None)
                                if cached is not None:
                                    pt1_dist = Vector2(pt1).distance_squared_to(player_c_pos)
                                    pt2_dist = Vector2(p2).distance_squared_to(player_c_pos)
                                    cached_p1_dist = Vector2(cached[0]).distance_squared_to(
                                        player_c_pos
                                    )
                                    cached_p2_dist = Vector2(cached[1]).distance_squared_to(
                                        player_c_pos
                                    )
                                    is_inside = (
                                        pt1_dist > cached_p1_dist and pt2_dist < cached_p2_dist
                                    )
                                    is_outside = (
                                        pt2_dist < cached_p1_dist or pt1_dist > cached_p2_dist
                                    )
                                    if not is_inside and not is_outside:
                                        if pt1_dist > cached_p1_dist:
                                            pt1 = cached[0]
                                            cache_dirty = True
                                        if pt2_dist < cached_p2_dist:
                                            p2 = cached[1]
                                            cache_dirty = True
                                else:
                                    cache_dirty = True
                                if cache_dirty:
                                    rays_cache[ang2] = pt1, p2
                                pts1.insert(0, pt1)
                                pts2.append(p2)

                                if DEBUG_DRAW:
                                    pygame.draw.line(surf, (162, 194, 126), p2, colis2[0])
                                    pygame.draw.rect(surf, (22, 232, 111), s_rect, 1)
                                break
                        if DEBUG_DRAW:
                            pygame.draw.line(surf, (254, 222, 156), colis[0], pt1)
                            pygame.draw.line(surf, (152, 184, 156), player_c_pos, colis[0])
                    else:
                        if DEBUG_DRAW:
                            pygame.draw.line(surf, (254, 222, 156), line[0], line[1])
                        raycast_ended_l = True

                if raycast_ended_l and raycast_ended_r:
                    break

                points = pts1 + pts2
                if len(points) > 2:
                    if DEBUG_DRAW:
                        pygame.draw.polygon(surf, (245, 100, 200), points, 1)
                    else:
                        # pts1 denote inner contour (closer to player)
                        # pts2 are outer contour
                        pygame.draw.polygon(surf, color, points)
            # end of raycasting

        light_spot.x = player.rect.centerx - LIGHT_SPOT_SIZE // 2
        light_spot.y = player.rect.centery - LIGHT_SPOT_SIZE // 2
        light_spot.draw(fog_surface, special_flags=pygame.BLEND_MIN)

        # fake blurring
        if BLUR_SHADOWS:
            the_pos = (
                player.rect.centerx - LIGHT_SPOT_SIZE // 2,
                player.rect.centery - LIGHT_SPOT_SIZE // 2,
            )
            lighto.blit(fog_surface, (0, 0), (*the_pos, LIGHT_SPOT_SIZE, LIGHT_SPOT_SIZE))
            if BLUR_SHADOWS > 1:
                l_blurred = pygame.transform.smoothscale(
                    lighto, (LIGHT_SPOT_SIZE // 4, LIGHT_SPOT_SIZE // 4)
                )
            l_blurred = pygame.transform.smoothscale(
                l_blurred, (LIGHT_SPOT_SIZE // 2, LIGHT_SPOT_SIZE // 2)
            )
            pygame.transform.scale(l_blurred, (LIGHT_SPOT_SIZE, LIGHT_SPOT_SIZE), lighto)
            fog_surface.blit(lighto, the_pos)

        screen.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_MULT)

        for y in range(0, fog_t_graph.nrows * fog_size_w, fog_size_w):
            c_tile_y = y // fog_size_w
            for x in range(0, fog_t_graph.ncols * fog_size_w, fog_size_w):
                c_tile_x = x // fog_size_w
                graph = fog_t_graph[c_tile_x, c_tile_y]
                fog_tile = fog_tiles[graph]
                screen.blit(fog_tile, (x, y), special_flags=pygame.BLEND_MULT)

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
