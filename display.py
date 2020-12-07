'''
Created on Oct 14, 2020

@author: gosha
'''

from enum import Enum
from math import ceil

from state import Result
import tkinter as tk


class Display(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.results = []

        class Page(Enum):
            LOADING = Display.SimpleTextPage(self, "Loading...")
            CALCULATING = Display.SimpleTextPage(self, "Calculating...")
            NO_POSIBILITIES = Display.SimpleTextPage(self, "Fail: All possibilities lead to paradox")
            STEP = Display.StepPage(self)
            LEVEL_SELECT = Display.LevelSelectPage(self)

            def __init__(self, page):
                self.page = page
                self.page.grid(row = 0, column = 0, sticky = tk.NSEW)

        self.Page = Page

        self.currentPage = self.Page.LOADING

    @property
    def results(self):
        return(self._results)

    @results.setter
    def results(self, results):
        self._results = []

        self.overallResult = Result.SUCCESS
        for result in results:
            if(result[0] != Result.UNRECOVERABLE_PARADOX):
                self._results.append(result)
                self.overallResult |= result[0]

        if(len(self._results) == 0):
            self._results = results

    @property
    def currentPage(self):
        return(self._currentPage)

    @currentPage.setter
    def currentPage(self, page):
        self._currentPage = page
        self._currentPage.page.tkraise()
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        self.update()

    @staticmethod
    def tkColor(color):
        return("#{:02X}{:02X}{:02X}".format(*map(lambda v: ceil(v * 255), color)))

    @staticmethod
    def chargeColor(charge, initialCharge):
        partsCharged = charge / initialCharge
        if(partsCharged > 0.5):
            return((2 - partsCharged * 2, 1, 0))
        else:
            return((1, partsCharged * 2, 0))

    @staticmethod
    def borderChargeColor(charge, initialCharge):
        return(tuple(map(lambda x: x / 2, Display.chargeColor(charge, initialCharge))))

    @staticmethod
    def inactiveChargeColor(*_):
        return((0.5, 0.5, 0.5))

    @staticmethod
    def inactiveBorderChargeColor(*_):
        return((0.75, 0.75, 0.75))

    class Font(Enum):
        HUGE = ("Veranda", 64)
        LARGE = ("Veranda", 32)
        NORMAL = ("Veranda", 16)
        SMALL = ("Veranda", 8)

    class SimpleTextPage(tk.Frame):

        def __init__(self, display, text):
            super().__init__(display)
            self.label = tk.Label(self, text = text, font = Display.Font.HUGE.value)
            self.label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = tk.NSEW)
            self.grid_columnconfigure(0, weight = 1)
            self.grid_rowconfigure(0, weight = 1)

    class StepPage(tk.Frame):

        def __init__(self, display):
            super().__init__(display)
            self.display = display

        def draw(self):
            self.gameCanvas = Display.GameCanvas(self)
            self.gameCanvas.grid(row = 0, column = 1, columnspan = 2, sticky = tk.NSEW)

            self.resultSelector = Display.ResultSelector(self)
            self.resultSelector.grid(row = 0, column = 0, rowspan = 4, sticky = tk.NSEW)

            modes = ("Global Time", "Charge Remaining")
            self.modeTKVar = tk.StringVar(self, value = modes[0])
            self.modeTKVar.trace('w', self.updateMode)
            self.tkFrame = tk.Frame(self)
            for column, mode in enumerate(modes):
                button = tk.Radiobutton(self.tkFrame, text = mode, variable = self.modeTKVar, value = mode, indicatoron = False)
                button.grid(row = 0, column = column, sticky = tk.NSEW)
                self.tkFrame.grid_columnconfigure(column, weight = 1)
            self.tkFrame.grid_rowconfigure(0, weight = 1)
            self.tkFrame.grid(row = 1, column = 1, columnspan = 2, sticky = tk.NSEW)

            tickInterval = max(1, ceil((self.state.maxTime - self.state.minTime) / 25))
            self.timeSlider = tk.Scale(self, from_ = self.state.minTime, to = self.state.maxTime, orient = tk.HORIZONTAL, command = self.timeChange, tickinterval = tickInterval)
            self.timeSlider.grid(row = 2, column = 2, sticky = tk.NSEW)

            self.playingTKVar = tk.BooleanVar(self, True, "playingTKVar")
            self.playCheckbox = tk.Checkbutton(self, variable = self.playingTKVar, text = "play")
            self.playCheckbox.grid(row = 2, column = 1, sticky = tk.NSEW)

            self.chargeModeTimeDisplay = tk.Label(self, text = "", bg = "#FFF")
            self.chargeModeTimeDisplay.grid(row = 3, column = 1, columnspan = 2, sticky = tk.NSEW)

            self.grid_columnconfigure(0, weight = 0)
            self.grid_columnconfigure(1, weight = 0)
            self.grid_columnconfigure(2, weight = 1)
            self.grid_rowconfigure(0, weight = 1)
            self.grid_rowconfigure(1, weight = 0)
            self.grid_rowconfigure(2, weight = 0)
            self.grid_rowconfigure(3, weight = 0)

            self.gameCanvas.draw()
            self.after(3000, self.tick)

        @property
        def board(self):
            return(self.display.board)

        @property
        def results(self):
            return(self.display.results)

        @property
        def activeResultIndex(self):
            return(self.resultSelector.alternativeTKVar.get())

        @property
        def activeResult(self):
            return(self.results[self.activeResultIndex] if len(self.results) > self.activeResultIndex else None)

        @property
        def time(self):
            return(self.timeSlider.get())

        @property
        def mode(self):
            return(self.modeTKVar.get())

        @property
        def state(self):
            return(self.activeResult[1])

        def updateMode(self, *_args, **_kwargs):
            if(self.mode == "Global Time"):
                tickInterval = max(1, ceil((self.state.maxTime - self.state.minTime) / 25))
                self.timeSlider.config(from_ = self.state.minTime, to = self.state.maxTime, tickinterval = tickInterval)
                self.time = self.state.minTime

            elif(self.mode == "Charge Remaining"):
                tickInterval = max(1, ceil((self.state.minCharge - self.state.maxCharge) / 25))
                self.timeSlider.config(from_ = self.state.maxCharge, to = self.state.minCharge, tickinterval = tickInterval)
                self.time = self.state.maxCharge

        @time.setter
        def time(self, value):
            self.timeSlider.set(value)

        def tick(self, *_):
            if(self.playingTKVar.get()):
                if((self.time < self.state.maxTime) if self.mode == "Global Time" else (self.time > self.state.minCharge)):
                    self.time += 1 if self.mode == "Global Time" else -1
                else:
                    self.playCheckbox.deselect()

            if(self.state.maxTime - self.state.minTime > 100):
                self.after(ceil(75000 / (self.state.maxTime - self.state.minTime)), self.tick)
            else:
                self.after(750, self.tick)

        def timeChange(self, *_):
            if(self.mode == "Global Time"):
                self.chargeModeTimeDisplay.config(text = None, bg = "#FFF")
            else:
                time = self.state.getRobotWithCharge(self.time)[1]
                self.chargeModeTimeDisplay.config(text = "Time: %s" % (time), bg = Display.tkColor(Display.chargeColor(self.time, self.state.maxCharge)))
            self.gameCanvas.draw()

        def alternativeResultChange(self, *_):
            self.gameCanvas.draw()

    class ResultSelector(tk.Frame):

        def __init__(self, parent):
            super().__init__(parent, bg = "#888")
            self.parent = parent
            self.alternativeTKVar = tk.IntVar()
            self.alternativeTKVar.trace('w', self.parent.alternativeResultChange)

            self.buttonContainer = tk.Frame(self, bg = "#888")
            self.buttonContainer.grid(row = 0, column = 0, sticky = tk.NSEW)
            self.grid_rowconfigure(0, weight = 1)
            self.grid_columnconfigure(0, weight = 1)

            for alternativeNumber, result in enumerate(parent.results):
                resultStatusText = {Result.SUCCESS: "Success", Result.UNRECOVERABLE_PARADOX: "Paradox", Result.FAIL: "Fail"}[result[0]]
                buttonColor = {Result.SUCCESS: (0, 1, 0), Result.UNRECOVERABLE_PARADOX: (0, 0, 1), Result.FAIL: (1, 0, 0)}[result[0]]
                button = tk.Radiobutton(self.buttonContainer, text = "Alternative %s - %s" % (alternativeNumber, resultStatusText), variable = self.alternativeTKVar, value = alternativeNumber, indicatoron = False, bg = Display.tkColor(buttonColor))
                button.grid(row = alternativeNumber, column = 0, sticky = tk.E + tk.N + tk.W)

    class GameCanvas(tk.Frame):

        def __init__(self, parent, tileSize = 45, tileCenterSize = 30, tileFlareHorizontalVerticalSize = 20, tileFlareDiagonalSize = 10):
            super().__init__(parent)

            self.parent = parent
            self.tileSize = tileSize
            self.tileCenterSize = tileCenterSize
            self.tileFlareHorizontalVerticalSize = tileFlareHorizontalVerticalSize
            self.tileFlareDiagonalSize = tileFlareDiagonalSize

            self.infoBox = Display.InfoBox(self)
            self.infoBox.grid(row = 0, column = 0, sticky = tk.NSEW)

            self.canvas = tk.Canvas(self, width = (self.board.width + 1) * self.tileSize, height = (self.board.height + 1) * self.tileSize)
            self.canvas.grid(row = 1, column = 0, sticky = tk.NSEW)

            self.grid_columnconfigure(0, weight = 1)
            self.grid_rowconfigure(0, weight = 0)
            self.grid_rowconfigure(1, weight = 1)

        @property
        def display(self):
            return(self.parent.display)

        @property
        def board(self):
            return(self.display.board)

        @property
        def result(self):
            return(self.parent.activeResult[0])

        @property
        def state(self):
            return(self.parent.state)

        @property
        def mode(self):
            return(self.parent.mode)

        @property
        def time(self):
            return(self.parent.time)

        def screenCoords(self, x, y):
            outX = (x + 1) * self.tileSize
            outY = (y + 1) * self.tileSize
            return((outX, outY))

        def draw(self):
            self.canvas.delete(tk.ALL)
            self.drawBoard()
            self.drawRobots()

        def drawBoard(self):
            time = self.time if self.mode == "Global Time" else self.state.getRobotWithCharge(self.time)[1]
            for tile in self.board.listTiles:
                self.drawTile(tile, time)

        def drawRobots(self):
            if(self.mode == "Global Time"):
                for robot in self.state.getRobotsAtTime(self.time):
                    self.drawRobot(robot)
            if(self.mode == "Charge Remaining"):
                currentRobot, time = self.state.getRobotWithCharge(self.time)
                for robot in self.state.getRobotsAtTime(time):
                    if(robot != currentRobot):
                        self.drawRobot(robot, colorFunction = Display.inactiveChargeColor, borderColorFunction = Display.inactiveBorderChargeColor)
                self.drawRobot(currentRobot)

        def drawTile(self, tile, time):
            colors = tile.getColors(self.state, time)
            self.drawSquare(*self.screenCoords(tile.x, tile.y), self.tileSize, colors[0], border = 1)
            self.drawSquare(*self.screenCoords(tile.x, tile.y), self.tileCenterSize, colors[1])
            if(len(colors) >= 3):
                self.drawFlare(*self.screenCoords(tile.x, tile.y), self.tileFlareDiagonalSize, self.tileFlareHorizontalVerticalSize, colors[2])
            text = tile.getText(self.state, time)
            self.canvas.create_text(*self.screenCoords(tile.x, tile.y), text = text[0], fill = Display.tkColor(text[1]), width = self.tileCenterSize)

        def drawSquare(self, x, y, l, color, border = 0):
            self.canvas.create_rectangle(x + l / 2, y - l / 2, x - l / 2, y + l / 2, fill = Display.tkColor(color), width = border, outline = "#000")

        def drawFlare(self, x, y, d, hv, color):
            self.canvas.create_polygon(x + hv / 2, y, x + d / 2, y + d / 2, x, y + hv / 2, x - d / 2, y + d / 2, x - hv / 2, y, x - d / 2, y - d / 2, x, y - hv / 2, x + d / 2, y - d / 2, fill = Display.tkColor(color), width = 0)

        def drawRobot(self, robot, colorFunction = None, border = 2, borderColorFunction = None, scale = 0.75):
            if(colorFunction is None):
                colorFunction = Display.chargeColor
            if(borderColorFunction is None):
                borderColorFunction = Display.borderChargeColor
            color = colorFunction(robot.chargeRemaining, robot.initialCharge)
            borderColor = borderColorFunction(robot.chargeRemaining, robot.initialCharge)

            x, y = self.screenCoords(robot.x, robot.y)
            dx, dy = robot.direction.dx, robot.direction.dy
            halfLength = self.tileSize / 2 * scale

            x0, y0 = x + halfLength * (-1 * dx - 0.5 * dy), y + halfLength * (0.5 * dx - 1 * dy)
            x1, y1 = x - halfLength * dx * 0.5, y - halfLength * dy * 0.5
            x2, y2 = x + halfLength * (-1 * dx + 0.5 * dy), y + halfLength * (-0.5 * dx - 1 * dy)
            x3, y3 = x + halfLength * dx, y + halfLength * dy

            self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = Display.tkColor(color), width = border, outline = Display.tkColor(borderColor))
            self.canvas.create_text(*self.screenCoords(robot.x, robot.y), text = str(robot.chargeRemaining), fill = "#000", width = self.tileCenterSize, font = Display.Font.SMALL.value)

    class LevelSelectPage(tk.Frame):

        def __init__(self, display, buttonsPerRow = 3):
            super().__init__(display)

            self.set = 0
            self.buttonsPerRow = buttonsPerRow

            self.levelButtons = []

            for column in range(buttonsPerRow):
                self.grid_columnconfigure(column + 1, weight = 1)

        def addButton(self, number, csvMap, code):
            button = tk.Button(self, text = "%s-%s" % (self.set, number))
            button.grid(row = number // self.buttonsPerRow, column = number % self.buttonsPerRow + 1)
            self.levelButtons.append(button)
