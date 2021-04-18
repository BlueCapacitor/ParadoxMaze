import tkinter as tk

from core.state import Result
from ui import tk_color


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
