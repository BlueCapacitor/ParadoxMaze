import tkinter as tk

from ui import tk_color
from ui.utilities.font import Font
from ui.widgets.menu_bar_button import MenuBarButton


class MenuBar(tk.Frame):
    back_icon = [[(0, 1 / 2),
                  (1 / 2, 0),
                  (1 / 2, 1 / 4),
                  (1, 1 / 4),
                  (1, 3 / 4),
                  (1 / 2, 3 / 4),
                  (1 / 2, 1)]]

    run_icon = [[(0, 0),
                 (1, 1 / 2),
                 (0, 1)]]

    hint_icon = "?"

    solution_icon = [[(1 / 7, y / 7),
                      (6 / 7, y / 7),
                      (6 / 7, (y + 1) / 7),
                      (1 / 7, (y + 1) / 7)] for y in (1, 3, 5)]

    def __init__(self, parent, display, back_page, colors, height=32, buttons=None, text=""):
        super().__init__(parent, bg=tk_color(colors[1]))

        self.parent = parent
        self.display = display
        self.back_page = back_page
        self.height = height
        self.colors = colors

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.left_button_container = tk.Frame(self, bg=tk_color(self.colors[1]))
        self.left_button_container.place(anchor=tk.W, relx=0, rely=0.5)

        self.right_button_container = tk.Frame(self, bg=tk_color(self.colors[1]))
        self.right_button_container.place(anchor=tk.E, relx=1, rely=0.5)

        self.label = tk.Label(self, text=text, font=Font.LARGE.value,
                              bg=tk_color(self.colors[1]), fg=tk_color(self.colors[0]))
        self.label.grid(row=0, column=0)

        self.add_button(False, self.go_back, MenuBar.back_icon)

        if buttons is not None:
            for side in (False, True):
                for action, icon in buttons[side]:
                    self.add_button(side, action, icon)

    def add_button(self, side, action, icon):
        button = MenuBarButton(self.right_button_container if side else self.left_button_container, self.height,
                               self.colors, icon, action=action)
        button.pack(side=tk.RIGHT if side else tk.LEFT, padx=(2.5 * (not side), 2.5 * side), pady=2.5)

    def go_back(self, *_):
        self.display.current_page = self.back_page
