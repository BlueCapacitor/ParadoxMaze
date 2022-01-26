import tkinter as tk

from ui.utilities.markdown import Markdown
from ui.widgets.scrolled_md_text import ScrolledMDText


class HintWindow(tk.Toplevel):
    def __init__(self, parent, text, colors):
        super().__init__(parent)

        self.colors = colors
        self.markdown = Markdown(text)

        self.scrolled_md_text = ScrolledMDText(self, self.markdown, self.colors)
        self.scrolled_md_text.pack(fill=tk.BOTH, expand=True)

        self.bind("<Configure>", self.resize)

        self.geometry(f"1000x100")

    def resize(self, event):
        self.maxsize(2 ** 16, self.scrolled_md_text.max_height)
