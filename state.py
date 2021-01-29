'''
Created on Oct 10, 2020

@author: gosha
'''

from enum import Enum

from tile import TargetTile


class State(object):

    def __init__(self, board, robotLog = None, controlValueLog = None, stickyValues = None):
        self.board = board
        if(robotLog is None):
            self.robotLog = {}
        else:
            self.robotLog = robotLog

        if(controlValueLog is None):
            self.controlValueLog = {}
        else:
            self.controlValueLog = dict(map(lambda entry: (entry[0], entry[1].copy(state = self)), controlValueLog.items()))

        if(stickyValues is None):
            self.stickyValues = {}
        else:
            self.stickyValues = stickyValues

    def copy(self):
        return(State(self.board,
                     dict(map(lambda entry: (entry[0], entry[1].copy()), self.robotLog.items())),
                     self.controlValueLog,
                     dict(self.stickyValues)))

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
            currentValue = False

            self.controlValueLog[(controlID, time)] = ControlValue(self, time, controlID, currentValue)

        return(self.controlValueLog[(controlID, time)])

    def getKeyForControlValue(self, controlValue):
        for key in self.controlValueLog.keys():
            if(self.controlValueLog[key] == controlValue):
                return(key)

    def setStickyValue(self, controlID, time, value):
        self.stickyValues[(controlID, time)] = value

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
                if(tile.isFatal(self, time) and tile.isStatic):
                    out = self.failAndFinalize(out)
                    break
                if(not(tile.isStatic)):
                    if(not(self.board.hasTimeTravel)):
                        if(not(tile.crashLook(self, time))):
                            out = self.failAndFinalize(out)
                    else:
                        controlValue, safeValue = tile.crashLook(self, time)
                        if(controlValue.static and controlValue.curentValue != safeValue):
                            out = self.failAndFinalize(out)

                if(not self.board.checkBounds(robotTrace)):
                    out = self.failAndFinalize(out)
                    break
                if(isinstance(tile, TargetTile)):
                    targets[tile] = True
                    continue

        if(out == Result.NO_SUCCESS and all(targets.values())):
            out = Result.POTENTIAL_SUCCESS

        return(out)

    def failAndFinalize(self, result):
        result |= Result.FAIL
        if(result == Result.RECOVERABLE_PARADOX):
            result = Result.UNRECOVERABLE_PARADOX
        return(result)

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

    def __init__(self, state, time, controlID, currentValue, possibleValues = {True, False}, static = False):
        self.state = state
        self.time = time
        self.controlID = controlID
        self._curentValue = currentValue
        self.possibleValues = possibleValues
        self.static = static

    def setCurrentValue(self, value, static):
        if(not(self.static)):
            self._curentValue = value
            self.static = static

    @property
    def curentValue(self):
        value = self._curentValue

        maxTime = None
        for ((controlID, time), stickyValue) in self.state.stickyValues.items():
            if(controlID == self.controlID and (maxTime is None or time > maxTime) and time <= self.time):
                value = stickyValue
                maxTime = time

        return(value)

    @property
    def validity(self):
        if(not(self.state.board.hasTimeTravel)):
            return(Result.SUCCESS)
        if(self.curentValue in self.possibleValues):
            return(Result.SUCCESS)
        else:
            if(self.static or len(self.possibleValues) == 0):
                return(Result.UNRECOVERABLE_PARADOX)
            else:
                return(Result.RECOVERABLE_PARADOX)

    def assumeValue(self, value):
        self.possibleValues &= {value}

    def copy(self, state = None, time = None):
        return(ControlValue(self.state if state is None else state, self.time if time is None else time, self.controlID, self.curentValue, set(self.possibleValues), self.static))
