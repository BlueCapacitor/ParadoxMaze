import tkinter as tk
from math import ceil, log10

from core.state import Result
from ui import tk_color
from ui.utilities.font import Font
from ui.widgets.automatic_hide_scrollbar import AutomaticHideScrollbar


class ResultSelector(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=tk_color(colors[1]), highlightthickness=0)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.list_box = tk.Listbox(self, bg=tk_color(colors[1]), font=Font.MED_SMALL.value, width=26, bd=0,
                                   selectbackground=tk_color(colors[3]), activestyle=tk.NONE, selectborderwidth=2)
        self.list_box.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        self.scroll_bar = AutomaticHideScrollbar(self, orient=tk.VERTICAL, command=self.list_box.yview)
        self.scroll_bar.grid(row=0, column=0, sticky=tk.NSEW)

        self.list_box.config(yscrollcommand=self.scroll_bar.set)

        num_digits = ceil(log10(len(self.parent.results)))

        for alternative_number, result in enumerate(self.parent.results):
            result_status_text = \
                {Result.SUCCESS: "Success", Result.UNRECOVERABLE_PARADOX: "Paradox", Result.FAIL: "Fail"}[result[0]]

            colors = {Result.SUCCESS: ((0, 1, 0), (0, 0.5, 0), (0.5, 1, 0.5), (0, 0.25, 0)),
                      Result.UNRECOVERABLE_PARADOX: ((0, 0, 1), (0, 0, 0.5), (0.5, 0.5, 1), (0, 0, 0.25)),
                      Result.FAIL: ((1, 0, 0), (0.5, 0, 0), (1, 0.5, 0.5), (0.25, 0, 0))}[result[0]]

            text = "0" * (num_digits - len(str(alternative_number))) + str(alternative_number)

            self.list_box.insert(tk.END, f"Alternative {text} - {result_status_text}")
            self.list_box.itemconfig(alternative_number, bg=tk_color(colors[0]), selectbackground=tk_color(colors[1]),
                                     fg=tk_color(colors[3]), selectforeground=tk_color(colors[2]))

        self.list_box.bind('<<ListboxSelect>>', self.result_change)

    def result_change(self, *_):
        self.parent.alternative_result_change()

    @property
    def active_alternative(self):
        selection = self.list_box.curselection()
        if len(selection) == 0:
            self.list_box.activate(0)
            return 0
        else:
            return self.list_box.curselection()[0]
