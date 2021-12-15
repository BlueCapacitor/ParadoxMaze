import tkinter as tk

from core.state import Result
from ui import tk_color
from ui.utilities.font import Font


class ResultSelector(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=tk_color(colors[1]))
        self.parent = parent
        self.alternative_tkvar = tk.IntVar()
        self.alternative_tkvar.trace('w', self.result_change)

        self.button_container = tk.Frame(self, bg=tk_color(colors[1]))
        self.button_container.grid(row=0, column=0, sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.buttons = []

        for alternative_number, result in enumerate(self.parent.results):
            result_status_text = \
                {Result.SUCCESS: "Success", Result.UNRECOVERABLE_PARADOX: "Paradox", Result.FAIL: "Fail"}[result[0]]
            self.buttons.append(tk.Radiobutton(self.button_container,
                                               text="Alternative %s - %s" % (alternative_number, result_status_text),
                                               variable=self.alternative_tkvar, value=alternative_number,
                                               indicatoron=False))

            self.buttons[-1].grid(row=alternative_number, column=0, sticky=tk.E + tk.N + tk.W)

        self.recolor()

    def result_change(self, *_):
        self.recolor()
        self.parent.alternative_result_change()

    def recolor(self):
        for alternative_number, result in enumerate(self.parent.results):
            button_colors = {Result.SUCCESS: ((0, 1, 0), (0, 0.25, 0), (0, 0.75, 0)),
                             Result.UNRECOVERABLE_PARADOX: ((0, 0, 1), (0, 0, 0.25), (0, 0, 0.75)),
                             Result.FAIL: ((1, 0, 0), (0.25, 0, 0), (0.75, 0, 0))}[result[0]]
            button = self.buttons[alternative_number]
            active = alternative_number == self.alternative_tkvar.get()
            button.config(bg=tk_color(button_colors[0 + 2 * active]), fg=tk_color(button_colors[1]),
                          selectcolor=tk_color(button_colors[0 + 2 * active]))
