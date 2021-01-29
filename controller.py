'''
Created on Oct 10, 2020

@author: gosha
'''

from instruction_set import Instruction
from state import State, Result, ControlValue
from tile import TransportTile, ControlTile

numberOfRobots = 1


class Controller(object):

    def __init__(self, board, robot, instructions, state = None, time = 0, lookValue = None):
        self.time = time

        self.board = board
        self.robot = robot

        if(state is None):
            self.state = State(board)
            self.state.logRobot(self.robot, self.time)
        else:
            self.state = state

        self.instructions = instructions
        if(lookValue is not None):
            self.robot.lookValue = lookValue

    def run(self):
        global numberOfRobots

        while(self.robot.chargeRemaining > 0):
            result, lookResult, crashLook = self.step()

            if(lookResult is not None and isinstance(crashLook, bool)):
                if(isinstance(lookResult, bool)):
                    self.robot.lookValue = lookResult
                else:
                    controlValue, safeValue = lookResult
                    if(controlValue.validity == Result.UNRECOVERABLE_PARADOX):
                        result = Result.UNRECOVERABLE_PARADOX
                        break
                    else:
                        if(controlValue.static):
                            self.robot.lookValue = (controlValue.currentValue and safeValue) or not(controlValue.currentValue or safeValue)
                        elif(len(controlValue.possibleValues) == 1):
                            value = controlValue.possibleValues[0]
                            self.robot.lookValue = (value and safeValue) or not(value or safeValue)
                        else:
                            numberOfRobots += 1

                            key = self.state.getKeyForControlValue(controlValue)

                            subControllerTrue = self.copy(lookValue = safeValue)
                            subControllerTrue.state.controlValueLog[key].assumeValue(True)

                            subControllerFalse = self.copy(lookValue = not(safeValue))
                            subControllerFalse.state.controlValueLog[key].assumeValue(False)

                            resultWithTrue = subControllerTrue.run()
                            resultWithFalse = subControllerFalse.run()

                            return(resultWithTrue + resultWithFalse)

            if(lookResult is None and not(isinstance(crashLook, bool))):
                controlValue, safeValue = crashLook
                if(controlValue.validity == Result.UNRECOVERABLE_PARADOX):
                    result = Result.UNRECOVERABLE_PARADOX
                    break
                else:
                    if(controlValue.static):
                        safe = (controlValue.curentValue and safeValue) or not(controlValue.curentValue or safeValue)
                        result |= Result.FAIL if not safe else Result.SUCCESS
                    elif(len(controlValue.possibleValues) == 1):
                        value = tuple(controlValue.possibleValues)[0]
                        safe = (value and safeValue) or not(value or safeValue)
                        result |= Result.FAIL if not safe else Result.SUCCESS
                    else:
                        numberOfRobots += 1

                        key = self.state.getKeyForControlValue(controlValue)

                        subControllerTrue = self.copy()
                        subControllerTrue.state.controlValueLog[key].assumeValue(True)

                        subControllerFalse = self.copy()
                        subControllerFalse.state.controlValueLog[key].assumeValue(False)

                        resultWithTrue = subControllerTrue.run()
                        resultWithFalse = subControllerFalse.run()

                        return(resultWithTrue + resultWithFalse)

                # TODO: Check for both lookResult is not None and not(isinstance(crashLook, bool))   (split controller into 4)

            if(result == Result.SUCCESS):
                break
            if(result == Result.RECOVERABLE_PARADOX):
                continue
            if(result == Result.UNRECOVERABLE_PARADOX):
                break
            if(result == Result.NO_SUCCESS):
                continue
            if(result == Result.FAIL):
                break

        if(result == Result.RECOVERABLE_PARADOX):
            result = Result.UNRECOVERABLE_PARADOX
        if(result == Result.NO_SUCCESS):
            result = Result.FAIL
        if(result == Result.POTENTIAL_SUCCESS):
            result = Result.SUCCESS

        numberOfRobots -= 1
        return([(result, self.state)])

    def step(self):
        instruction = self.instructions.nextInstruction(self.robot)
        if(instruction == Instruction.SLEEP):
            pass
        if(instruction == Instruction.LEFT):
            self.robot.turnLeft()
        if(instruction == Instruction.RIGHT):
            self.robot.turnRight()
        if(instruction == Instruction.FORWARD):
            self.robot.moveForward()
        if(instruction == Instruction.SLEEP):
            self.robot.sleep()
        if(instruction == Instruction.LOOK):
            lookResult = self.robot.look(self.state, self.time)
        if(instruction == Instruction.DEBUG):
            print("@@@@ Debug @@@@")
            return((Result.NO_SUCCESS, None))

        self.time += 1
        self.state.logRobot(self.robot, self.time)

        crashLook = self.robot.crashLook(self.state, self.time)

        tile = self.board.getTile(self.robot.x, self.robot.y)

        if(isinstance(tile, ControlTile)):
            tile.trigger(self.state, self.time)

        if(isinstance(tile, TransportTile)):
            self.robot.x, self.robot.y, self.time = tile.getDestination(self.state, self.time, self.robot)
            self.robot.discontinuePath()

            self.state.logRobot(self.robot, self.time)

        return(self.state.isValid, lookResult if instruction == Instruction.LOOK else None, crashLook)

    def copy(self, lookValue = None):
        return(Controller(self.board, self.robot.copy(), self.instructions.copy(), state = self.state.copy(), time = self.time, lookValue = lookValue))
