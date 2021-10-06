import pygame as pg


from .flood_iter import Flood


class InfiniteMap:
    def __init__(self):
        self.map = {}
        self.default = 0

    def get(self, pos):
        if pos in self.map:
            return self.map[pos]
        return self.default

    def set(self, pos, value):
        self.map[pos] = value


class FogArea:
    def __init__(self, rect_w, rect_h, width, height, max_visibility):
        self.rect_w = rect_w
        self.rect_h = rect_h
        self.width = width
        self.height = height
        self.discovered = InfiniteMap()
        self.max_steps = max_visibility
        self._trans_tile = pg.Surface((rect_w, rect_h), pg.SRCALPHA)
        self._trans_tile.fill((0, 0, 0, 0))
        self._fog_of_war = self._trans_tile.copy()
        self._fog_of_war.fill((0, 0, 0, 125))
        self._unknown_area_tile = self._trans_tile.copy()
        self._unknown_area_tile.fill((0, 0, 0))

    def pos_to_grid(self, pos):
        fixed_x = pos[0] - pos[0] % self.rect_w
        fixed_y = pos[1] - pos[1] % self.rect_h
        grid_x = fixed_x / self.rect_w
        grid_y = fixed_y / self.rect_h
        return grid_x, grid_y

    def grid_to_pos(self, grid):
        return grid[0] * self.rect_w, grid[1] * self.rect_h

    def in_visible_range(self, player_pos, check_pos):
        grid_pos = self.grid_to_pos(check_pos)
        for x, y, _ in Flood(player_pos[0], player_pos[1], self.max_steps):
            if (x, y) == grid_pos:
                return True
        return False

    def get_mask(self, player_pos):
        pos = self.pos_to_grid(player_pos)
        int_pos = int(pos[0]), int(pos[1])

        mask = pg.Surface((self.rect_w * self.width, self.rect_h * self.height), pg.SRCALPHA)

        for i in range(self.width):
            for j in range(self.height):
                tile_pos = (i, j)
                if self.discovered.get(tile_pos):
                    if self.in_visible_range(pos, tile_pos):
                        pass
                    else:
                        mask.blit(self._fog_of_war, self.grid_to_pos(tile_pos))
                else:
                    mask.blit(self._unknown_area_tile, self.grid_to_pos(tile_pos))
