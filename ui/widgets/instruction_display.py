import tkinter as tk

from ui import tk_color
from ui.utilities.markdown import Markdown
from ui.widgets.scrolled_md_text import ScrolledMDText


class InstructionDisplay(tk.Frame):
    def __init__(self, parent, colors, text):
        super().__init__(parent, bg=tk_color(colors[1]))

        self.colors = colors
        if len(text) > 0:
            self.markdown = Markdown(text)
            self.scrolled_md_text = ScrolledMDText(self, self.markdown, self.colors)
            self.scrolled_md_text.grid(row=0, column=0, sticky=tk.NSEW)
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

    @property
    def max_height(self):
        return self.scrolled_md_text.max_height
