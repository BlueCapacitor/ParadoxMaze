import tkinter as tk
from math import ceil

from ui import charge_color, tk_color, ticks_per_step
from ui.utilities.font import Font
from ui.widgets.game_canvas import GameCanvas
from ui.widgets.menu_bar import MenuBar
from ui.widgets.overall_result_display import OverallResultDisplay
from ui.widgets.result_selector import ResultSelector


class StepPage(tk.Frame):

    def __init__(self, display):
        super().__init__(display)
        self.display = display
        self.drawn = False

        self.colors = None

        self.menu_bar = None
        self.game_canvas = None
        self.overall_result_display = None
        self.result_selector = None
        self.mode_tkvar = None
        self.tk_frame = None
        self.time_slider = None
        self.playing_tkvar = None
        self.play_checkbox = None
        self.charge_mode_time_display = None
        self.speed_slider = None
        self.buttons = []

    def draw(self, colors, set_number, level_number):
        if self.drawn:
            self.redraw(colors, set_number, level_number)
        else:
            self.colors = colors

            self.config(bg=tk_color(colors[3]))

            self.menu_bar = MenuBar(self, self.display, self.display.Page.CODING, colors,
                                    text=f"Level {set_number}-{level_number}")
            self.menu_bar.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW)

            self.game_canvas = GameCanvas(self)
            self.game_canvas.grid(row=2, column=1, columnspan=4, sticky=tk.NSEW)

            self.overall_result_display = OverallResultDisplay(self)
            self.overall_result_display.grid(row=1, column=0, columnspan=5, sticky=tk.NSEW)

            self.result_selector = ResultSelector(self, colors)
            self.result_selector.grid(row=2, column=0, rowspan=4, sticky=tk.NSEW)

            modes = ("Global Time", "Charge Remaining")
            self.mode_tkvar = tk.StringVar(self, value=modes[0])
            self.mode_tkvar.trace('w', self.update_mode)
            self.tk_frame = tk.Frame(self)

            self.buttons = []
            for column, mode in enumerate(modes):
                self.buttons.append(tk.Radiobutton(self.tk_frame, text=mode, variable=self.mode_tkvar, value=mode,
                                                   indicatoron=False, bg=tk_color(colors[0]),
                                                   selectcolor=tk_color(colors[0]),
                                                   font=Font.MED_SMALL.value, activebackground=tk_color(colors[1])))
                self.buttons[-1].grid(row=2, column=column, sticky=tk.NSEW)
                self.tk_frame.grid_columnconfigure(column, weight=1)
            self.tk_frame.grid_rowconfigure(0, weight=1)
            self.tk_frame.grid(row=3, column=1, columnspan=4, sticky=tk.NSEW)

            tick_interval = max(1, ceil((self.state.max_time - self.state.min_time) / 25))
            self.time_slider = tk.Scale(self, from_=self.state.min_time, to=self.state.max_time,
                                        orient=tk.HORIZONTAL, command=self.time_change,
                                        tickinterval=tick_interval, resolution=self.actual_steps_per_tick,
                                        bg=tk_color(colors[3]), activebackground=tk_color(colors[0]),
                                        troughcolor=tk_color(colors[2]), font=Font.MED_SMALL.value,
                                        highlightthickness=0)
            self.time_slider.grid(row=4, column=2, sticky=tk.NSEW)

            self.playing_tkvar = tk.BooleanVar(self, False, "playing_tkvar")
            self.play_checkbox = tk.Checkbutton(self, variable=self.playing_tkvar, text="play", bg=tk_color(colors[3]),
                                                font=Font.MED_SMALL.value)
            self.play_checkbox.grid(row=4, column=1, sticky=tk.NSEW)

            self.speed_slider = tk.Scale(self, from_=1, to=10, orient=tk.HORIZONTAL, tickinterval=9,
                                         command=self.speed_change, bg=tk_color(colors[3]),
                                         activebackground=tk_color(colors[0]), troughcolor=tk_color(colors[2]),
                                         font=Font.MED_SMALL.value, highlightthickness=0)
            self.speed_slider.set(3)
            self.speed_slider.grid(row=4, column=4)

            self.charge_mode_time_display = tk.Label(self, text="", bg=tk_color(colors[3]))
            self.charge_mode_time_display.grid(row=5, column=1, columnspan=4, sticky=tk.NSEW)

            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=0)
            self.grid_columnconfigure(2, weight=1)
            self.grid_columnconfigure(3, weight=0)
            self.grid_columnconfigure(4, weight=0)
            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=1)
            self.grid_rowconfigure(3, weight=0)
            self.grid_rowconfigure(4, weight=0)
            self.grid_rowconfigure(5, weight=0)

            self.game_canvas.draw(True, colors=colors)
            self.tick()

            self.drawn = True

    def redraw(self, colors, set_number, level_number):
        self.colors = colors

        self.config(bg=tk_color(colors[3]))

        self.menu_bar.destroy()
        self.menu_bar = MenuBar(self, self.display, self.display.Page.CODING, colors,
                                text=f"Level {set_number}-{level_number}")
        self.menu_bar.grid(row=0, column=0, columnspan=5, sticky=tk.NSEW)

        self.overall_result_display.destroy()
        self.overall_result_display = OverallResultDisplay(self)
        self.overall_result_display.grid(row=1, column=0, columnspan=5, sticky=tk.NSEW)

        self.result_selector.destroy()
        self.result_selector = ResultSelector(self, colors)
        self.result_selector.grid(row=2, column=0, rowspan=4, sticky=tk.NSEW)

        self.time_slider.config(bg=tk_color(colors[3]), activebackground=tk_color(colors[0]),
                                troughcolor=tk_color(colors[2]))

        self.speed_slider.config(bg=tk_color(colors[3]), activebackground=tk_color(colors[0]),
                                 troughcolor=tk_color(colors[2]))

        self.play_checkbox.config(bg=tk_color(colors[3]))

        for button in self.buttons:
            button.config(bg=tk_color(colors[0]), selectcolor=tk_color(colors[0]))

        self.update_mode()
        self.time_change()

        self.game_canvas.draw(True, colors=colors)

    @property
    def board(self):
        return self.display.board

    @property
    def results(self):
        return self.display.results

    @property
    def active_result_index(self):
        return self.result_selector.active_alternative

    @property
    def active_result(self):
        if len(self.results) <= self.active_result_index:
            self.result_selector.list_box.activate(0)
            return self.results[0]
        else:
            return self.results[self.active_result_index]

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

    @property
    def delay_time(self):
        return 32

    @property
    def actual_steps_per_tick(self):
        return 1 / round(ticks_per_step * 2 ** ((3 - self.speed_slider.get()) / 2) if self.speed_slider is not None
                         else ticks_per_step)

    def tick(self, *_):
        if self.playing_tkvar.get():
            if ((self.time < self.state.max_time) if self.mode == "Global Time" else (
                    self.time > self.state.min_charge)):
                if self.mode == "Global Time":
                    self.time += self.actual_steps_per_tick
                    self.time = min(self.time, self.state.max_time)
                else:
                    self.time -= self.actual_steps_per_tick
                    self.time = max(self.time, self.state.min_charge)

            else:
                self.play_checkbox.deselect()

        self.after(self.delay_time, self.tick)

    def time_change(self, *_):
        if self.mode == "Global Time":
            self.charge_mode_time_display.config(text="", bg=tk_color(self.colors[3]))
        else:
            time = self.state.get_robot_with_charge(round(self.time))[1]
            self.charge_mode_time_display.config(text="Time: %s" % time,
                                                 bg=tk_color(charge_color(self.time, self.state.max_charge)))
        self.game_canvas.draw(False)

    def speed_change(self, *_):
        self.time_slider.config(resolution=self.actual_steps_per_tick, from_=self.state.min_time,
                                to=self.state.max_time)

    def alternative_result_change(self, *_):
        self.update_mode()
        self.game_canvas.draw(True)
