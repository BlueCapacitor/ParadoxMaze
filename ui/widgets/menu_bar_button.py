import tkinter as tk

from ui import tk_color
from ui.utilities.font import Font


class MenuBarButton(tk.Canvas):
    def __init__(self, parent, size, colors, icon, action=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, width=size, height=size, bg=tk_color(colors[1]), highlightthickness=0,
                         relief=tk.RAISED, bd=2)

        icon_size = size * 3 / 4
        icon_tl = size * 1 / 8
        if isinstance(icon, list):
            for points in icon:
                self.create_polygon(*sum(((point[0] * icon_size + icon_tl,
                                           point[1] * icon_size + icon_tl) for point in points), ()),
                                    fill=tk_color(colors[2]))
        else:
            self.create_oval(icon_tl, icon_tl, icon_size + icon_tl, icon_size + icon_tl, width=0,
                             fill=tk_color(colors[2]))

            letter_shift = (0, 1)
            self.create_text((size / 2 + letter_shift[0], size / 2 + letter_shift[1]), text=icon, anchor=tk.CENTER,
                             font=Font.MED_LARGE.value, fill=tk_color(colors[1]))

        self.xview_moveto(0)
        self.yview_moveto(0)

        if action is not None:
            self.bind("<Button-1>", action)
