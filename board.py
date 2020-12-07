'''
Created on Oct 10, 2020

@author: gosha
'''

from tile import EmptyTile, TargetTile


class Board(object):

    def __init__(self, tiles):
        self.tiles = []
        dependentTiles = {}

        for y in range(len(tiles)):
            self.tiles.append([])
            for x in range(len(tiles[y])):
                tile = tiles[y][x]
                if(isinstance(tiles[y][x], EmptyTile)):
                    self.tiles[y].append(tile)
                elif(type(tile) in (tuple, list)):
                    if(type(tile[1]) in (tuple, list)):
                        self.tiles[y].append(None)
                        dependentTiles[(x, y)] = tile
                    elif(type(tile[1]) in (dict,)):
                        self.tiles[y].append(tile[0](x, y, **tile[1]))
                else:
                    self.tiles[y].append(tile(x, y))

        for items in dependentTiles.items():
            x, y, tile, depX, depY = items[0][0], items[0][1], items[1][0], items[1][1][0], items[1][1][1]

            assert (depX, depY) not in dependentTiles.keys()
            self.tiles[y][x] = tile(x, y, self.tiles[depY][depX])

        assert self.isValid(), "Invalid board"

    @property
    def width(self):
        return(len(self.tiles[0]))

    @property
    def height(self):
        return(len(self.tiles))

    @property
    def listTiles(self):
        return(sum(self.tiles, []))

    def isValid(self):
        for row in self.tiles:
            if(len(row) != self.width):
                return(False)
            for tile in row:
                if(not(isinstance(tile, EmptyTile))):
                    return(False)
        return(True)

    def getTile(self, x, y):
        return(self.tiles[y][x])

    def getTargets(self):
        out = []
        for tile in self.listTiles:
            if(isinstance(tile, TargetTile)):
                out.append(tile)

        return(out)

    def checkBounds(self, robot):
        return(0 <= robot.x < self.width and 0 <= robot.y < self.height)
