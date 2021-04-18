from enum import Enum
import tkinter.font as tk_font


class Font(Enum):
    HUGE = ("Veranda", 64)
    LARGE = ("Veranda", 32)
    NORMAL = ("Veranda", 16)
    SMALL = ("Veranda", 8)

    def measure(self, window, text):
        return tk_font.Font(root=window, font=self.value).measure(text)
