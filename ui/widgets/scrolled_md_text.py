import tkinter as tk

from ui import tk_color
from ui.widgets.automatic_hide_scrollbar import AutomaticHideScrollbar
from ui.widgets.md_text import MDText


class ScrolledMDText(tk.Frame):
    def __init__(self, parent, markdown, colors, *args, max_ratio=0.25, **kwargs):
        super().__init__(parent, height=256, bg=tk_color(colors[1]))

        self.parent = parent
        self.max_ratio = max_ratio

        self.pack_propagate(False)

        self.md_text = MDText(self, markdown, colors, *args, **kwargs)
        self.md_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scrollbar = AutomaticHideScrollbar(self, orient=tk.VERTICAL, command=self.md_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.md_text.config(yscrollcommand=self.scrollbar.set)

        self.bind("<Configure>", self.resize)

    @property
    def max_height(self):
        return self.md_text.preferred_height

    def resize(self, *_args, **_kwargs):
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
