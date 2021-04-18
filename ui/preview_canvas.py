import tkinter as tk

from core.state import State
from ui.game_canvas import GameCanvas


class PreviewCanvas(GameCanvas):

    def __init__(self, parent, board, robot_start, tile_size=45, tile_center_size=30,
                 tile_flare_horizontal_vertical_size=20, tile_flare_diagonal_size=10):
        self._board = board
        self.robot_start = robot_start

        self._state = State(board)
        self.state.robot_log = {0: [robot_start]}
        self._time = 0

        super().__init__(parent, tile_size=tile_size, tile_center_size=tile_center_size,
                         tile_flare_horizontal_vertical_size=tile_flare_horizontal_vertical_size,
                         tile_flare_diagonal_size=tile_flare_diagonal_size)

    @property
    def board(self):
        return self._board

    @property
    def state(self):
        return self._state

    @property
    def time(self):
        return self._time

    def draw_robots(self):
        self.draw_robot(self.robot_start)

    def draw_board(self):
        for tile in self.board.list_tiles:
            self.draw_tile(tile, self.time)

    def destroy(self):
        self.canvas.delete(tk.ALL)
        super().destroy()
