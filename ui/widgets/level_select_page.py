from os import path, listdir

import tkinter as tk

from main import root_path
from ui import tk_color
from ui.utilities.csv_map import CSVMap
from ui.utilities.font import Font


class LevelSelectPage(tk.Frame):

    def __init__(self, display, buttons_per_row=5):
        super().__init__(display, padx=4, pady=4)
        self.display = display

        self.set = 1
        self.buttons_per_row = buttons_per_row

        self.level_buttons = []
        self.set_label = tk.Label(self, font=Font.LARGE.value)
        self.set_label.grid(row=0, column=1, columnspan=self.buttons_per_row - 2, sticky=tk.NSEW, padx=8, pady=8)

        self.left_button = tk.Label(self, font=Font.LARGE.value, text="-")
        self.left_button.grid(row=0, column=0, sticky=tk.NSEW, padx=8, pady=8)
        self.left_button.bind("<Button-1>", self.left)

        self.right_button = tk.Label(self, font=Font.LARGE.value, text="+")
        self.right_button.grid(row=0, column=self.buttons_per_row - 1, sticky=tk.NSEW, padx=8, pady=8)
        self.right_button.bind("<Button-1>", self.right)

        for column in range(self.buttons_per_row):
            self.grid_columnconfigure(column, weight=1)

        self.colors = None
        self.num_rows = 1

        self.redraw()

    levels_path = path.join(root_path, "levels")

    @property
    def set_path(self):
        return path.join(self.levels_path, f"set-{self.set:02}")

    @property
    def resource_path(self):
        return path.join(self.set_path, "resources")

    @property
    def valid_set(self):
        return path.isdir(self.set_path)

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
        color_file = open(path.join(root_path, self.resource_path, "set-colors.txt"), 'r')
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

        for row in range(1, self.num_rows + 1):
            self.rowconfigure(row, weight=0)

        self.num_rows = 1

        self.level_buttons = []

        self.read_state_from_file_system()

    def read_state_from_file_system(self):
        level_folders = listdir(self.set_path)
        level_folders.sort()
        for level_folder in level_folders:
            if level_folder.split('-')[0] != "level":
                continue

            number = int(level_folder.split('-')[-1])

            file_names = [f"{self.set}-{number}-map.csv", "instruction_text.md", "hint.md", "solution.txt"]
            file_contents = []

            for file_name in file_names:
                file_path = path.join(self.set_path, level_folder, file_name)
                with open(file_path, 'r') as file:
                    file_contents.append(file.read())

            code_file_path = path.join(self.set_path, level_folder, "code.txt")

            self.add_button(number, file_contents[0], code_file_path, *file_contents[1:])

    def add_button(self, number, csv_map_text, code_file_path, instruction_text, hint_text, solution):
        button = tk.Label(self, text=f"{self.set}-{number}", font=Font.LARGE.value,
                          bg=tk_color(self.colors[1]), fg=tk_color(self.colors[2]))
        button.bind("<Button-1>", lambda *_: self.load_level(csv_map_text, code_file_path, instruction_text, hint_text,
                                                             solution, number))
        row = (number - 1) // self.buttons_per_row + 1
        button.grid(row=row, column=(number - 1) % self.buttons_per_row,
                    sticky=tk.NSEW, padx=8, pady=8)

        self.grid_rowconfigure(row, weight=1)
        if row > self.num_rows:
            self.num_rows = row

        self.level_buttons.append(button)

    def load_level(self, csv_map_text, code_file_path, instruction_text, hint_text, solution, level_number):
        self.display.current_page = self.display.Page.CODING
        self.display.Page.CODING.value.load_level(CSVMap(csv_map_text), code_file_path, instruction_text, hint_text,
                                                  solution, self.colors, self.set, level_number)
