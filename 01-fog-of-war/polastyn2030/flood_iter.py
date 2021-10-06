from __future__ import annotations


from typing import Tuple, Set, Iterator, List


class Flood:
    def __init__(self, start_x: int, start_y: int, max_iterations: int):
        self.start_x = start_x
        self.start_y = start_y
        self.max_iterations = max_iterations

    def __iter__(self) -> "FloodIter":
        return FloodIter(self).start()


class FloodIter:
    iterator: Iterator[Tuple[int, int]]

    def __init__(self, flood_info: Flood):
        self.flood_info = flood_info
        self.visited_places: Set[Tuple[int, int]] = set()
        self.routes: Set[Tuple[int, int]] = set()
        self.asking_routes: Set[Tuple[int, int]] = set()
        self.possible_movement = PossibleMovement()
        self.first_time: bool = True
        self.iterator = iterator((self.flood_info.start_x, self.flood_info.start_y), self.possible_movement,
                                 self.flood_info.max_iterations)

    def start(self):
        self.iterator = iterator((self.flood_info.start_x, self.flood_info.start_y), self.possible_movement,
                                 self.flood_info.max_iterations)
        return self

    def __iter__(self) -> "FloodIter":
        return self.start()

    def __next__(self) -> Tuple[int, int, "PossibleMovement"]:
        if self.first_time:
            self.first_time = False
            return self.flood_info.start_x, self.flood_info.start_y, self.possible_movement
        return next(self.iterator) + (self.possible_movement,)


class PossibleMovement:
    def __init__(self):
        self.left = False
        self.up = False
        self.right = False
        self.down = False

        self.left_teleport: Tuple[int, int] = (-1, -1)
        self.up_teleport: Tuple[int, int] = (-1, -1)
        self.right_teleport: Tuple[int, int] = (-1, -1)
        self.down_teleport: Tuple[int, int] = (-1, -1)

    def get_movement(self, pos: Tuple[int, int]):
        raw = self.raw_movement(pos)
        ret: Set[Tuple[int, int]] = set()

        if self.left:
            ret.add(raw[0])

        if self.up:
            ret.add(raw[1])

        if self.right:
            ret.add(raw[2])

        if self.down:
            ret.add(raw[3])
        return ret

    def raw_movement(self, pos: Tuple[int, int], reset: bool = True):
        _pos = pos
        ret: List[Tuple[int, int]] = []

        if self.left_teleport != (-1, -1):
            pos = self.left_teleport
            if reset:
                self.left_teleport = (-1, -1)
        ret.append((pos[0] - 1, pos[1]))
        pos = _pos

        if self.up_teleport != (-1, -1):
            pos = self.up_teleport
            if reset:
                self.up_teleport = (-1, -1)
        ret.append((pos[0], pos[1] - 1))
        pos = _pos

        if self.right_teleport != (-1, -1):
            pos = self.right_teleport
            if reset:
                self.right_teleport = (-1, -1)
        ret.append((pos[0] + 1, pos[1]))
        pos = _pos

        if self.down_teleport != (-1, -1):
            pos = self.down_teleport
            if reset:
                self.down_teleport = (-1, -1)
        ret.append((pos[0], pos[1] + 1))

        return ret

    def all_true(self):
        self.left = True
        self.up = True
        self.up = True
        self.down = True

    def all_false(self):
        self.left = False
        self.up = False
        self.up = False
        self.down = False


def iterator(start_pos: Tuple[int, int], is_correct: PossibleMovement, max_depth: int) -> Iterator[Tuple[int, int]]:
    routes: Set[Tuple[int, int]] = set()
    visited: Set[Tuple[int, int]] = set()

    def get_correct_spread(check_pos: Tuple[int, int]) -> Set[Tuple[int, int]]:
        return is_correct.get_movement(check_pos).difference(visited)

    routes.update(get_correct_spread(start_pos))
    cnt = 0

    while len(routes):
        if cnt >= max_depth:
            break
        new_routes = set()
        old_routes = set()
        for rout in routes:
            visited.add(rout)
            new_routes.update(get_correct_spread(rout))
            old_routes.add(rout)
            yield rout
        cnt += 1

        routes.update(new_routes)
        routes.difference_update(old_routes)
