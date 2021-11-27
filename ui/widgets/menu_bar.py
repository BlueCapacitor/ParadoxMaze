import tkinter as tk

from ui import tk_color
from ui.utilities.font import Font


class MenuBar(tk.Frame):

    def __init__(self, parent, display, back_page, colors, height=32, run_action=None, text=""):
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

        self.label = tk.Label(self, text=text, font=Font.LARGE.value,
                              bg=tk_color(colors[1]), fg=tk_color(colors[0]))
        self.label.grid(row=0, column=1, sticky=tk.NSEW)

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
