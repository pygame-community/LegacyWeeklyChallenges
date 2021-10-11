# Copyright <2021> <gresm - user on github.com> - MIT LICENSE
#
# Permission is hereby granted, free of charge,
# to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction,
# including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

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
    iterator: Iterator[Tuple[int, int, int]]

    def __init__(self, flood_info: Flood):
        self.flood_info = flood_info
        self.visited_places: Set[Tuple[int, int]] = set()
        self.routes: Set[Tuple[int, int]] = set()
        self.asking_routes: Set[Tuple[int, int]] = set()
        self.possible_movement = PossibleMovement()
        self.first_time: bool = True
        self.iterator = iterator(
            (self.flood_info.start_x, self.flood_info.start_y),
            self.possible_movement,
            self.flood_info.max_iterations,
        )

    def start(self):
        self.iterator = iterator(
            (self.flood_info.start_x, self.flood_info.start_y),
            self.possible_movement,
            self.flood_info.max_iterations,
        )
        return self

    def __iter__(self) -> "FloodIter":
        return self.start()

    def __next__(self) -> Tuple[int, int, int, "PossibleMovement"]:
        if self.first_time:
            self.first_time = False
            return (
                self.flood_info.start_x,
                self.flood_info.start_y,
                0,
                self.possible_movement,
            )
        return next(self.iterator) + (self.possible_movement,)


class PossibleMovement:
    def __init__(self):
        self.left = False
        self.up = False
        self.right = False
        self.down = False

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

    # noinspection PyMethodMayBeStatic
    def raw_movement(self, pos: Tuple[int, int]):
        ret: List[Tuple[int, int]] = [
            (pos[0] - 1, pos[1]),
            (pos[0], pos[1] - 1),
            (pos[0] + 1, pos[1]),
            (pos[0], pos[1] + 1),
        ]

        return ret

    def all_true(self):
        self.left = True
        self.up = True
        self.right = True
        self.down = True

    def all_false(self):
        self.left = False
        self.up = False
        self.right = False
        self.down = False


def iterator(
    start_pos: Tuple[int, int], is_correct: PossibleMovement, max_depth: int
) -> Iterator[Tuple[int, int, int]]:

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
            yield rout + (cnt,)
        cnt += 1

        routes.update(new_routes)
        routes.difference_update(old_routes)
