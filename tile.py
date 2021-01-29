'''
Created on Oct 10, 2020

@author: gosha
'''
from abc import ABC, abstractmethod


def getColorForId(n):
    colorShift = 7
    color = [1, 1, 0]
    for _ in range((n * colorShift) % 12):
        color = shiftNextHue(color)
    return(color)


def shiftNextHue(prev):
    case = sum(prev)
    if(case == 1):
        oneIndex = prev.index(1)
        nextColor = [0, 0, 0]
        nextColor[oneIndex] = 1
        nextColor[(oneIndex + 1) % 3] = 0.5
    if(case == 1.5):
        oneIndex = prev.index(1)
        nextColor = [0, 0, 0]
        nextColor[oneIndex] = 1
        nextColor[(oneIndex + 1) % 3] = 1 if prev[(oneIndex + 1) % 3] == 0.5 else 0
    if(case == 2):
        zeroIndex = prev.index(0)
        nextColor = [0, 0, 0]
        nextColor[(zeroIndex + 1) % 3] = 0.5
        nextColor[(zeroIndex + 2) % 3] = 1

    return(nextColor)


class EmptyTile(object):

    isStatic = True
    isTimeTravel = False

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def isSolid(self, _state, _time):
        return(False)

    def isFatal(self, state, time):
        return(self.isSolid(state, time))

    def getColors(self, _state, _time):
        return(((0.75, 0.75, 0.75),
                (1, 1, 1)))

    def getText(self, _state, _time):
        return('', (0, 0, 0))

    def couldBeFatal(self, _state, _time):
        return(False)


class WallTile(EmptyTile):

    def isSolid(self, _state, _time):
        return(True)

    def getColors(self, _state, _time):
        return(((0.25, 0.25, 0.25),
                (0, 0, 0)))


class LavaTile(EmptyTile):

    def isFatal(self, _state, _time):
        return(True)

    def getColors(self, _state, _time):
        return(((1, 0, 0),
                (1, 0.25, 0)))


class HologramTile(EmptyTile):

    def isFatal(self, _state, _time):
        return(False)

    def isSolid(self, _state, _time):
        return(True)

    def getColors(self, _state, _time):
        return(((0.5, 0.5, 1),
                (0.75, 0.75, 1)))


class TargetTile(EmptyTile):

    def getColors(self, state, time):
        for checkTime in range(state.minTime, time + 1):
            for robotTrace in state.getRobotsAtTime(checkTime):
                if(robotTrace.x == self.x and robotTrace.y == self.y):
                    return(((0.5, 0.5, 0.5),
                            (0.5, 0.5, 0.5),
                            (1, 1, 1)))
        return((0.5, 0.5, 0.5),
               (0.75, 0.75, 0.75),
               (1, 1, 1))


class DestinationTile(EmptyTile):

    def __init__(self, x, y, letter = '', color = None):
        super().__init__(x, y)

        self.letter = letter

        if(color is None):
            color = getColorForId(ord(letter))

        self.onColor = color
        self.offColor = (0.5 + color[0] / 2, 0.5 + color[1] / 2, 0.5 + color[2] / 2)

    def getColors(self, state, time):
        for robotTrace in state.getRobotsAtTime(time):
            if(robotTrace.x == self.x and robotTrace.y == self.y):
                return(((0.75, 0.75, 0.75),
                        self.onColor))
        return(((0.75, 0.75, 0.75),
                self.offColor))

    def getText(self, _state, _time):
        return((self.letter, (0.25, 0.25, 0.25)))


class TransportTile(EmptyTile, ABC):

    @abstractmethod
    def getDestination(self, _state, _time, _robot):
        pass  # return((newX, newY, newTime))


class PortalTile(TransportTile):

    def __init__(self, x, y, destinationTile):
        super().__init__(x, y)
        self.destinationTile = destinationTile

    def getDestination(self, _state, time, _robot):
        return((self.destinationTile.x, self.destinationTile.y, time))

    def getColors(self, state, time):
        for robotTrace in state.getRobotsAtTime(time):
            if(robotTrace.x == self.x and robotTrace.y == self.y):
                return(((0, 0, 0),
                        self.destinationTile.onColor))
        return(((0, 0, 0),
                self.destinationTile.offColor))

    def getText(self, _state, _time):
        return((self.destinationTile.letter.upper(), (0.25, 0.25, 0.25)))


class TimeGateTile(TransportTile):

    isTimeTravel = True

    def __init__(self, x, y, dt):
        super().__init__(x, y)
        self.dt = dt

    def getDestination(self, _state, time, _robot):
        return((self.x, self.y, time + self.dt))

    def getColors(self, _state, _time):
        return(((0.25, 0, 0.75) if self.dt < 0 else (0.75, 0.5, 0) if self.dt > 0 else (0.75, 0.75, 0.75),
                (0.25, 0.25, 0.25)))

    def getText(self, _state, _time):
        return(str(self.dt) if self.dt < 0 else '+' + str(self.dt), (1, 1, 1))


class CloseTimedDoorTile(EmptyTile):

    def __init__(self, x, y, triggerTime):
        super().__init__(x, y)
        self.triggerTime = triggerTime

    def isSolid(self, _state, time):
        return(time >= self.triggerTime)

    def getColors(self, _state, time):
        return(((0.5, 0.25, 0.25),
                (0, 0, 0) if time >= self.triggerTime else (1, 1, 1)))

    def getText(self, _state, time):
        return(('' if time >= self.triggerTime else str(self.triggerTime - time), (0.25, 0.25, 0.25)))


class OpenTimedDoorTile(EmptyTile):

    def __init__(self, x, y, triggerTime):
        super().__init__(x, y)
        self.triggerTime = triggerTime

    def isSolid(self, _state, time):
        return(time < self.triggerTime)

    def getColors(self, _state, time):
        return(((0.5, 0.5, 0.25),
                (0, 0, 0) if time < self.triggerTime else (1, 1, 1)))

    def getText(self, _state, time):
        return(('' if time >= self.triggerTime else str(self.triggerTime - time), (0.75, 0.75, 0.75)))


class TimePortalTile(TransportTile):

    isTimeTravel = True

    def __init__(self, x, y, destT):
        super().__init__(x, y)
        self.destT = destT

    def getDestination(self, _state, _time, _robot):
        return((self.x, self.y, self.destT))

    def getColors(self, _state, _time):
        return(((0.0, 0.0, 0.25),
                (0.25, 0.25, 0.25)))

    def getText(self, _state, _time):
        return(str(self.destT), (1, 1, 1))


class ControlTile(EmptyTile, ABC):

    @abstractmethod
    def trigger(self, _state, _time):
        pass


class ButtonTile(ControlTile):

    def __init__(self, x, y, controlID):
        super().__init__(x, y)
        self.controlID = controlID

        self.color = getColorForId(controlID)

    def trigger(self, state, time):
        controlValue = state.getControlValue(self.controlID, time)
        controlValue.setCurrentValue(True, True)

    def getColors(self, state, time):
        for robotTrace in state.getRobotsAtTime(time):
            if(robotTrace.x == self.x and robotTrace.y == self.y):
                return(((0.5, 0.5, 0.5),
                        (0.5, 0.5, 0.5),
                        self.color))
        return((0.5, 0.5, 0.5),
               (0.75, 0.75, 0.75),
               self.color)

    def getText(self, _state, _time):
        return((self.controlID, (0, 0, 0)))


class OnToggleTile(ControlTile):

    def __init__(self, x, y, controlID):
        super().__init__(x, y)
        self.controlID = controlID

        self.color = getColorForId(controlID)

    def trigger(self, state, time):
        state.setStickyValue(self.controlID, time, True)

    def getColors(self, state, time):
        if(state.getControlValue(self.controlID, time).curentValue):
            return(((0.5, 0.5, 0.5),
                    (0.5, 0.75, 0.5),
                    self.color))
        return((0.5, 0.5, 0.5),
               (0.75, 1, 0.75),
               self.color)

    def getText(self, _state, _time):
        return((self.controlID, (0, 0, 0)))


class OffToggleTile(ControlTile):

    def __init__(self, x, y, controlID):
        super().__init__(x, y)
        self.controlID = controlID

        self.color = getColorForId(controlID)

    def trigger(self, state, time):
        state.setStickyValue(self.controlID, time, False)

    def getColors(self, state, time):
        if(not(state.getControlValue(self.controlID, time).curentValue)):
            return(((0.5, 0.5, 0.5),
                    (0.5, 0.75, 0.5),
                    self.color))
        return((0.5, 0.5, 0.5),
               (0.75, 1, 0.75),
               self.color)

    def getText(self, _state, _time):
        return((self.controlID, (0, 0, 0)))


class NonStaticDoorTile(EmptyTile, ABC):

    isStatic = False

    @abstractmethod
    def look(self, _state, _time):
        pass  # return(controlValue, looksOpenOnValue)

    @abstractmethod
    def crashLook(self, _state, _time):
        pass  # return(controlValue, openOnValue)


class OpenLogicalDoorTile(NonStaticDoorTile):

    def __init__(self, x, y, controlID):
        super().__init__(x, y)
        self.controlID = controlID

        self.color = getColorForId(controlID)

    def isSolid(self, state, time):
        return(not(state.getControlValue(self.controlID, time).curentValue))

    def getColors(self, state, time):
        return(((0.25, 0.5, 0.25),
                (0, 0, 0) if self.isSolid(state, time) else (1, 1, 1),
                self.color))

    def getText(self, _state, _time):
        return((self.controlID, (0, 0, 0)))

    def look(self, state, time):
        if(state.board.hasTimeTravel):
            return((state.getControlValue(self.controlID, time), True))
        else:
            return(state.getControlValue(self.controlID, time).curentValue)

    def crashLook(self, state, time):
        return(self.look(state, time))

    def couldBeFatal(self, state, time):
        controlValue = state.getControlValue(self.controlID, time)
        return(False in controlValue.possibleValues)


class CloseLogicalDoorTile(NonStaticDoorTile):

    def __init__(self, x, y, controlID):
        super().__init__(x, y)
        self.controlID = controlID

        self.color = getColorForId(controlID)

    def isSolid(self, state, time):
        return(state.getControlValue(self.controlID, time).curentValue)

    def getColors(self, state, time):
        return(((0.5, 0.25, 0.25),
                (0, 0, 0) if self.isSolid(state, time) else (1, 1, 1),
                self.color))

    def getText(self, _state, _time):
        return((self.controlID, (0, 0, 0)))

    def look(self, state, time):
        if(state.board.hasTimeTravel):
            return((state.getControlValue(self.controlID, time), False))
        else:
            return(not(state.getControlValue(self.controlID, time).curentValue))

    def crashLook(self, state, time):
        return(self.look(state, time))

    def couldBeFatal(self, state, time):
        controlValue = state.getControlValue(self.controlID, time)
        return(False in controlValue.possibleValues)
