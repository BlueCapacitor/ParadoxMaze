from core.board import Board
from core.robot import Direction, Robot
from tiles.button import ButtonTile
from tiles.close_logical_door import CloseLogicalDoorTile
from tiles.close_time_door import CloseTimedDoorTile
from tiles.destination import DestinationTile
from tiles.hologram import HologramTile
from tiles.lava import LavaTile
from tiles.off_toggle import OffToggleTile
from tiles.on_toggle import OnToggleTile
from tiles.open_logical_door import OpenLogicalDoorTile
from tiles.open_time_door import OpenTimedDoorTile
from tiles.portal import PortalTile
from tiles.q_door import QDoor
from tiles.target import TargetTile
from tiles.time_gate import TimeGateTile
from tiles.time_portal import TimePortalTile
from tiles.wall import WallTile
from tiles.empty import EmptyTile


class CSVMap:
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
    q_door_symbol = '|'
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
                elif cell == CSVMap.q_door_symbol:
                    self.tiles[y].append((QDoor, {"control_id": int(args[0]),
                                                  "properties": [[c == "+" for c in args[a]] for a in range(1, 3)]}))
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

    def find_cells(self, symbol):
        out = []

        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                if self.cells[y][x].split(':')[0] == symbol:
                    out.append((x, y) + tuple(self.cells[y][x].split(':')[1:]))

        return out

    def build_board(self):
        return Board(self.tiles)

    def build_robots(self, code):
        robots = []
        robot_number = 0
        for direction in CSVMap.robot_start_symbols.keys():
            for position in self.find_cells(CSVMap.robot_start_symbols[direction]):
                robots.append(Robot(position[0], position[1], direction, int(position[2]), int(position[2]),
                                    code.copy_code() if code is not None else None))
                robot_number += 1
        return robots
