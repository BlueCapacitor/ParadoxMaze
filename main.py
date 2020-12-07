'''
Created on Oct 10, 2020

@author: gosha
'''

from controller import Controller
from csv_map import CSVMap
from display import Display
from instruction_set import InstructionSet


def setUpAndRun():
    csvMap = CSVMap("demoMap/13-demoMap.csv")

    board = csvMap.buildBoard()

    instructionFile = open("instruction_input", 'r')
    instructionStr = instructionFile.read()
    instructions = InstructionSet(instructionStr)

    robot = csvMap.buildRobot()
    controller = Controller(board, robot, instructions)

    display.currentPage = display.Page.CALCULATING

    results = controller.run()
    print(results)

    robotLog = controller.state.robotLog
    for time in sorted(robotLog.keys()):
        print("%s: %s" % (time, robotLog[time]))

    display.board = board
    display.results = results
    display.currentPage = display.Page.STEP
    display.currentPage.page.draw()


if(__name__ == '__main__'):
    display = Display()
    display.title("Time Travel Game")

    display.after(0, setUpAndRun)
    display.mainloop()
