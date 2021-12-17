import tkinter as tk

from core.controller import Controller
from core.instruction_set import InstructionSet
from ui import tk_color
from ui.widgets.coding_box import CodeBox
from ui.widgets.instruction_display import InstructionDisplay
from ui.widgets.menu_bar import MenuBar
from ui.widgets.preview_canvas import PreviewCanvas


class CodingPage(tk.Frame):

    def __init__(self, display):
        super().__init__(display)
        self.display = display

        self.code_box = CodeBox(self)
        self.code_box.grid(row=2, column=1, sticky=tk.NSEW)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.p_time = None

        self.preview_canvas = None
        self.menu_bar = None
        self.csv_map = None
        self.code_file_path = None
        self.colors = None
        self.bg = None
        self.board = None
        self.instruction_display = None
        self.instruction_text = ""
        self.set_number = 0
        self.level_number = 0

    def load_level(self, csv_map, code_file_path, instruction_text, colors, set_number, level_number):
        self.csv_map = csv_map
        self.code_file_path = code_file_path
        self.instruction_text = instruction_text
        self.set_number = set_number
        self.level_number = level_number
        self.draw(colors)

    def draw(self, colors):
        self.colors = colors

        self.bg = tk_color(self.colors[0])

        if self.menu_bar is not None:
            self.menu_bar.destroy()

        self.menu_bar = MenuBar(self, self.display, self.display.Page.LEVEL_SELECT, self.colors,
                                run_action=self.run, text=f"Level {self.set_number}-{self.level_number}")
        self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        if self.instruction_display is not None:
            self.instruction_display.destroy()

        self.instruction_display = InstructionDisplay(self, self.colors, self.instruction_text)
        self.instruction_display.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

        self.board = self.csv_map.build_board()

        if self.preview_canvas is not None:
            self.preview_canvas.destroy()

        self.preview_canvas = PreviewCanvas(self, self.board, self.csv_map.build_robot())
        self.preview_canvas.grid(row=2, column=0, sticky=tk.NSEW)

        self.preview_canvas.draw(True, colors=self.colors)
        self.code_box.load_file()

        width, height = self.display.winfo_width(), self.display.winfo_height()
        window_x, window_y = self.display.winfo_x(), self.display.winfo_y()
        self.display.geometry(f"{width - 1}x{height - 1}+{window_x}+{window_y}")
        self.update()
        self.display.update()
        self.display.update_idletasks()
        self.display.geometry(f"{width}x{height}+{window_x}+{window_y}")

    def run(self, *_):
        instructions = InstructionSet(self.code_box.text)

        robot = self.csv_map.build_robot()
        controller = Controller(self.board, robot, instructions)

        self.display.current_page = self.display.Page.CALCULATING

        results = controller.run()

        self.display.board = self.board
        self.display.results = results
        self.display.current_page = self.display.Page.STEP
        self.display.current_page.page.draw(self.colors, self.set_number, self.level_number)
