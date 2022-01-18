import tkinter as tk


class AutomaticHideScrollbar(tk.Scrollbar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = "grid"

    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.hide()
        else:
            self.show()
        super().set(low, high)

    def grid(self, *args, **kwargs):
        self.mode = "grid"
        super().grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.mode = "pack"
        super().pack(*args, **kwargs)

    def place(self, *args, **kwargs):
        self.mode = "place"
        super().place(*args, **kwargs)

    def hide(self):
        match self.mode:
            case "grid":
                self.grid_remove()
            case "pack":
                self.pack_forget()
            case "place":
                self.place_forget()

    def show(self):
        match self.mode:
            case "grid":
                self.grid()
            case "pack":
                self.pack()
            case "place":
                self.place()
