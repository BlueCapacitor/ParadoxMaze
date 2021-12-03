"""
Created on Oct 10, 2020

@author: gosha
"""

from core.tiles.empty import EmptyTile
from core.tiles.target import TargetTile


class Board(object):

    def __init__(self, tiles):
        self.tiles = []
        dependent_tiles = {}

        for y in range(len(tiles)):
            self.tiles.append([])
            for x in range(len(tiles[y])):
                tile = tiles[y][x]
                if isinstance(tiles[y][x], EmptyTile):
                    self.tiles[y].append(tile)
                elif type(tile) in (tuple, list):
                    if type(tile[1]) in (tuple, list):
                        self.tiles[y].append(None)
                        dependent_tiles[(x, y)] = tile
                    elif type(tile[1]) in (dict,):
                        self.tiles[y].append(tile[0](x, y, **tile[1]))
                else:
                    self.tiles[y].append(tile(x, y))

        for items in dependent_tiles.items():
            x, y, tile, dep_x, dep_y = items[0][0], items[0][1], items[1][0], items[1][1][0], items[1][1][1]

            assert (dep_x, dep_y) not in dependent_tiles.keys()
            self.tiles[y][x] = tile(x, y, self.tiles[dep_y][dep_x])

        assert self.is_valid(), "Invalid board"

        self.has_time_travel = False
        for tile in self.list_tiles:
            if tile.is_time_travel:
                self.has_time_travel = True
                break

    @property
    def width(self):
        return len(self.tiles[0])

    @property
    def height(self):
        return len(self.tiles)

    @property
    def list_tiles(self):
        return sum(self.tiles, [])

    def is_valid(self):
        for row in self.tiles:
            if len(row) != self.width:
                print("test 1")
                return False
            for tile in row:
                if not(isinstance(tile, EmptyTile)):
                    print("test 2", tile)
                    return False
        return True

    def get_tile(self, x, y):
        return self.tiles[y][x]

    def get_targets(self):
        out = []
        for tile in self.list_tiles:
            if isinstance(tile, TargetTile):
                out.append(tile)

        return out

    def check_bounds(self, robot):
        return 0 <= robot.x < self.width and 0 <= robot.y < self.height
