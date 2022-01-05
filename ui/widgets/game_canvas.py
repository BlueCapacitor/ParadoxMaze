import tkinter as tk
from math import floor, ceil, cos, pi, sin

from ui import tk_color, inactive_charge_color, inactive_border_charge_color, charge_color, \
    border_charge_color, \
    apply_robot_move_curve, apply_robot_turn_curve
from tiles import Drawings
from ui.utilities.font import Font
from ui.widgets.automatic_hide_scrollbar import AutomaticHideScrollbar


class GameCanvas(tk.Frame):

    def __init__(self, parent, tile_size=48, tile_center_size=32):
        super().__init__(parent)

        self.parent = parent
        self.tile_size = tile_size
        self.tile_ring_size = tile_size * 47 / 48
        self.tile_center_size = tile_center_size

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, width=(self.board.width + 1) * self.tile_size,
                                height=(self.board.height + 1) * self.tile_size,
                                scrollregion=(0, 0, (self.board.width + 1) * self.tile_size,
                                              (self.board.height + 1) * self.tile_size), highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

        self.scroll_v = AutomaticHideScrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_v.grid(row=0, column=1, sticky=tk.NSEW)

        self.scroll_h = AutomaticHideScrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_h.grid(row=1, column=0, sticky=tk.NSEW)

        self.canvas.config(xscrollcommand=self.scroll_h.set, yscrollcommand=self.scroll_v.set)

        self.p_time = None
        self.p_round_slice_time = None

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
    def tile_time(self):
        return round(self.time)

    @property
    def p_tile_time(self):
        return round(self.p_time)

    @property
    def tile_time_changed(self):
        return self.p_time is None or self.tile_time != self.p_tile_time

    def set_colors(self, colors):
        self.canvas.config(bg=tk_color(colors[3]))

    def screen_coords(self, x, y):
        out_x = (x + 1) * self.tile_size
        out_y = (y + 1) * self.tile_size
        return out_x, out_y

    def draw(self, force_reset, colors=None):
        if self.mode == "Global Time":
            if self.tile_time_changed or force_reset:
                self.canvas.delete(tk.ALL)
                self.draw_board()
            else:
                self.canvas.delete("robot")

            self.p_time = self.time

            for robot0 in self.state.get_robots_at_time(floor(self.time)):
                robot1 = self.state.get_robot_with_time_and_continuity_id(ceil(self.time), robot0.continuity_id)
                self.draw_intermediate_robot(self.time, floor(self.time), ceil(self.time), robot0, robot1)

        if self.mode == "Charge Remaining":
            charge0 = floor(self.time)
            charge1 = ceil(self.time)
            charge_fraction = (self.time - charge0) / (charge1 - charge0) if charge0 != charge1 else 0

            robots_with_this_charge = self.state.get_all_robots_with_charge(charge0)

            assert len(robots_with_this_charge) <= 2, \
                "Something is wrong: there are more than two robot traces with the same charge"
            assert len(robots_with_this_charge) >= 1, \
                "Something is wrong: there are no robots with charge %s" % charge0

            current_robot0, initial_time = min(robots_with_this_charge,
                                               key=lambda robot_tuple: robot_tuple[0].continuity_id)

            robots_with_next_charge = self.state.get_all_robots_with_charge(charge1)

            assert len(robots_with_next_charge) <= 2, \
                "Something is wrong: there are more than two robot traces with the same charge"
            assert len(robots_with_next_charge) >= 1, \
                "Something is wrong: there are no robots with charge %s" % charge1

            current_robot1, final_time = max(robots_with_next_charge,
                                             key=lambda robot_tuple: robot_tuple[0].continuity_id)

            slice_time = initial_time * (1 - charge_fraction) + final_time * charge_fraction
            time0 = floor(slice_time)
            time1 = ceil(slice_time)

            if force_reset or round(slice_time) != self.p_round_slice_time:
                self.canvas.delete(tk.ALL)
                self.draw_board()

                self.p_round_slice_time = round(slice_time)
            else:
                self.canvas.delete("robot")

            self.canvas.config(
                scrollregion=(0, 0, (self.board.width + 1) * self.tile_size, (self.board.height + 1) * self.tile_size))

            robots = self.state.get_robots_at_time(time0)

            for robot0 in robots:
                if robot0 != current_robot0:
                    robot1 = self.state.get_robot_with_time_and_continuity_id(time1, robot0.continuity_id)
                    greyed_out = robot0.charge_remaining != charge0 or final_time != initial_time + 1
                    self.draw_intermediate_robot(slice_time, time0, time1, robot0, robot1,
                                                 color_function=inactive_charge_color if greyed_out else None,
                                                 border_color_function=inactive_border_charge_color
                                                 if greyed_out else None)

            self.draw_intermediate_robot(self.time, charge0, charge1, current_robot0, current_robot1)

        if self.mode == "Preview":
            self.draw_board()
            for robot in self.state.get_robots_at_time(self.time):
                self.draw_robot(robot)

        if colors is not None:
            self.set_colors(colors)

    def draw_board(self):
        self.canvas.create_rectangle(*self.screen_coords(-0.5, -0.5),
                                     *self.screen_coords(self.board.width - 0.5, self.board.height - 0.5),
                                     fill=tk_color((0, 0, 0)), width=0)

        time = self.tile_time if self.mode == "Global Time" else self.state.get_robot_with_charge(self.tile_time)[1]
        for tile in self.board.list_tiles:
            self.draw_tile(tile, time)

    def draw_tile(self, tile, time):
        drawing = tile.get_drawing(self.state, time)
        self.draw_square(*self.screen_coords(tile.x, tile.y), self.tile_ring_size, drawing[0])
        self.draw_square(*self.screen_coords(tile.x, tile.y), self.tile_center_size, drawing[1])
        for procedure in drawing[2:]:
            match procedure:
                case Drawings.RECT, size, color:
                    self.draw_square(*self.screen_coords(tile.x, tile.y), size * self.tile_center_size, color)

                case Drawings.TEXT, text, color:
                    self.canvas.create_text(*self.screen_coords(tile.x, tile.y), text=text, fill=tk_color(color),
                                            width=self.tile_center_size)

                case Drawings.FLARE, diagonal_size, rectilinear_size, color:
                    self.draw_flare(*self.screen_coords(tile.x, tile.y), diagonal_size * self.tile_center_size,
                                    rectilinear_size * self.tile_center_size, color)

                case Drawings.CIRCLE, radius, color:
                    self.draw_circle(*self.screen_coords(tile.x, tile.y), radius * self.tile_center_size, color)

                case Drawings.REG_POLY, n, radius, color:
                    self.draw_regular_poly(*self.screen_coords(tile.x, tile.y), n, radius * self.tile_center_size,
                                           color)

                case Drawings.REG_POLY, n, radius, angle_offset, color:
                    self.draw_regular_poly(*self.screen_coords(tile.x, tile.y), n, radius * self.tile_center_size,
                                           color, angle_offset=angle_offset)

                case Drawings.CORNERS, distance, width, color:
                    self.draw_corners(*self.screen_coords(tile.x, tile.y), distance * self.tile_ring_size,
                                      width * self.tile_ring_size, color)

    def draw_square(self, x, y, side, color, border=0):
        self.canvas.create_rectangle(x + side / 2, y - side / 2,
                                     x - side / 2, y + side / 2,
                                     fill=tk_color(color),
                                     width=border, outline="#000")

    def draw_circle(self, x, y, radius, color, border=0):
        self.canvas.create_oval(x + radius, y - radius,
                                x - radius, y + radius,
                                fill=tk_color(color),
                                width=border, outline="#000")

    def draw_flare(self, x, y, d, rl, color):
        self.canvas.create_polygon(x + rl / 2, y, x + d / 2, y + d / 2, x, y + rl / 2, x - d / 2, y + d / 2,
                                   x - rl / 2, y, x - d / 2, y - d / 2, x, y - rl / 2, x + d / 2, y - d / 2,
                                   fill=tk_color(color), width=0)

    def draw_regular_poly(self, x, y, n, r, color, angle_offset=0):
        points = zip((x + r * sin((i + angle_offset) * 2 * pi / n) for i in range(n)),
                     (y + r * cos((i + angle_offset) * 2 * pi / n) for i in range(n)))
        self.canvas.create_polygon(*points, fill=tk_color(color), width=0)

    def draw_corners(self, x, y, distance, width, color):
        inner = distance - width / 2
        outer = distance + width / 2
        full = self.tile_ring_size / 2
        # self.canvas.create_rectangle(x - full, y - full, x + full, y + full,
        #                              fill=tk_color((0, 1, 0)), width=0)
        for dx in (-1, 1):
            for dy in (-1, 1):
                self.canvas.create_polygon(x + inner * dx, y + full * dy,
                                           x + outer * dx, y + full * dy,
                                           x + full * dx, y + outer * dy,
                                           x + full * dx, y + inner * dy,
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

    def draw_intermediate_robot(self, time, time0, time1, robot0, robot1, color_function=None, border=2,
                                border_color_function=None, scale=0.75):
        if robot1 is None:
            if time == time0:
                self.draw_robot(robot0, color_function, border, border_color_function, scale)
        else:
            time_fraction = (time - time0) / (time1 - time0) if time0 != time1 else 0

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
