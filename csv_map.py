"""
Created on Oct 21, 2020

@author: gosha
"""
from board import Board
from robot import Direction, Robot
from tile import EmptyTile, WallTile, DestinationTile, PortalTile, TargetTile, \
    TimeGateTile, CloseTimedDoorTile, OpenTimedDoorTile, TimePortalTile, \
    ButtonTile, OpenLogicalDoorTile, LavaTile, HologramTile, \
    CloseLogicalDoorTile, OnToggleTile, OffToggleTile


class CSVMap(object):

    empty_symbol = ''
    wall_symbol = '0'
    lava_symbol = '1'
    hologram_symbol = '2'
    target_symbol = '@'
    time_gate_symbol = '*'
    close_timed_door_symbol = ')'
    open_timed_door_symbol = '('
    open_logical_door_symbol = '['
    close_logical_door_symbol = ']'
    time_portal_symbol = '>'
    button_symbol = '^'
    on_toggle_symbol = '+'
    off_toggle_symbol = '-'
    destination_symbols = tuple("abcdefghijklmnopqrstuvwxyz")
    portal_symbols = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    robot_start_symbols = {Direction.RIGHT: "$R", Direction.UP: "$U", Direction.LEFT: "$L", Direction.DOWN: "$D"}

    def __init__(self, text):
        self.cells = [[cell for cell in line.split(',')] for line in text.split('\n')]

        self.tiles = []

        for y in range(len(self.cells)):
            self.tiles.append([])
            for x in range(len(self.cells[y])):
                cell_text = self.cells[y][x].split(':')
                cell, args = cell_text[0], cell_text[1:]
                if cell == CSVMap.empty_symbol:
                    self.tiles[y].append(EmptyTile)
                elif cell == CSVMap.wall_symbol:
                    self.tiles[y].append(WallTile)
                elif cell == CSVMap.lava_symbol:
                    self.tiles[y].append(LavaTile)
                elif cell == CSVMap.hologram_symbol:
                    self.tiles[y].append(HologramTile)
                elif cell == CSVMap.target_symbol:
                    self.tiles[y].append(TargetTile)
                elif cell in CSVMap.destination_symbols:
                    self.tiles[y].append((DestinationTile, {"letter": cell}))
                elif cell in CSVMap.portal_symbols:
                    destination = self.find_cell(cell.lower())
                    assert destination is not None, "No '%s' found in csv file" % (cell.lower())
                    self.tiles[y].append((PortalTile, destination[0: 2]))
                elif cell == CSVMap.time_gate_symbol:
                    self.tiles[y].append((TimeGateTile, {"dt": int(args[0])}))
                elif cell == CSVMap.close_timed_door_symbol:
                    self.tiles[y].append((CloseTimedDoorTile, {"trigger_time": int(args[0])}))
                elif cell == CSVMap.open_timed_door_symbol:
                    self.tiles[y].append((OpenTimedDoorTile, {"trigger_time": int(args[0])}))
                elif cell == CSVMap.time_portal_symbol:
                    self.tiles[y].append((TimePortalTile, {"dest_t": int(args[0])}))
                elif cell == CSVMap.button_symbol:
                    self.tiles[y].append((ButtonTile, {"control_id": int(args[0])}))
                elif cell == CSVMap.open_logical_door_symbol:
                    self.tiles[y].append((OpenLogicalDoorTile, {"control_id": int(args[0])}))
                elif cell == CSVMap.close_logical_door_symbol:
                    self.tiles[y].append((CloseLogicalDoorTile, {"control_id": int(args[0])}))
                elif cell == CSVMap.on_toggle_symbol:
                    self.tiles[y].append((OnToggleTile, {"control_id": int(args[0])}))
                elif cell == CSVMap.off_toggle_symbol:
                    self.tiles[y].append((OffToggleTile, {"control_id": int(args[0])}))
                else:
                    self.tiles[y].append(EmptyTile)

    def find_cell(self, symbol):
        out = None

        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                if self.cells[y][x].split(':')[0] == symbol:
                    assert out is None, "More than one '%s' found in csv file" % symbol
                    out = (x, y) + tuple(self.cells[y][x].split(':')[1:])

        return out

    def build_board(self):
        return Board(self.tiles)

    def build_robot(self):
        for direction in CSVMap.robot_start_symbols.keys():
            pos = self.find_cell(CSVMap.robot_start_symbols[direction])
            if pos is not None:
                return Robot(pos[0], pos[1], direction, int(pos[2]), int(pos[2]))
