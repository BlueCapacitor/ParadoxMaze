import tkinter as tk

from ui.utilities.font import Font


class SimpleTextPage(tk.Frame):
    def __init__(self, display, text):
        super().__init__(display)
        self.label = tk.Label(self, text=text, font=Font.HUGE.value)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
