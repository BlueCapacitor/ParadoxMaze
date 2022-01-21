import tkinter as tk

from core.controller import Controller
from language.code import Code
from ui import tk_color
from ui.widgets.coding_box import CodeBox
from ui.widgets.instruction_display import InstructionDisplay
from ui.widgets.menu_bar import MenuBar
from ui.widgets.preview_canvas import PreviewCanvas


class CodingPage(tk.Frame):

    def __init__(self, display):
        super().__init__(display)
        self.display = display

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.p_time = None

        self.vertical_paned_window = None
        self.horizontal_paned_window = None
        self.preview_canvas = None
        self.menu_bar = None
        self.csv_map = None
        self.code_file_path = None
        self.colors = None
        self.bg = None
        self.board = None
        self.instruction_display = None
        self.code_box = None
        self.instruction_text = ""
        self.set_number = 0
        self.level_number = 0

        self.bind("<Configure>", self.resized)

    def load_level(self, csv_map, code_file_path, instruction_text, colors, set_number, level_number):
        self.csv_map = csv_map
        self.code_file_path = code_file_path
        self.instruction_text = instruction_text
        self.set_number = set_number
        self.level_number = level_number
        self.draw(colors)

    def draw(self, colors):
        self.colors = colors

        has_instructions = len(self.instruction_text) > 0

        self.config(bg=tk_color(self.colors[1]))

        if self.menu_bar is not None:
            self.menu_bar.destroy()

        self.menu_bar = MenuBar(self, self.display, self.display.Page.LEVEL_SELECT, self.colors,
                                run_action=self.run, text=f"Level {self.set_number}-{self.level_number}")
        self.menu_bar.grid(row=0, column=0, sticky=tk.NSEW)

        if self.vertical_paned_window is not None:
            self.vertical_paned_window.destroy()

        if has_instructions:
            self.vertical_paned_window = tk.PanedWindow(self, orient=tk.VERTICAL, borderwidth=0, sashwidth=8,
                                                        bg=tk_color(self.colors[1]))
            self.vertical_paned_window.grid(row=1, column=0, sticky=tk.NSEW)

        if self.instruction_display is not None:
            self.instruction_display.destroy()

        if has_instructions:
            self.instruction_display = InstructionDisplay(self.vertical_paned_window, self.colors, self.instruction_text)
            self.vertical_paned_window.add(self.instruction_display)

        if self.horizontal_paned_window is not None:
            self.horizontal_paned_window.destroy()

        self.horizontal_paned_window = tk.PanedWindow(self.vertical_paned_window if has_instructions else self,
                                                      orient=tk.HORIZONTAL, borderwidth=0, sashwidth=8,
                                                      bg=tk_color(self.colors[1]))
        if has_instructions:
            self.vertical_paned_window.add(self.horizontal_paned_window)
        else:
            self.horizontal_paned_window.grid(row=1, column=0, sticky=tk.NSEW)

        self.board = self.csv_map.build_board()

        # if self.preview_canvas is not None:
        #     self.preview_canvas.destroy()

        self.preview_canvas = PreviewCanvas(self.horizontal_paned_window, self.board, self.csv_map.build_robot())
        self.horizontal_paned_window.add(self.preview_canvas)

        self.preview_canvas.draw(True, colors=self.colors)

        if self.code_box is not None:
            self.code_box.destroy()

        self.code_box = CodeBox(self.horizontal_paned_window, self)
        self.horizontal_paned_window.add(self.code_box)
        self.code_box.load_file()

        width, height = self.display.winfo_width(), self.display.winfo_height()
        window_x, window_y = self.display.winfo_x(), self.display.winfo_y()
        self.display.geometry(f"{width - 1}x{height - 1}+{window_x}+{window_y}")
        self.update()
        self.display.update()
        self.display.update_idletasks()
        self.display.geometry(f"{width}x{height}+{window_x}+{window_y}")

    def resized(self, event):
        if len(self.instruction_text) > 0 and self.instruction_display is not None:
            max_instruction_height = self.instruction_display.max_height
            min_height = max(0, event.height - max_instruction_height - self.menu_bar.height -
                             self.horizontal_paned_window.cget("sashwidth") - 13)
            self.vertical_paned_window.paneconfig(self.horizontal_paned_window, minsize=min_height)

    def run(self, *_):
        robot = self.csv_map.build_robot()
        code = Code(robot, code=self.code_box.text)
        controller = Controller(self.board, robot, code)

        self.display.current_page = self.display.Page.CALCULATING

        results = controller.run()

        self.display.board = self.board
        self.display.results = results
        self.display.current_page = self.display.Page.STEP
        self.display.current_page.page.draw(self.colors, self.set_number, self.level_number)
