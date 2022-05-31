import tkinter as tk
from os import path

from main import root_path
from ui.utilities.markdown import Markdown
from ui.widgets.md_text import MDText


class IntroPage(tk.Frame):
    def __init__(self, display):
        super().__init__(display)
        with open(path.join(root_path, "levels", "other", "intro.md")) as intro_md_file:
            self.md_text = MDText(self, Markdown(intro_md_file.read()),
                                  colors=((0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0), (0.75, 0.75, 0.75)))
            self.md_text.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
