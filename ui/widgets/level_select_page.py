import os

import tkinter as tk

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
            code_file_path = "%s/%s/code.txt" % (self.set_path, level_folder)
            with open("%s/%s/%s-%s-map.csv" % (self.set_path, level_folder, self.set, number), 'r') as csv_map_file:
                csv_map_text = csv_map_file.read()

            instruction_text_path = "%s/%s/instruction_text.md" % (self.set_path, level_folder)
            if not os.path.exists(instruction_text_path):
                with open(instruction_text_path, 'x'):
                    pass

            with open(instruction_text_path, 'r') as instruction_text_file:
                instruction_text = instruction_text_file.read()

            self.add_button(number, csv_map_text, code_file_path, instruction_text)

    def add_button(self, number, csv_map_text, code_file_path, instruction_text):
        button = tk.Label(self, text="%s-%s" % (self.set, number), font=Font.LARGE.value,
                          bg=tk_color(self.colors[1]), fg=tk_color(self.colors[2]))
        button.bind("<Button-1>", lambda *_: self.load_level(csv_map_text, code_file_path, instruction_text, number))
        button.grid(row=(number - 1) // self.buttons_per_row + 1, column=(number - 1) % self.buttons_per_row,
                    sticky=tk.NSEW, padx=8, pady=8)
        self.grid_rowconfigure((number - 1) // self.buttons_per_row + 1, weight=1)
        self.level_buttons.append(button)

    def load_level(self, csv_map_text, code_file_path, instruction_text, level_number):
        self.display.current_page = self.display.Page.CODING
        self.display.Page.CODING.value.load_level(CSVMap(csv_map_text), code_file_path, instruction_text, self.colors,
                                                  self.set, level_number)
