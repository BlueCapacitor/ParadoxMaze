import tkinter as tk


class ScrollBoundCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind_scroll()

    def bind_scroll(self):
        self.bind("<ButtonPress-1>", self.scroll_start)
        self.bind("<B1-Motion>", self.scroll_move)

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)
