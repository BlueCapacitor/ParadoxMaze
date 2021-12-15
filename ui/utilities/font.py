from enum import Enum
import tkinter.font as tk_font

family = "Menlo"


class Font(Enum):
    HUGE = (family, 64)
    LARGER = (family, 48)
    LARGE = (family, 32)
    NORMAL = (family, 16)
    MED_SMALL = (family, 12)
    SMALL = (family, 8)

    @staticmethod
    def metrics(font, window, *args, **kwargs):
        return tk_font.Font(root=window, font=font.value if isinstance(font, Font) else font).metrics(*args, **kwargs)

    @staticmethod
    def measure(font, window, text):
        return tk_font.Font(root=window, font=font.value if isinstance(font, Font) else font).measure(text)

    @staticmethod
    def create_font(size, weight="normal", slant="roman"):
        base_font = (Font.NORMAL, Font.LARGE, Font.LARGER, Font.HUGE)[size]
        return base_font.value + (weight, slant)
