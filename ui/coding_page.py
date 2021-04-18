import tkinter as tk
from tkinter import ttk

from core.controller import Controller
from core.instruction_set import InstructionSet
from ui import tk_color
from ui.coding_box import CodeBox
from ui.menu_bar import MenuBar
from ui.preview_canvas import PreviewCanvas


class CodingPage(tk.Frame):

    def __init__(self, display):
        super().__init__(display)
        self.display = display

        self.code_box = CodeBox(self)
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

        self.menu_bar = MenuBar(self, self.display, self.display.Page.LEVEL_SELECT, self.colors,
                                run_action=self.run)
        self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        self.board = self.csv_map.build_board()

        if self.preview_canvas is not None:
            self.preview_canvas.destroy()

        self.preview_canvas = PreviewCanvas(self, self.board, self.csv_map.build_robot())
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
