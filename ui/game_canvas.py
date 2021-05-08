import tkinter as tk
from math import floor, ceil, cos, sin

from ui import tk_color, inactive_charge_color, inactive_border_charge_color, charge_color, border_charge_color, \
    apply_robot_move_curve, apply_robot_turn_curve
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

    @property
    def p_time(self):
        return self.parent.p_time

    @property
    def tile_time(self):
        return round(self.time)

    @property
    def p_tile_time(self):
        return round(self.tile_time)

    @property
    def tile_time_changed(self):
        return self.p_time is None or self.tile_time != self.p_tile_time

    def set_colors(self, colors):
        self.canvas.config(bg=tk_color(colors[0]), highlightcolor=tk_color(colors[1]))

    def screen_coords(self, x, y):
        out_x = (x + 1) * self.tile_size
        out_y = (y + 1) * self.tile_size
        return out_x, out_y

    def draw(self, force_reset):
        self.canvas.delete(tk.ALL if self.tile_time_changed or force_reset else "robot")
        self.canvas.config(
            scrollregion=(0, 0, (self.board.width + 1) * self.tile_size, (self.board.height + 1) * self.tile_size))

        if self.tile_time_changed or force_reset:
            self.draw_board()

        self.draw_robots()

    def draw_board(self):
        time = self.tile_time if self.mode == "Global Time" else self.state.get_robot_with_charge(self.time)[1]
        for tile in self.board.list_tiles:
            self.draw_tile(tile, time)

    def draw_robots(self):
        if self.mode == "Global Time":
            for robot0 in self.state.get_robots_at_time(floor(self.time)):
                robot1 = self.state.get_robot_with_continuity_id(ceil(self.time), robot0.continuity_id)
                self.draw_intermediate_robot(floor(self.time), ceil(self.time), robot0, robot1)

        if self.mode == "Charge Remaining":
            current_robot, time = self.state.get_robot_with_charge(self.tile_time)
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

        self.draw_robot_shape(x, y, dx, dy, color, border, border_color, scale, robot.charge_remaining)

    def draw_intermediate_robot(self, time0, time1, robot0, robot1, color_function=None, border=2,
                                border_color_function=None, scale=0.75):
        if robot1 is None:
            if self.time == time0:
                self.draw_robot(robot0, color_function, border, border_color_function, scale)
        else:
            time_fraction = (self.time - time0) / (time1 - time0) if time0 != time1 else 0

            if color_function is None:
                color_function = charge_color
            if border_color_function is None:
                border_color_function = border_charge_color

            color = color_function(robot0.charge_remaining * (1 - time_fraction) +
                                   robot1.charge_remaining * time_fraction,
                                   robot0.initial_charge)
            border_color = border_color_function(robot0.charge_remaining * (1 - time_fraction) +
                                                 robot1.charge_remaining * time_fraction, robot0.initial_charge)

            x, y = self.screen_coords(*apply_robot_move_curve(time_fraction, robot0.x, robot1.x, robot0.y, robot1.y))
            angle = apply_robot_turn_curve(time_fraction, robot0.direction.angle, robot1.direction.angle)
            dx, dy = cos(angle), -sin(angle)
            charge_remaining = round(robot0.charge_remaining * (1 - time_fraction) +
                                     robot1.charge_remaining * time_fraction)

            self.draw_robot_shape(x, y, dx, dy, color, border, border_color, scale, charge_remaining)

    def draw_robot_shape(self, x, y, dx, dy, color, border, border_color, scale, charge_remaining):
        half_length = self.tile_size / 2 * scale

        x0, y0 = x + half_length * (-1 * dx - 0.5 * dy), y + half_length * (0.5 * dx - 1 * dy)
        x1, y1 = x - half_length * dx * 0.5, y - half_length * dy * 0.5
        x2, y2 = x + half_length * (-1 * dx + 0.5 * dy), y + half_length * (-0.5 * dx - 1 * dy)
        x3, y3 = x + half_length * dx, y + half_length * dy

        self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill=tk_color(color), width=border,
                                   outline=tk_color(border_color), tags=("robot",))
        self.canvas.create_text(x, y, text=str(charge_remaining),
                                fill="#000", width=self.tile_center_size, font=Font.SMALL.value, tags=("robot",))
