import tkinter as tk

from ui import tk_color
from ui.utilities.markdown import Markdown
from ui.widgets.md_text import MDText


class InstructionDisplay(tk.Frame):
    def __init__(self, parent, colors, text):
        super().__init__(parent, bg=tk_color(colors[0]))

        self.parent = parent
        self.colors = colors
        if len(text) > 0:
            self.markdown = Markdown(text)
            self.md_text = MDText(self, self.markdown, self.colors, bg=tk_color(self.colors[0]),
                                  highlightthickness=0, bd=0)
            self.md_text.grid(row=0, column=0, sticky=tk.NSEW)
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
