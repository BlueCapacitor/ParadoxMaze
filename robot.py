'''
Created on Oct 10, 2020

@author: gosha
'''

from enum import Enum


class StaticRobot(object):

    def __init__(self, x, y, direction, chargeRemaining, initialCharge, continuityID = 0, lookValue = False):
        self.x = x
        self.y = y
        self.chargeRemaining = chargeRemaining
        self.initialCharge = initialCharge
        self.direction = direction
        self.continuityID = continuityID
        self.lookValue = lookValue

    @property
    def forwardX(self):
        return(self.x + self.direction.dx)

    @property
    def forwardY(self):
        return(self.y + self.direction.dy)

    def copy(self):
        return(StaticRobot(self.x, self.y, self.direction, self.chargeRemaining, self.initialCharge, continuityID = self.continuityID, lookValue = self.lookValue))

    def __str__(self):
        return("<RobotTrace: (%s, %s) facing %s, charge: %s>" % (self.x, self.y, self.direction.strName, self.chargeRemaining))

    def __repr__(self):
        return(str(self))


class Robot(StaticRobot):

    def __init__(self, x, y, direction, chargeRemaining, initialCharge, continuityID = 0, lookValue = False):
        super().__init__(x, y, direction, chargeRemaining, initialCharge, continuityID = continuityID, lookValue = lookValue)

    def sleep(self):
        self.chargeRemaining -= 1

    def look(self, state, time):
        self.chargeRemaining -= 1
        tile = state.board.getTile(self.forwardX, self.forwardY)
        return(tile.look(state, time) if not(tile.isStatic) else not(tile.isSolid(state, time)))

    def crashLook(self, state, time):
        tile = state.board.getTile(self.x, self.y)
        return(tile.crashLook(state, time) if not(tile.isStatic) else not(tile.isFatal(state, time)))

    def turnLeft(self):
        self.direction = self.direction.left()
        self.chargeRemaining -= 1

    def turnRight(self):
        self.direction = self.direction.right()
        self.chargeRemaining -= 1

    def moveForward(self):
        self.x, self.y = self.forwardX, self.forwardY
        self.chargeRemaining -= 1

    def discontinuePath(self):
        self.continuityID += 1

    def copy(self):
        return(Robot(self.x, self.y, self.direction, self.chargeRemaining, self.initialCharge, continuityID = self.continuityID, lookValue = self.lookValue))

    def makeTrace(self):
        return(super().copy())


class Direction(Enum):
    RIGHT = (0, 1, 0, "right")
    UP = (1, 0, -1, "up")
    LEFT = (2, -1, 0, "left")
    DOWN = (3, 0, 1, "down")

    def __new__(cls, val, _dx, _dy, _strName):
        obj = object.__new__(cls)
        obj._value_ = val
        return(obj)

    def __init__(self, _val, dx, dy, strName):
        self.dx = dx
        self.dy = dy
        self.strName = strName

    def left(self):
        return(Direction((self.value + 1) % 4))

    def right(self):
        return(Direction((self.value - 1) % 4))

    def opposite(self):
        return(Direction((self.value + 2) % 4))
