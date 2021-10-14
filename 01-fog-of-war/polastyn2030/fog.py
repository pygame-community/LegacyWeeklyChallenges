from __future__ import annotations


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

    def remove(self, pos):
        if pos in self.map:
            del self.map[pos]

    def clear(self):
        self.map = {}


class FogArea:
    def __init__(self, rect_w, rect_h, max_visibility):
        self.rect_w = rect_w
        self.rect_h = rect_h
        self.discovered = InfiniteMap()
        self.lighted_area = InfiniteMap()
        self.more_lighted_area = InfiniteMap()
        self.max_steps = max_visibility
        self._smooth_trans = 60
        self._semi_trans = 100
        self._fog_of_war = 125
        self._unknown = 255
        self._trans_tile = pg.Surface((rect_w, rect_h), pg.SRCALPHA)
        self._trans_tile.fill((0, 0, 0, 0))

        self._created_tiles: dict[int, pg.Surface] = {}

    def _get_tile(self, trans):
        if trans in self._created_tiles:
            return self._created_tiles[trans]

        copy = self._trans_tile.copy()
        copy.fill((0, 0, 0, trans))
        self._created_tiles[trans] = copy
        return copy

    def pos_to_grid(self, pos):
        fixed_x = pos[0] - pos[0] % self.rect_w
        fixed_y = pos[1] - pos[1] % self.rect_h
        grid_x = fixed_x / self.rect_w
        grid_y = fixed_y / self.rect_h
        return grid_x, grid_y

    def grid_to_pos(self, grid):
        return grid[0] * self.rect_w, grid[1] * self.rect_h

    def get_mask(self, size: tuple[int, int]):
        mask = pg.Surface(size, pg.SRCALPHA)
        x_grid = (size[0] - size[0] % self.rect_w) // self.rect_w
        y_grid = (size[1] - size[1] % self.rect_h) // self.rect_h

        i = 0
        while i <= x_grid:
            j = 0
            while j <= y_grid:
                tile_pos = (i, j)
                if self.discovered.get(tile_pos):
                    if self.lighted_area.get(tile_pos):
                        if self.more_lighted_area.get(tile_pos):
                            by = self.more_lighted_area.get(tile_pos)
                            mask.blit(
                                self._get_tile(self._smooth_trans + by * 5),
                                self.grid_to_pos(tile_pos),
                            )
                        else:
                            mask.blit(
                                self._get_tile(self._semi_trans),
                                self.grid_to_pos(tile_pos),
                            )
                    else:
                        mask.blit(self._get_tile(self._fog_of_war), self.grid_to_pos(tile_pos))

                        if self.more_lighted_area.get(tile_pos):
                            self.more_lighted_area.remove(tile_pos)
                else:
                    mask.blit(self._get_tile(self._unknown), self.grid_to_pos(tile_pos))
                j += 1
            i += 1
        return mask

    def draw(self, screen: pg.Surface):
        screen.blit(self.get_mask(screen.get_size()), (0, 0))

    def logic(self, player):
        self.lighted_area.clear()

        pos = self.pos_to_grid(player.pos)
        pos = (pos[0] + 1, pos[1] + 1)

        for x, y, step, check in Flood(pos[0], pos[1], self.max_steps):
            check.all_true()
            self.lighted_area.set((x, y), 1)
            self.discovered.set((x, y), 1)
            # self.more_lighted_area.set((x, y), step + 1)

        for x, y, step, check in Flood(pos[0], pos[1], self.max_steps // 2):
            check.all_true()
            self.more_lighted_area.set((x, y), step + 1)

    def lighted_up(self, pos):
        return self.lighted_area.get(self.pos_to_grid(pos))
