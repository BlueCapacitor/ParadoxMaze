import tkinter as tk

from ui.widgets.automatic_hide_scrollbar import AutomaticHideScrollbar
from ui.widgets.md_text import MDText


class ScrolledMDText(tk.Frame):
    def __init__(self, parent, reference_widget, *args, max_ratio=0.25, **kwargs):
        super().__init__(parent, height=256)

        self.parent = parent
        self.reference_widget = reference_widget
        self.max_ratio = max_ratio

        self.pack_propagate(False)

        self.md_text = MDText(self, *args, **kwargs)
        self.md_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scrollbar = AutomaticHideScrollbar(self, orient=tk.VERTICAL, command=self.md_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.md_text.config(yscrollcommand=self.scrollbar.set)

        self.bind("<Configure>", self.resize)

    def resize(self, *_args, **_kwargs):
        self.config(height=min(self.reference_widget.winfo_height() * self.max_ratio, self.md_text.preferred_height))
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
