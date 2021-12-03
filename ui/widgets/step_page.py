import tkinter as tk
from math import ceil

from ui import charge_color, tk_color, ticks_per_step
from ui.widgets.game_canvas import GameCanvas
from ui.widgets.menu_bar import MenuBar
from ui.widgets.result_selector import ResultSelector


class StepPage(tk.Frame):

    def __init__(self, display):
        super().__init__(display)
        self.display = display
        self.drawn = False

        self.menu_bar = None
        self.game_canvas = None
        self.result_selector = None
        self.mode_tkvar = None
        self.tk_frame = None
        self.time_slider = None
        self.playing_tkvar = None
        self.play_checkbox = None
        self.charge_mode_time_display = None

    def draw(self, colors, set_number, level_number):
        if self.drawn:
            self.redraw(colors, set_number, level_number)
        else:
            self.menu_bar = MenuBar(self, self.display, self.display.Page.CODING, colors,
                                    text=f"Level {set_number}-{level_number}")
            self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

            self.game_canvas = GameCanvas(self)
            self.game_canvas.grid(row=2, column=1, columnspan=2, sticky=tk.NSEW)

            self.result_selector = ResultSelector(self, colors)
            self.result_selector.grid(row=2, column=0, rowspan=4, sticky=tk.NSEW)

            modes = ("Global Time", "Charge Remaining")
            self.mode_tkvar = tk.StringVar(self, value=modes[0])
            self.mode_tkvar.trace('w', self.update_mode)
            self.tk_frame = tk.Frame(self)
            for column, mode in enumerate(modes):
                button = tk.Radiobutton(self.tk_frame, text=mode, variable=self.mode_tkvar, value=mode,
                                        indicatoron=False)
                button.grid(row=2, column=column, sticky=tk.NSEW)
                self.tk_frame.grid_columnconfigure(column, weight=1)
            self.tk_frame.grid_rowconfigure(0, weight=1)
            self.tk_frame.grid(row=3, column=1, columnspan=2, sticky=tk.NSEW)

            tick_interval = max(1, ceil((self.state.max_time - self.state.min_time) / 25))
            resolution = 1 / ticks_per_step
            self.time_slider = tk.Scale(self, from_=self.state.min_time, to=self.state.max_time,
                                        orient=tk.HORIZONTAL, command=self.time_change,
                                        tickinterval=tick_interval, resolution=resolution)
            self.time_slider.grid(row=4, column=2, sticky=tk.NSEW)

            self.playing_tkvar = tk.BooleanVar(self, False, "playing_tkvar")
            self.play_checkbox = tk.Checkbutton(self, variable=self.playing_tkvar, text="play")
            self.play_checkbox.grid(row=4, column=1, sticky=tk.NSEW)

            self.charge_mode_time_display = tk.Label(self, text="", bg="#FFF")
            self.charge_mode_time_display.grid(row=5, column=1, columnspan=2, sticky=tk.NSEW)

            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=0)
            self.grid_columnconfigure(2, weight=1)
            self.grid_rowconfigure(2, weight=1)
            self.grid_rowconfigure(3, weight=0)
            self.grid_rowconfigure(4, weight=0)
            self.grid_rowconfigure(5, weight=0)

            self.game_canvas.draw(True)
            self.tick()

            self.drawn = True

    def redraw(self, colors, set_number, level_number):
        self.menu_bar.destroy()
        self.menu_bar = MenuBar(self, self.display, self.display.Page.CODING, colors,
                                text=f"Level {set_number}-{level_number}")
        self.menu_bar.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        self.result_selector.destroy()
        self.result_selector = ResultSelector(self, colors)
        self.result_selector.grid(row=2, column=0, rowspan=4, sticky=tk.NSEW)

        self.update_mode()

        self.game_canvas.draw(True)

    @property
    def board(self):
        return self.display.board

    @property
    def results(self):
        return self.display.results

    @property
    def active_result_index(self):
        return self.result_selector.alternative_tkvar.get()

    @property
    def active_result(self):
        return self.results[self.active_result_index] if len(self.results) > self.active_result_index else None

    @property
    def time(self):
        return self.time_slider.get()

    @property
    def mode(self):
        return self.mode_tkvar.get()

    @property
    def state(self):
        return self.active_result[1]

    def update_mode(self, *_args, **_kwargs):
        if self.mode == "Global Time":
            tick_interval = max(1, ceil((self.state.max_time - self.state.min_time) / 25))
            self.time_slider.config(from_=self.state.min_time,
                                    to=self.state.max_time,
                                    tickinterval=tick_interval)
            self.time = self.state.min_time

        elif self.mode == "Charge Remaining":
            tick_interval = max(1, ceil((self.state.min_charge - self.state.max_charge) / 25))
            self.time_slider.config(from_=self.state.max_charge,
                                    to=self.state.min_charge,
                                    tickinterval=tick_interval)
            self.time = self.state.max_charge

        self.game_canvas.draw(True)

    @time.setter
    def time(self, value):
        self.time_slider.set(value)

    def tick(self, *_):
        if self.playing_tkvar.get():
            if ((self.time < self.state.max_time) if self.mode == "Global Time" else (
                    self.time > self.state.min_charge)):
                if self.mode == "Global Time":
                    self.time += 1 / ticks_per_step
                    self.time = min(self.time, self.state.max_time)
                else:
                    self.time -= 1 / ticks_per_step
                    self.time = max(self.time, self.state.min_charge)

            else:
                self.play_checkbox.deselect()

        if self.state.max_time - self.state.min_time > 100:
            self.after(ceil(75000 / (self.state.max_time - self.state.min_time) / ticks_per_step), self.tick)
        else:
            self.after(ceil(750 / ticks_per_step), self.tick)

    def time_change(self, *_):
        if self.mode == "Global Time":
            self.charge_mode_time_display.config(text="", bg="#FFF")
        else:
            time = self.state.get_robot_with_charge(round(self.time))[1]
            self.charge_mode_time_display.config(text="Time: %s" % time,
                                                 bg=tk_color(charge_color(self.time, self.state.max_charge)))
        self.game_canvas.draw(False)

    def alternative_result_change(self, *_):
        self.game_canvas.draw(True)
