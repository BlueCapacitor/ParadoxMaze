"""
Created on Oct 14, 2020

@author: gosha
"""

from enum import Enum
from math import ceil
import os

from core.controller import Controller
from display.csv_map import CSVMap
from core.instruction_set import InstructionSet
from core.state import Result, State
import tkinter as tk
import tkinter.font as tk_font
import tkinter.ttk as ttk

from display import tk_color, charge_color, inactive_charge_color, inactive_border_charge_color, border_charge_color


class Display(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.results = []

        class Page(Enum):
            LOADING = Display.SimpleTextPage(self, "Loading...")
            CALCULATING = Display.SimpleTextPage(self, "Calculating...")
            NO_POSSIBILITIES = Display.SimpleTextPage(self, "Fail: All possibilities lead to paradox")
            STEP = Display.StepPage(self)
            LEVEL_SELECT = Display.LevelSelectPage(self)
            CODING = Display.CodingPage(self)

            def __init__(self, page):
                self.page = page
                self.page.grid(row=0, column=0, sticky=tk.NSEW)

        self.Page = Page

        self.current_page = self.Page.LOADING

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, results):
        self._results = []

        self.overall_result = Result.SUCCESS
        for result in results:
            if result[0] != Result.UNRECOVERABLE_PARADOX:
                self._results.append(result)
                self.overall_result |= result[0]

        if len(self._results) == 0:
            self._results = results

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, page):
        self._current_page = page
        self._current_page.page.tkraise()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.update()

    class Font(Enum):
        HUGE = ("Veranda", 64)
        LARGE = ("Veranda", 32)
        NORMAL = ("Veranda", 16)
        SMALL = ("Veranda", 8)

        def measure(self, window, text):
            return tk_font.Font(root=window, font=self.value).measure(text)

    class SimpleTextPage(tk.Frame):

        def __init__(self, display, text):
            super().__init__(display)
            self.label = tk.Label(self, text=text, font=Display.Font.HUGE.value)
            self.label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

    class StepPage(tk.Frame):

        def __init__(self, display):
            super().__init__(display)
            self.display = display
            self.drawn = False

            self.menu_bar = None
            self.game_canvas = None
            self.result_selector = None
            self.mode_tkvar = None
            self.tk_frame = None
            self.time_slider = None
            self.playing_tkvar = None
            self.play_checkbox = None
            self.charge_mode_time_display = None

        def draw(self, colors):
            if self.drawn:
                self.redraw(colors)
            else:
                self.menu_bar = Display.MenuBar(self, self.display, self.display.Page.CODING, colors)
                self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

                self.game_canvas = Display.GameCanvas(self)
                self.game_canvas.grid(row=2, column=1, columnspan=2, sticky=tk.NSEW)

                self.result_selector = Display.ResultSelector(self, colors)
                self.result_selector.grid(row=2, column=0, rowspan=4, sticky=tk.NSEW)

                modes = ("Global Time", "Charge Remaining")
                self.mode_tkvar = tk.StringVar(self, value=modes[0])
                self.mode_tkvar.trace('w', self.update_mode)
                self.tk_frame = tk.Frame(self)
                for column, mode in enumerate(modes):
                    button = tk.Radiobutton(self.tk_frame, text=mode, variable=self.mode_tkvar, value=mode,
                                            indicatoron=False)
                    button.grid(row=2, column=column, sticky=tk.NSEW)
                    self.tk_frame.grid_columnconfigure(column, weight=1)
                self.tk_frame.grid_rowconfigure(0, weight=1)
                self.tk_frame.grid(row=3, column=1, columnspan=2, sticky=tk.NSEW)

                tick_interval = max(1, ceil((self.state.max_time - self.state.min_time) / 25))
                self.time_slider = tk.Scale(self, from_=self.state.min_time, to=self.state.max_time,
                                            orient=tk.HORIZONTAL, command=self.time_change, tickinterval=tick_interval)
                self.time_slider.grid(row=4, column=2, sticky=tk.NSEW)

                self.playing_tkvar = tk.BooleanVar(self, False, "playing_tkvar")
                self.play_checkbox = tk.Checkbutton(self, variable=self.playing_tkvar, text="play")
                self.play_checkbox.grid(row=4, column=1, sticky=tk.NSEW)

                self.charge_mode_time_display = tk.Label(self, text="", bg="#FFF")
                self.charge_mode_time_display.grid(row=5, column=1, columnspan=2, sticky=tk.NSEW)

                self.grid_columnconfigure(0, weight=0)
                self.grid_columnconfigure(1, weight=0)
                self.grid_columnconfigure(2, weight=1)
                self.grid_rowconfigure(2, weight=1)
                self.grid_rowconfigure(3, weight=0)
                self.grid_rowconfigure(4, weight=0)
                self.grid_rowconfigure(5, weight=0)

                self.game_canvas.draw()
                self.tick()

                self.drawn = True

        def redraw(self, colors):
            self.menu_bar.destroy()
            self.menu_bar = Display.MenuBar(self, self.display, self.display.Page.CODING, colors)
            self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

            self.result_selector.destroy()
            self.result_selector = Display.ResultSelector(self, colors)
            self.result_selector.grid(row=2, column=0, rowspan=4, sticky=tk.NSEW)

            self.update_mode()

            self.game_canvas.draw()

        @property
        def board(self):
            return self.display.board

        @property
        def results(self):
            return self.display.results

        @property
        def active_result_index(self):
            return self.result_selector.alternative_tkvar.get()

        @property
        def active_result(self):
            return self.results[self.active_result_index] if len(self.results) > self.active_result_index else None

        @property
        def time(self):
            return self.time_slider.get()

        @property
        def mode(self):
            return self.mode_tkvar.get()

        @property
        def state(self):
            return self.active_result[1]

        def update_mode(self, *_args, **_kwargs):
            if self.mode == "Global Time":
                tick_interval = max(1, ceil((self.state.max_time - self.state.min_time) / 25))
                self.time_slider.config(from_=self.state.min_time,
                                        to=self.state.max_time,
                                        tickinterval=tick_interval)
                self.time = self.state.min_time

            elif self.mode == "Charge Remaining":
                tick_interval = max(1, ceil((self.state.min_charge - self.state.max_charge) / 25))
                self.time_slider.config(from_=self.state.max_charge,
                                        to=self.state.min_charge,
                                        tickinterval=tick_interval)
                self.time = self.state.max_charge

        @time.setter
        def time(self, value):
            self.time_slider.set(value)

        def tick(self, *_):
            if self.playing_tkvar.get():
                if ((self.time < self.state.max_time) if self.mode == "Global Time" else (
                        self.time > self.state.min_charge)):
                    self.time += 1 if self.mode == "Global Time" else -1
                else:
                    self.play_checkbox.deselect()

            if self.state.max_time - self.state.min_time > 100:
                self.after(ceil(75000 / (self.state.max_time - self.state.min_time)), self.tick)
            else:
                self.after(750, self.tick)

        def time_change(self, *_):
            if self.mode == "Global Time":
                self.charge_mode_time_display.config(text="", bg="#FFF")
            else:
                time = self.state.get_robot_with_charge(self.time)[1]
                self.charge_mode_time_display.config(text="Time: %s" % time, bg=tk_color(
                    charge_color(self.time, self.state.max_charge)))
            self.game_canvas.draw()

        def alternative_result_change(self, *_):
            self.game_canvas.draw()

    class ResultSelector(tk.Frame):

        def __init__(self, parent, colors):
            super().__init__(parent, bg=tk_color(colors[1]))
            self.parent = parent
            self.alternative_tkvar = tk.IntVar()
            self.alternative_tkvar.trace('w', self.parent.alternative_result_change)

            self.button_container = tk.Frame(self, bg=tk_color(colors[1]))
            self.button_container.grid(row=0, column=0, sticky=tk.NSEW)
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

            for alternative_number, result in enumerate(parent.results):
                result_status_text = \
                    {Result.SUCCESS: "Success", Result.UNRECOVERABLE_PARADOX: "Paradox", Result.FAIL: "Fail"}[result[0]]
                button_color = \
                    {Result.SUCCESS: (0, 1, 0), Result.UNRECOVERABLE_PARADOX: (0, 0, 1), Result.FAIL: (1, 0, 0)}[
                        result[0]]
                button = tk.Radiobutton(self.button_container,
                                        text="Alternative %s - %s" % (alternative_number, result_status_text),
                                        variable=self.alternative_tkvar, value=alternative_number, indicatoron=False,
                                        bg=tk_color(button_color))
                button.grid(row=alternative_number, column=0, sticky=tk.E + tk.N + tk.W)

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
                                    width=self.tile_center_size, font=Display.Font.SMALL.value)

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

    class LevelSelectPage(tk.Frame):

        def __init__(self, display, buttons_per_row=5):
            super().__init__(display, padx=4, pady=4)
            self.display = display

            self.set = 1
            self.buttons_per_row = buttons_per_row

            self.level_buttons = []
            self.set_label = tk.Label(self, font=Display.Font.LARGE.value)
            self.set_label.grid(row=0, column=1, columnspan=self.buttons_per_row - 2, sticky=tk.NSEW, padx=8, pady=8)

            self.left_button = tk.Label(self, font=Display.Font.LARGE.value, text="-")
            self.left_button.grid(row=0, column=0, sticky=tk.NSEW, padx=8, pady=8)
            self.left_button.bind("<Button-1>", self.left)

            self.right_button = tk.Label(self, font=Display.Font.LARGE.value, text="+")
            self.right_button.grid(row=0, column=self.buttons_per_row - 1, sticky=tk.NSEW, padx=8, pady=8)
            self.right_button.bind("<Button-1>", self.right)

            for column in range(self.buttons_per_row):
                self.grid_columnconfigure(column, weight=1)

            self.colors = None
            self.redraw()

        levels_path = "levels"

        @property
        def set_path(self):
            return "%s/set-%02d" % (self.levels_path, self.set)

        @property
        def resource_path(self):
            return "%s/resources" % self.set_path

        @property
        def valid_set(self):
            return os.path.isdir(self.set_path)

        @property
        def is_first_set(self):
            return self.set == 1

        @property
        def is_last_set(self):
            self.set += 1
            out = not self.valid_set
            self.set -= 1
            return out

        def left(self, *_):
            if not self.is_first_set:
                self.set -= 1
                self.redraw()

        def right(self, *_):
            if not self.is_last_set:
                self.set += 1
                self.redraw()

        def get_colors(self):
            color_file = open("%s/set-colors.txt" % self.resource_path, 'r')
            colors = tuple(map(lambda s: tuple(map(float, s.split(", "))), color_file.read().split('\n')))
            color_file.close()
            return colors

        def redraw(self):
            self.colors = self.get_colors()

            self.config(bg=tk_color(self.colors[0]))
            self.set_label.config(bg=tk_color(self.colors[0]), fg=tk_color(self.colors[1]))

            self.set_label.config(text="Set %s" % self.set)

            self.left_button.config(
                bg=tk_color(self.colors[3]) if self.is_first_set else tk_color(self.colors[1]),
                fg=tk_color(self.colors[2]))
            self.right_button.config(
                bg=tk_color(self.colors[3]) if self.is_last_set else tk_color(self.colors[1]),
                fg=tk_color(self.colors[2]))

            for button in self.level_buttons:
                button.destroy()

            self.level_buttons = []

            self.read_state_from_file_system()

        def read_state_from_file_system(self):
            level_folders = os.listdir(self.set_path)
            level_folders.sort()
            for level_folder in level_folders:
                if level_folder.split('-')[0] != "level":
                    continue

                number = int(level_folder.split('-')[-1])
                csv_map_file = open("%s/%s/%s-%s-map.csv" % (self.set_path, level_folder, self.set, number), 'r')
                code_file_path = "%s/%s/code.txt" % (self.set_path, level_folder)
                csv_map_text = csv_map_file.read()
                csv_map_file.close()

                self.add_button(number, csv_map_text, code_file_path)

        def add_button(self, number, csv_map_text, code_file_path):
            button = tk.Label(self, text="%s-%s" % (self.set, number), font=Display.Font.LARGE.value,
                              bg=tk_color(self.colors[1]), fg=tk_color(self.colors[2]))
            button.bind("<Button-1>", lambda *_: self.load_level(csv_map_text, code_file_path))
            button.grid(row=(number - 1) // self.buttons_per_row + 1, column=(number - 1) % self.buttons_per_row,
                        sticky=tk.NSEW, padx=8, pady=8)
            self.grid_rowconfigure((number - 1) // self.buttons_per_row + 1, weight=1)
            self.level_buttons.append(button)

        def load_level(self, csv_map_text, code_file_path):
            self.display.current_page = self.display.Page.CODING
            self.display.Page.CODING.value.load_level(CSVMap(csv_map_text), code_file_path, self.colors)

    class CodingPage(tk.Frame):

        def __init__(self, display):
            super().__init__(display)
            self.display = display

            self.code_box = Display.CodeBox(self)
            self.code_box.grid(row=1, column=2, sticky=tk.NSEW)

            self.separator = ttk.Separator(self, orient=tk.VERTICAL)
            self.separator.grid(row=1, column=1)

            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(2, weight=1)

            self.preview_canvas = None
            self.menu_bar = None
            self.csv_map = None
            self.code_file_path = None
            self.colors = None
            self.bg = None
            self.board = None

        def load_level(self, csv_map, code_file_path, colors):
            self.csv_map = csv_map
            self.code_file_path = code_file_path
            self.draw(colors)

        def draw(self, colors):
            self.colors = colors

            self.bg = tk_color(self.colors[0])

            if self.menu_bar is not None:
                self.menu_bar.destroy()

            self.menu_bar = Display.MenuBar(self, self.display, self.display.Page.LEVEL_SELECT, self.colors,
                                            run_action=self.run)
            self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

            self.board = self.csv_map.build_board()

            if self.preview_canvas is not None:
                self.preview_canvas.destroy()

            self.preview_canvas = Display.PreviewCanvas(self, self.board, self.csv_map.build_robot())
            self.preview_canvas.grid(row=1, column=0, sticky=tk.NSEW)

            self.preview_canvas.draw()
            self.code_box.load_file()

        def run(self, *_):
            instructions = InstructionSet(self.code_box.text)

            robot = self.csv_map.build_robot()
            controller = Controller(self.board, robot, instructions)

            self.display.current_page = self.display.Page.CALCULATING

            results = controller.run()

            self.display.board = self.board
            self.display.results = results
            self.display.current_page = self.display.Page.STEP
            self.display.current_page.page.draw(self.colors)

    class CodeBox(tk.Frame):

        def __init__(self, coding_page):
            super().__init__(coding_page)
            self.coding_page = coding_page

            self.do_not_overwrite_file = False

            self.text_box = Display.TextWithModifiedCallback(self, wrap=tk.NONE, font=Display.Font.NORMAL,
                                                             tabs=(Display.Font.NORMAL.measure(self, ' ' * 2),))
            self.text_box.grid(row=0, column=0, sticky=tk.NSEW)
            self.scroll_v = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.text_box.yview)
            self.scroll_v.grid(row=0, column=1, sticky=tk.NSEW)
            self.scroll_h = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text_box.xview)
            self.scroll_h.grid(row=1, column=0, sticky=tk.NSEW)
            self.text_box.config(yscrollcommand=self.scroll_v.set, xscrollcommand=self.scroll_h.set)

            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

            self.text_box.bind("<Return>", self.enter)
            self.text_box.bind('}', self.close_brace)

            self.text_box.bind("<<TextModified>>", self.save)

        def current_indentation(self):
            text = self.text_box.get("0.0", tk.INSERT)
            indentation = 0
            for line in text.split('\n'):
                indentation += line.split("//")[0].count('{') - line.split("//")[0].count('}')
            return indentation

        def character_before_cursor(self):
            return self.text_box.get("insert - 1 char", tk.INSERT)

        def enter(self, *_):
            self.text_box.insert(tk.INSERT, '\n' + '\t' * self.current_indentation())
            return "break"

        def close_brace(self, *_):
            if self.character_before_cursor() == '\t':
                self.text_box.delete("insert - 1 char", tk.INSERT)

        def load_file(self):
            self.do_not_overwrite_file = True
            file_path = self.coding_page.code_file_path
            file = open(file_path, 'r')
            self.text_box.delete("0.0", tk.END)
            self.text_box.insert(tk.END, file.read())
            file.close()
            self.do_not_overwrite_file = False

        def save(self, *_):
            if not self.do_not_overwrite_file:
                file_path = self.coding_page.code_file_path
                file = open(file_path, 'w')
                file.flush()
                file.write(self.text)
                file.close()

        @property
        def text(self):
            text = self.text_box.get("0.0", "end")
            if len(text) > 0 and text[-1] == '\n':
                text = text[:-1]
            return text

    class TextWithModifiedCallback(tk.Text):

        def __init__(self, *args, **kwargs):
            tk.Text.__init__(self, *args, **kwargs)

            self._orig = self._w + "_orig"
            self.tk.call("rename", self._w, self._orig)
            self.tk.createcommand(self._w, self._proxy)

        def _proxy(self, command, *args):
            cmd = (self._orig, command) + args

            result = self.tk.call(cmd)
            # try:
            #     result = self.tk.call(cmd)
            # except Exception:
            #     return

            if command in ("insert", "delete", "replace"):
                self.event_generate("<<TextModified>>")

            return result

    class MenuBar(tk.Frame):

        def __init__(self, parent, display, back_page, colors, height=32, run_action=None):
            super().__init__(parent, bg=tk_color(colors[1]))

            self.parent = parent
            self.display = display
            self.back_page = back_page
            self.height = height

            self.grid_rowconfigure(0, weight=0)
            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)

            self.back_button = tk.Canvas(self, width=self.height, height=self.height, bg=tk_color(colors[1]),
                                         highlightthickness=0, relief=tk.RAISED, bd=2)

            arrow_size = self.height * 3 / 4
            arrow_tl = self.height * 1 / 8
            self.back_button.create_polygon(arrow_tl, arrow_tl + arrow_size / 2,
                                            arrow_tl + arrow_size / 2, arrow_tl,
                                            arrow_tl + arrow_size / 2, arrow_tl + arrow_size / 4,
                                            arrow_tl + arrow_size, arrow_tl + arrow_size / 4,
                                            arrow_tl + arrow_size, arrow_tl + arrow_size * 3 / 4,
                                            arrow_tl + arrow_size / 2, arrow_tl + arrow_size * 3 / 4,
                                            arrow_tl + arrow_size / 2, arrow_tl + arrow_size,
                                            arrow_tl, arrow_tl + arrow_size / 2,
                                            fill=tk_color(colors[2]))

            self.back_button.xview_moveto(0)
            self.back_button.yview_moveto(0)

            self.back_button.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W, padx=2.5, pady=2.5)
            self.back_button.bind("<Button-1>", self.go_back)

            if run_action is not None:
                self.run_button = tk.Canvas(self, width=self.height, height=self.height, bg=tk_color(colors[1]),
                                            highlightthickness=0, relief=tk.RAISED, bd=2)

                arrow_size = self.height * 3 / 4
                arrow_tl = self.height * 1 / 8
                self.run_button.create_polygon(arrow_tl, arrow_tl,
                                               arrow_tl + arrow_size, arrow_tl + arrow_size / 2,
                                               arrow_tl, arrow_tl + arrow_size,
                                               arrow_tl, arrow_tl,
                                               fill=tk_color(colors[2]))

                self.run_button.xview_moveto(0)
                self.run_button.yview_moveto(0)

                self.run_button.grid(row=0, column=2, sticky=tk.N + tk.S + tk.E, padx=2.5, pady=2.5)
                self.run_button.bind("<Button-1>", run_action)

        def go_back(self, *_):
            self.display.current_page = self.back_page
