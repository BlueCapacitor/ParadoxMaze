'''
Created on Oct 14, 2020

@author: gosha
'''

from enum import Enum
from math import ceil
import os

from controller import Controller
from csv_map import CSVMap
from instruction_set import InstructionSet
from state import Result, State
import tkinter as tk
import tkinter.font as tk_font
import tkinter.ttk as ttk


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
            CODING = Display.CodingPage(self)

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

    @staticmethod
    def drawRoundedRectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return(canvas.create_polygon(points, **kwargs, smooth = True))

    class Font(Enum):
        HUGE = ("Veranda", 64)
        LARGE = ("Veranda", 32)
        NORMAL = ("Veranda", 16)
        SMALL = ("Veranda", 8)

        def measure(self, window, text):
            return(tk_font.Font(root = window, font = self.value).measure(text))

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
            self.drawn = False

        def draw(self, colors):
            if(self.drawn):
                self.redraw(colors)
            else:
                self.menuBar = Display.MenuBar(self, self.display, self.display.Page.CODING, colors)
                self.menuBar.grid(row = 0, column = 0, columnspan = 3, sticky = tk.NSEW)

                self.gameCanvas = Display.GameCanvas(self)
                self.gameCanvas.grid(row = 2, column = 1, columnspan = 2, sticky = tk.NSEW)

                self.resultSelector = Display.ResultSelector(self, colors)
                self.resultSelector.grid(row = 2, column = 0, rowspan = 4, sticky = tk.NSEW)

                modes = ("Global Time", "Charge Remaining")
                self.modeTKVar = tk.StringVar(self, value = modes[0])
                self.modeTKVar.trace('w', self.updateMode)
                self.tkFrame = tk.Frame(self)
                for column, mode in enumerate(modes):
                    button = tk.Radiobutton(self.tkFrame, text = mode, variable = self.modeTKVar, value = mode, indicatoron = False)
                    button.grid(row = 2, column = column, sticky = tk.NSEW)
                    self.tkFrame.grid_columnconfigure(column, weight = 1)
                self.tkFrame.grid_rowconfigure(0, weight = 1)
                self.tkFrame.grid(row = 3, column = 1, columnspan = 2, sticky = tk.NSEW)

                tickInterval = max(1, ceil((self.state.maxTime - self.state.minTime) / 25))
                self.timeSlider = tk.Scale(self, from_ = self.state.minTime, to = self.state.maxTime, orient = tk.HORIZONTAL, command = self.timeChange, tickinterval = tickInterval)
                self.timeSlider.grid(row = 4, column = 2, sticky = tk.NSEW)

                self.playingTKVar = tk.BooleanVar(self, False, "playingTKVar")
                self.playCheckbox = tk.Checkbutton(self, variable = self.playingTKVar, text = "play")
                self.playCheckbox.grid(row = 4, column = 1, sticky = tk.NSEW)

                self.chargeModeTimeDisplay = tk.Label(self, text = "", bg = "#FFF")
                self.chargeModeTimeDisplay.grid(row = 5, column = 1, columnspan = 2, sticky = tk.NSEW)

                self.grid_columnconfigure(0, weight = 0)
                self.grid_columnconfigure(1, weight = 0)
                self.grid_columnconfigure(2, weight = 1)
                self.grid_rowconfigure(2, weight = 1)
                self.grid_rowconfigure(3, weight = 0)
                self.grid_rowconfigure(4, weight = 0)
                self.grid_rowconfigure(5, weight = 0)

                self.gameCanvas.draw()
                self.tick()

                self.drawn = True

        def redraw(self, colors):
            self.menuBar.destroy()
            self.menuBar = Display.MenuBar(self, self.display, self.display.Page.CODING, colors)
            self.menuBar.grid(row = 0, column = 0, columnspan = 3, sticky = tk.NSEW)

            self.resultSelector.destroy()
            self.resultSelector = Display.ResultSelector(self, colors)
            self.resultSelector.grid(row = 2, column = 0, rowspan = 4, sticky = tk.NSEW)

            self.updateMode()

            self.gameCanvas.draw()

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
                self.chargeModeTimeDisplay.config(text = "", bg = "#FFF")
            else:
                time = self.state.getRobotWithCharge(self.time)[1]
                self.chargeModeTimeDisplay.config(text = "Time: %s" % (time), bg = Display.tkColor(Display.chargeColor(self.time, self.state.maxCharge)))
            self.gameCanvas.draw()

        def alternativeResultChange(self, *_):
            self.gameCanvas.draw()

    class ResultSelector(tk.Frame):

        def __init__(self, parent, colors):
            super().__init__(parent, bg = Display.tkColor(colors[1]))
            self.parent = parent
            self.alternativeTKVar = tk.IntVar()
            self.alternativeTKVar.trace('w', self.parent.alternativeResultChange)

            self.buttonContainer = tk.Frame(self, bg = Display.tkColor(colors[1]))
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

            self.grid_rowconfigure(0, weight = 1)
            self.grid_columnconfigure(0, weight = 1)

            self.canvas = tk.Canvas(self, width = (self.board.width + 1) * self.tileSize, height = (self.board.height + 1) * self.tileSize, scrollregion = (0, 0, (self.board.width + 1) * self.tileSize, (self.board.height + 1) * self.tileSize))
            self.canvas.grid(row = 0, column = 0, sticky = tk.NSEW)

            self.scrollV = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.canvas.yview)
            self.scrollV.grid(row = 0, column = 1, sticky = tk.NSEW)

            self.scrollH = tk.Scrollbar(self, orient = tk.HORIZONTAL, command = self.canvas.xview)
            self.scrollH.grid(row = 1, column = 0, sticky = tk.NSEW)

            self.canvas.config(xscrollcommand = self.scrollH.set, yscrollcommand = self.scrollV.set)

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

        def setColors(self, colors):
            self.canvas.config(bg = Display.tkColor(colors[0]), highlightcolor = Display.tkColor(colors[1]))

        def screenCoords(self, x, y):
            outX = (x + 1) * self.tileSize
            outY = (y + 1) * self.tileSize
            return((outX, outY))

        def draw(self):
            self.canvas.delete(tk.ALL)
            self.canvas.config(scrollregion = (0, 0, (self.board.width + 1) * self.tileSize, (self.board.height + 1) * self.tileSize))

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

    class PreviewCanvas(GameCanvas):

        def __init__(self, parent, board, robotStart, tileSize = 45, tileCenterSize = 30, tileFlareHorizontalVerticalSize = 20, tileFlareDiagonalSize = 10):
            self._board = board
            self.robotStart = robotStart

            self._state = State(board)
            self.state.robotLog = {0: [robotStart]}
            self._time = 0

            super().__init__(parent, tileSize = tileSize, tileCenterSize = tileCenterSize, tileFlareHorizontalVerticalSize = tileFlareHorizontalVerticalSize, tileFlareDiagonalSize = tileFlareDiagonalSize)

        @property
        def board(self):
            return(self._board)

        @property
        def state(self):
            return(self._state)

        @property
        def time(self):
            return(self._time)

        def drawRobots(self):
            self.drawRobot(self.robotStart)

        def drawBoard(self):
            for tile in self.board.listTiles:
                self.drawTile(tile, self.time)

        def destroy(self):
            self.canvas.delete(tk.ALL)
            super().destroy()

    class LevelSelectPage(tk.Frame):

        def __init__(self, display, buttonsPerRow = 5):
            super().__init__(display, padx = 4, pady = 4)
            self.display = display

            self.set = 1
            self.buttonsPerRow = buttonsPerRow

            self.levelButtons = []
            self.setLabel = tk.Label(self, font = Display.Font.LARGE.value)
            self.setLabel.grid(row = 0, column = 1, columnspan = self.buttonsPerRow - 2, sticky = tk.NSEW, padx = 8, pady = 8)

            self.leftButton = tk.Label(self, font = Display.Font.LARGE.value, text = "-")
            self.leftButton.grid(row = 0, column = 0, sticky = tk.NSEW, padx = 8, pady = 8)
            self.leftButton.bind("<Button-1>", self.left)

            self.rightButton = tk.Label(self, font = Display.Font.LARGE.value, text = "+")
            self.rightButton.grid(row = 0, column = self.buttonsPerRow - 1, sticky = tk.NSEW, padx = 8, pady = 8)
            self.rightButton.bind("<Button-1>", self.right)

            for column in range(self.buttonsPerRow):
                self.grid_columnconfigure(column, weight = 1)

            self.redraw()

        levelsPath = "levels"

        @property
        def setPath(self):
            return("%s/set-%02d" % (self.levelsPath, self.set))

        @property
        def resourcePath(self):
            return("%s/resources" % (self.setPath))

        @property
        def validSet(self):
            return(os.path.isdir(self.setPath))

        @property
        def isFirstSet(self):
            return(self.set == 1)

        @property
        def isLastSet(self):
            self.set += 1
            out = not(self.validSet)
            self.set -= 1
            return(out)

        def left(self, *_):
            if(not(self.isFirstSet)):
                self.set -= 1
                self.redraw()

        def right(self, *_):
            if(not(self.isLastSet)):
                self.set += 1
                self.redraw()

        def getColors(self):
            colorFile = open("%s/set-colors.txt" % self.resourcePath, 'r')
            colors = tuple(map(lambda s: tuple(map(float, s.split(", "))), colorFile.read().split('\n')))
            return(colors)

        def redraw(self):
            self.colors = self.getColors()

            self.config(bg = Display.tkColor(self.colors[0]))
            self.setLabel.config(bg = Display.tkColor(self.colors[0]), fg = Display.tkColor(self.colors[1]))

            self.setLabel.config(text = "Set %s" % (self.set))

            self.leftButton.config(bg = Display.tkColor(self.colors[3]) if self.isFirstSet else Display.tkColor(self.colors[1]), fg = Display.tkColor(self.colors[2]))
            self.rightButton.config(bg = Display.tkColor(self.colors[3]) if self.isLastSet else Display.tkColor(self.colors[1]), fg = Display.tkColor(self.colors[2]))

            for button in self.levelButtons:
                button.destroy()

            self.levelButtons = []

            self.readStateFromFileSystem()

        def readStateFromFileSystem(self):
            levelFolders = os.listdir(self.setPath)
            levelFolders.sort()
            for levelFolder in levelFolders:
                if(levelFolder.split('-')[0] != "level"):
                    continue

                number = int(levelFolder.split('-')[-1])
                csvMapFile = open("%s/%s/%s-%s-map.csv" % (self.setPath, levelFolder, self.set, number), 'r')
                codeFilePath = "%s/%s/code.txt" % (self.setPath, levelFolder)
                csvMapText = csvMapFile.read()
                csvMapFile.close()

                self.addButton(number, csvMapText, codeFilePath)

        def addButton(self, number, csvMapText, codeFilePath):
            button = tk.Label(self, text = "%s-%s" % (self.set, number), font = Display.Font.LARGE.value, bg = Display.tkColor(self.colors[1]), fg = Display.tkColor(self.colors[2]))
            button.bind("<Button-1>", lambda *_: self.loadLevel(number, csvMapText, codeFilePath))
            button.grid(row = (number - 1) // self.buttonsPerRow + 1, column = (number - 1) % self.buttonsPerRow, sticky = tk.NSEW, padx = 8, pady = 8)
            self.grid_rowconfigure((number - 1) // self.buttonsPerRow + 1, weight = 1)
            self.levelButtons.append(button)

        def loadLevel(self, number, csvMapText, codeFilePath):
            self.display.currentPage = self.display.Page.CODING
            self.display.Page.CODING.value.csvMap = CSVMap(csvMapText)
            self.display.Page.CODING.value.codeFilePath = codeFilePath
            self.display.Page.CODING.value.draw(self.colors)

    class CodingPage(tk.Frame):

        def __init__(self, display):
            super().__init__(display)
            self.display = display

            self.codeBox = Display.CodeBox(self)
            self.codeBox.grid(row = 1, column = 2, sticky = tk.NSEW)

            self.separator = ttk.Separator(self, orient = tk.VERTICAL)
            self.separator.grid(row = 1, column = 1)

            self.grid_rowconfigure(1, weight = 1)
            self.grid_columnconfigure(0, weight = 1)
            self.grid_columnconfigure(2, weight = 1)

            self.previewCanvas = None
            self.menuBar = None

        def draw(self, colors):
            self.colors = colors

            self.bg = Display.tkColor(self.colors[0])

            if(self.menuBar is not None):
                self.menuBar.destroy()

            self.menuBar = Display.MenuBar(self, self.display, self.display.Page.LEVEL_SELECT, self.colors, runAction = self.run)
            self.menuBar.grid(row = 0, column = 0, columnspan = 3, sticky = tk.NSEW)

            self.board = self.csvMap.buildBoard()

            if(self.previewCanvas is not None):
                self.previewCanvas.destroy()

            self.previewCanvas = Display.PreviewCanvas(self, self.board, self.csvMap.buildRobot())
            self.previewCanvas.grid(row = 1, column = 0, sticky = tk.NSEW)

            self.previewCanvas.draw()
            self.codeBox.loadFile()

        def run(self, *_):
            instructions = InstructionSet(self.codeBox.text)

            robot = self.csvMap.buildRobot()
            controller = Controller(self.board, robot, instructions)

            self.display.currentPage = self.display.Page.CALCULATING

            results = controller.run()

            self.display.board = self.board
            self.display.results = results
            self.display.currentPage = self.display.Page.STEP
            self.display.currentPage.page.draw(self.colors)

    class CodeBox(tk.Frame):

        def __init__(self, codingPage):
            super().__init__(codingPage)
            self.codingPage = codingPage

            self.doNotOverwriteFile = False

            self.textBox = Display.TextWithModifiedCallback(self, wrap = tk.NONE, font = Display.Font.NORMAL, tabs = (Display.Font.NORMAL.measure(self, ' ' * 2),))
            self.textBox.grid(row = 0, column = 0, sticky = tk.NSEW)
            self.scrollV = tk.Scrollbar(self, orient = tk.VERTICAL, command = self.textBox.yview)
            self.scrollV.grid(row = 0, column = 1, sticky = tk.NSEW)
            self.scrollH = tk.Scrollbar(self, orient = tk.HORIZONTAL, command = self.textBox.xview)
            self.scrollH.grid(row = 1, column = 0, sticky = tk.NSEW)
            self.textBox.config(yscrollcommand = self.scrollV.set, xscrollcommand = self.scrollH.set)

            self.grid_rowconfigure(0, weight = 1)
            self.grid_columnconfigure(0, weight = 1)

            self.textBox.bind("<Return>", self.enter)
            self.textBox.bind('}', self.closeBrace)

            self.textBox.bind("<<TextModified>>", self.save)

        def currentIndentation(self):
            text = self.textBox.get("0.0", tk.INSERT)
            indentation = 0
            for line in text.split('\n'):
                indentation += line.split("//")[0].count('{') - line.split("//")[0].count('}')
            return(indentation)

        def characterBeforeCursor(self):
            return(self.textBox.get("insert - 1 char", tk.INSERT))

        def enter(self, *_):
            self.textBox.insert(tk.INSERT, '\n' + '\t' * self.currentIndentation())
            return("break")

        def closeBrace(self, *_):
            if(self.characterBeforeCursor() == '\t'):
                self.textBox.delete("insert - 1 char", tk.INSERT)

        def loadFile(self):
            self.doNotOverwriteFile = True
            filePath = self.codingPage.codeFilePath
            file = open(filePath, 'r')
            self.textBox.delete("0.0", tk.END)
            self.textBox.insert(tk.END, file.read())
            file.close()
            self.doNotOverwriteFile = False

        def save(self, *_):
            if(not(self.doNotOverwriteFile)):
                filePath = self.codingPage.codeFilePath
                file = open(filePath, 'w')
                file.flush()
                file.write(self.text)
                file.close()

        @property
        def text(self):
            text = self.textBox.get("0.0", "end")
            if(len(text) > 0 and text[-1] == '\n'):
                text = text[:-1]
            return(text)

    class TextWithModifiedCallback(tk.Text):

        def __init__(self, *args, **kwargs):
            tk.Text.__init__(self, *args, **kwargs)

            self._orig = self._w + "_orig"
            self.tk.call("rename", self._w, self._orig)
            self.tk.createcommand(self._w, self._proxy)

        def _proxy(self, command, *args):
            cmd = (self._orig, command) + args

            try:
                result = self.tk.call(cmd)
            except Exception:
                return

            if command in ("insert", "delete", "replace"):
                self.event_generate("<<TextModified>>")

            return(result)

    class MenuBar(tk.Frame):

        def __init__(self, parent, display, backPage, colors, height = 32, runAction = None):
            super().__init__(parent, bg = Display.tkColor(colors[1]))

            self.parent = parent
            self.display = display
            self.backPage = backPage
            self.height = height

            self.grid_rowconfigure(0, weight = 0)
            self.grid_columnconfigure(0, weight = 0)
            self.grid_columnconfigure(1, weight = 1)

            self.backButton = tk.Canvas(self, width = self.height, height = self.height, bg = Display.tkColor(colors[1]), highlightthickness = 0, relief = tk.RAISED, bd = 2)

            arrowSize = self.height * 3 / 4
            arrowTL = self.height * 1 / 8
            self.backButton.create_polygon(arrowTL, arrowTL + arrowSize / 2,
                                           arrowTL + arrowSize / 2, arrowTL,
                                           arrowTL + arrowSize / 2, arrowTL + arrowSize / 4,
                                           arrowTL + arrowSize, arrowTL + arrowSize / 4,
                                           arrowTL + arrowSize, arrowTL + arrowSize * 3 / 4,
                                           arrowTL + arrowSize / 2, arrowTL + arrowSize * 3 / 4,
                                           arrowTL + arrowSize / 2, arrowTL + arrowSize,
                                           arrowTL, arrowTL + arrowSize / 2,
                                           fill = Display.tkColor(colors[2]))

            self.backButton.xview_moveto(0)
            self.backButton.yview_moveto(0)

            self.backButton.grid(row = 0, column = 0, sticky = tk.N + tk.S + tk.W, padx = 2.5, pady = 2.5)
            self.backButton.bind("<Button-1>", self.goBack)

            if(runAction is not None):
                self.runButton = tk.Canvas(self, width = self.height, height = self.height, bg = Display.tkColor(colors[1]), highlightthickness = 0, relief = tk.RAISED, bd = 2)

                arrowSize = self.height * 3 / 4
                arrowTL = self.height * 1 / 8
                self.runButton.create_polygon(arrowTL, arrowTL,
                                              arrowTL + arrowSize, arrowTL + arrowSize / 2,
                                              arrowTL, arrowTL + arrowSize,
                                              arrowTL, arrowTL,
                                              fill = Display.tkColor(colors[2]))

                self.runButton.xview_moveto(0)
                self.runButton.yview_moveto(0)

                self.runButton.grid(row = 0, column = 2, sticky = tk.N + tk.S + tk.E, padx = 2.5, pady = 2.5)
                self.runButton.bind("<Button-1>", runAction)

        def goBack(self, *_):
            self.display.currentPage = self.backPage
