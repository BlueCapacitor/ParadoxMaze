import tkinter as tk

from core.state import State
from ui import tk_color
from ui.widgets.game_canvas import GameCanvas


class PreviewCanvas(GameCanvas):

    def __init__(self, parent, board, robot_start, tile_size=48, tile_center_size=32):
        self._board = board
        self.robot_start = robot_start

        self._state = State(board)
        self.state.robot_log = {0: [robot_start]}
        self._time = 0

        super().__init__(parent, tile_size=tile_size, tile_center_size=tile_center_size)

    @property
    def board(self):
        return self._board

    @property
    def state(self):
        return self._state

    @property
    def time(self):
        return self._time

    @property
    def mode(self):
        return "Preview"

    def draw_robots(self):
        self.draw_robot(self.robot_start)

    def draw_board(self):
        self.canvas.create_rectangle(*self.screen_coords(-0.5, -0.5),
                                     *self.screen_coords(self.board.width - 0.5, self.board.height - 0.5),
                                     fill=tk_color((0, 0, 0)))

        for tile in self.board.list_tiles:
            self.draw_tile(tile, self.time)

    def destroy(self):
        self.canvas.delete(tk.ALL)
        super().destroy()
