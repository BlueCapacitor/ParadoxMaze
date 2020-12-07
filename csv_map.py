'''
Created on Oct 21, 2020

@author: gosha
'''
from board import Board
from robot import Direction, Robot
from tile import EmptyTile, WallTile, DestinationTile, PortalTile, TargetTile, \
    TimeGateTile, CloseTimedDoorTile, OpenTimedDoorTile, TimePortalTile, \
    ButtonTile, OpenLogicalDoorTile


class CSVMap(object):

    emptySymbol = ''
    wallSymbol = '0'
    targetSymbol = '@'
    timeGateSymbol = '*'
    closeTimedDoorSymbol = ')'
    openTimedDoorSymbol = '('
    openLogicalDoorSymbol = '['
    closeLogicalDoorSymbol = ']'
    timePortalSymbol = '>'
    buttonSymbol = '^'
    destinationSymbols = tuple("abcdefghijklmnopqrstuvwxyz")
    portalSymbols = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    robotStartSymbols = {Direction.RIGHT: "$R", Direction.UP: "$U", Direction.LEFT: "$L", Direction.DOWN: "$D"}

    def __init__(self, fileName):
        file = open(fileName, 'r')
        text = file.read()
        self.cells = [[cell for cell in line.split(',')] for line in text.split('\n')]

        self.tiles = []

        for y in range(len(self.cells)):
            self.tiles.append([])
            for x in range(len(self.cells[y])):
                cellText = self.cells[y][x].split(':')
                cell, args = cellText[0], cellText[1:]
                if(cell == CSVMap.emptySymbol):
                    self.tiles[y].append(EmptyTile)
                elif(cell == CSVMap.wallSymbol):
                    self.tiles[y].append(WallTile)
                elif(cell == CSVMap.targetSymbol):
                    self.tiles[y].append(TargetTile)
                elif(cell in CSVMap.destinationSymbols):
                    self.tiles[y].append((DestinationTile, {"letter": cell}))
                elif(cell in CSVMap.portalSymbols):
                    destination = self.findCell(cell.lower())
                    assert destination is not None, "No '%s' found in csv file"
                    self.tiles[y].append((PortalTile, destination[0: 2]))
                elif(cell == CSVMap.timeGateSymbol):
                    self.tiles[y].append((TimeGateTile, {"dt": int(args[0])}))
                elif(cell == CSVMap.closeTimedDoorSymbol):
                    self.tiles[y].append((CloseTimedDoorTile, {"triggerTime": int(args[0])}))
                elif(cell == CSVMap.openTimedDoorSymbol):
                    self.tiles[y].append((OpenTimedDoorTile, {"triggerTime": int(args[0])}))
                elif(cell == CSVMap.timePortalSymbol):
                    self.tiles[y].append((TimePortalTile, {"destT": int(args[0])}))
                elif(cell == CSVMap.buttonSymbol):
                    self.tiles[y].append((ButtonTile, {"controlID": int(args[0])}))
                elif(cell == CSVMap.openLogicalDoorSymbol):
                    self.tiles[y].append((OpenLogicalDoorTile, {"controlID": int(args[0])}))
                else:
                    self.tiles[y].append(EmptyTile)

    def findCell(self, symbol):
        out = None

        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                if(self.cells[y][x].split(':')[0] == symbol):
                    assert out is None, "More than one '%s' found in csv file" % (symbol)
                    out = (x, y) + tuple(self.cells[y][x].split(':')[1:])

        return(out)

    def buildBoard(self):
        return(Board(self.tiles))

    def buildRobot(self):
        for direction in CSVMap.robotStartSymbols.keys():
            pos = self.findCell(CSVMap.robotStartSymbols[direction])
            if(pos is not None):
                return(Robot(pos[0], pos[1], direction, int(pos[2]), int(pos[2])))
