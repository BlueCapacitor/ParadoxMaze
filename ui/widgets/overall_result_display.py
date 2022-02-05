import tkinter as tk

from core.state_v2 import Result
from ui import tk_color
from ui.utilities.font import Font


class OverallResultDisplay(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, height=20)
        self.parent = parent

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        result = parent.display.overall_result

        result_status_text = {Result.SUCCESS: "Success", Result.FAIL: "Fail"}[result]
        colors = {Result.SUCCESS: ((0, 1, 0), (0, 0.5, 0)), Result.FAIL: ((1, 0, 0), (0.5, 0, 0))}[result]
        self.config(bg=tk_color(colors[0]))
        label = tk.Label(self, text=result_status_text, fg=tk_color(colors[1]), bg=tk_color(colors[0]),
                         font=Font.NORMAL.value)
        label.grid(row=0, column=0, sticky=tk.NSEW)
