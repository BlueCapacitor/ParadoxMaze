import tkinter as tk

from ui import tk_color, inactive_charge_color, inactive_border_charge_color, charge_color, border_charge_color
from ui.font import Font


class GameCanvas(tk.Frame):

    def __init__(self, parent, tile_size=45, tile_center_size=30, tile_flare_horizontal_vertical_size=20,
                 tile_flare_diagonal_size=10):
        super().__init__(parent)

        self.parent = parent
        self.tile_size = tile_size
        self.tile_center_size = tile_center_size
        self.tile_flare_horizontal_verticalSize = tile_flare_horizontal_vertical_size
        self.tile_flare_diagonal_size = tile_flare_diagonal_size

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, width=(self.board.width + 1) * self.tile_size,
                                height=(self.board.height + 1) * self.tile_size, scrollregion=(
                0, 0, (self.board.width + 1) * self.tile_size, (self.board.height + 1) * self.tile_size))
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

        self.scroll_v = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_v.grid(row=0, column=1, sticky=tk.NSEW)

        self.scroll_h = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_h.grid(row=1, column=0, sticky=tk.NSEW)

        self.canvas.config(xscrollcommand=self.scroll_h.set, yscrollcommand=self.scroll_v.set)

    @property
    def display(self):
        return self.parent.display

    @property
    def board(self):
        return self.display.board

    @property
    def result(self):
        return self.parent.active_result[0]

    @property
    def state(self):
        return self.parent.state

    @property
    def mode(self):
        return self.parent.mode

    @property
    def time(self):
        return self.parent.time

    def set_colors(self, colors):
        self.canvas.config(bg=tk_color(colors[0]), highlightcolor=tk_color(colors[1]))

    def screen_coords(self, x, y):
        out_x = (x + 1) * self.tile_size
        out_y = (y + 1) * self.tile_size
        return out_x, out_y

    def draw(self):
        self.canvas.delete(tk.ALL)
        self.canvas.config(
            scrollregion=(0, 0, (self.board.width + 1) * self.tile_size, (self.board.height + 1) * self.tile_size))

        self.draw_board()
        self.draw_robots()

    def draw_board(self):
        time = self.time if self.mode == "Global Time" else self.state.get_robot_with_charge(self.time)[1]
        for tile in self.board.list_tiles:
            self.draw_tile(tile, time)

    def draw_robots(self):
        if self.mode == "Global Time":
            for robot in self.state.get_robots_at_time(self.time):
                self.draw_robot(robot)
        if self.mode == "Charge Remaining":
            current_robot, time = self.state.get_robot_with_charge(self.time)
            for robot in self.state.get_robots_at_time(time):
                if robot != current_robot:
                    self.draw_robot(robot, color_function=inactive_charge_color,
                                    border_color_function=inactive_border_charge_color)
            self.draw_robot(current_robot)

    def draw_tile(self, tile, time):
        colors = tile.get_colors(self.state, time)
        self.draw_square(*self.screen_coords(tile.x, tile.y), self.tile_size, colors[0], border=1)
        self.draw_square(*self.screen_coords(tile.x, tile.y), self.tile_center_size, colors[1])
        if len(colors) >= 3:
            self.draw_flare(*self.screen_coords(tile.x, tile.y), self.tile_flare_diagonal_size,
                            self.tile_flare_horizontal_verticalSize, colors[2])
        text = tile.get_text(self.state, time)
        self.canvas.create_text(*self.screen_coords(tile.x, tile.y), text=text[0], fill=tk_color(text[1]),
                                width=self.tile_center_size)

    def draw_square(self, x, y, side, color, border=0):
        self.canvas.create_rectangle(x + side / 2, y - side / 2,
                                     x - side / 2, y + side / 2,
                                     fill=tk_color(color),
                                     width=border, outline="#000")

    def draw_flare(self, x, y, d, hv, color):
        self.canvas.create_polygon(x + hv / 2, y, x + d / 2, y + d / 2, x, y + hv / 2, x - d / 2, y + d / 2,
                                   x - hv / 2, y, x - d / 2, y - d / 2, x, y - hv / 2, x + d / 2, y - d / 2,
                                   fill=tk_color(color), width=0)

    def draw_robot(self, robot, color_function=None, border=2, border_color_function=None, scale=0.75):
        if color_function is None:
            color_function = charge_color
        if border_color_function is None:
            border_color_function = border_charge_color
        color = color_function(robot.charge_remaining, robot.initial_charge)
        border_color = border_color_function(robot.charge_remaining, robot.initial_charge)

        x, y = self.screen_coords(robot.x, robot.y)
        dx, dy = robot.direction.dx, robot.direction.dy
        half_length = self.tile_size / 2 * scale

        x0, y0 = x + half_length * (-1 * dx - 0.5 * dy), y + half_length * (0.5 * dx - 1 * dy)
        x1, y1 = x - half_length * dx * 0.5, y - half_length * dy * 0.5
        x2, y2 = x + half_length * (-1 * dx + 0.5 * dy), y + half_length * (-0.5 * dx - 1 * dy)
        x3, y3 = x + half_length * dx, y + half_length * dy

        self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill=tk_color(color), width=border,
                                   outline=tk_color(border_color))
        self.canvas.create_text(*self.screen_coords(robot.x, robot.y), text=str(robot.charge_remaining),
                                fill="#000",
                                width=self.tile_center_size, font=Font.SMALL.value)
