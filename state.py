'''
Created on Oct 10, 2020

@author: gosha
'''

from enum import Enum

from tile import TargetTile


class State(object):

    def __init__(self, board, robotLog = None, controlValueLog = None):
        self.board = board
        if(robotLog is None):
            self.robotLog = {}
        else:
            self.robotLog = robotLog

        if(controlValueLog is None):
            self.controlValueLog = {}
        else:
            self.controlValueLog = controlValueLog

    def copy(self):
        return(State(self.board, dict(map(lambda entry: (entry[0], entry[1].copy()), self.robotLog.items())), dict(map(lambda entry: (entry[0], entry[1].copy()), self.controlValueLog.items()))))

    def getRobotsAtTime(self, time):
        return(self.robotLog[time] if time in self.robotLog.keys() else [])

    def getAllRobots(self):
        return(sum(self.robotLog.values(), []))

    def getRobotWithCharge(self, charge):
        for time in self.robotLog.keys():
            for robot in self.robotLog[time]:
                if(robot.chargeRemaining == charge):
                    return(robot, time)

    def logRobot(self, robot, time):
        if(time not in self.robotLog.keys()):
            self.robotLog[time] = []

        self.robotLog[time].append(robot.makeTrace())

    def getControlValue(self, controlID, time):
        if((controlID, time) not in self.controlValueLog.keys()):
            self.controlValueLog[(controlID, time)] = ControlValue()

        return(self.controlValueLog[(controlID, time)])

    def getKeyForControlValue(self, controlValue):
        for key in self.controlValueLog.keys():
            if(self.controlValueLog[key] == controlValue):
                return(key)

    @property
    def isValid(self):
        out = Result.NO_SUCCESS

        for controlID, time in self.controlValueLog.keys():
            controlValue = self.controlValueLog[(controlID, time)]
            out |= controlValue.validity

        targets = {tile: False for tile in self.board.getTargets()}

        for time in self.robotLog.keys():
            for robotTrace in self.robotLog[time]:
                tile = self.board.getTile(robotTrace.x, robotTrace.y)
                if(tile.isSolid(self, time) and tile.isStatic):
                    out |= Result.FAIL
                    break
                if(not self.board.checkBounds(robotTrace)):
                    out |= Result.FAIL
                    break
                if(isinstance(tile, TargetTile)):
                    targets[tile] = True
                    continue

        if(out == Result.NO_SUCCESS and all(targets.values())):
            out = Result.POTENTIAL_SUCCESS

        return(out)

    @property
    def maxTime(self):
        return(max(self.robotLog.keys()))

    @property
    def minTime(self):
        return(min(self.robotLog.keys()))

    @property
    def maxCharge(self):
        return(None if self.getAllRobots() == [] else self.getAllRobots()[0].initialCharge)

    @property
    def minCharge(self):
        return(min(map(lambda robot: robot.chargeRemaining, self.getAllRobots())))


class Result(Enum):
    SUCCESS = 1
    POTENTIAL_SUCCESS = 2
    NO_SUCCESS = 3
    FAIL = 4
    RECOVERABLE_PARADOX = 5
    UNRECOVERABLE_PARADOX = 6

    def __or__(self, other):
        return(self if self.value > other.value else other)


class ControlValue():

    def __init__(self, currentValue = False, possibleValues = {True, False}, static = False):
        self.curentValue = currentValue
        self.possibleValues = possibleValues
        self.static = static

    def setState(self, value, static):
        if(not(self.static)):
            self.curentValue = value
            self.static = static

    @property
    def validity(self):
        if(self.curentValue in self.possibleValues):
            return(Result.SUCCESS)
        else:
            if(self.static or len(self.possibleValues) == 0):
                return(Result.UNRECOVERABLE_PARADOX)
            else:
                return(Result.RECOVERABLE_PARADOX)

    def assumeValue(self, value):
        self.possibleValues &= {value}

    def copy(self):
        return(ControlValue(self.curentValue, set(self.possibleValues), self.static))
