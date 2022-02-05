import tkinter as tk
from enum import Enum

from core.state_v2 import Result
from ui.widgets.coding_page import CodingPage
from ui.widgets.intro_page import IntroPage
from ui.widgets.level_select_page import LevelSelectPage
from ui.widgets.simple_text_page import SimpleTextPage
from ui.widgets.step_page import StepPage


class Display(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.results = []

        class Page(Enum):
            INTRO = IntroPage(self)
            LOADING = SimpleTextPage(self, "Loading...")
            CALCULATING = SimpleTextPage(self, "Calculating...")
            STEP = StepPage(self)
            LEVEL_SELECT = LevelSelectPage(self)
            CODING = CodingPage(self)

            def __init__(self, page):
                self.page = page
                self.page.grid(row=0, column=0, sticky=tk.NSEW)

        self.Page = Page

        self.current_page = self.Page.LOADING
        self.overall_result = None

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, results):
        self._results = []

        self.overall_result = Result.SUCCESS
        for result in results:
            if result[0] != Result.UNRECOVERABLE_PARADOX:
                self._results.append(result)
                self.overall_result |= result[0]

        if len(self._results) == 0:
            self.overall_result = Result.FAIL
            self._results = results

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, page):
        self._current_page = page
        self._current_page.page.tkraise()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.update()
