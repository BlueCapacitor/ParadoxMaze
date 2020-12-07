'''
Created on Oct 10, 2020

@author: gosha
'''

from instruction_set import Instruction
from state import State, Result
from tile import TransportTile, ControlTile


class Controller(object):

    def __init__(self, board, robot, instructions, state = None, time = 0, lookValue = False):
        self.time = time

        self.board = board
        self.robot = robot

        if(state is None):
            self.state = State(board)
            self.state.logRobot(self.robot, self.time)
        else:
            self.state = state

        self.instructions = instructions
        self.robot.lookValue = lookValue

    def run(self):
        while(self.robot.chargeRemaining > 0):
            result, lookResult = self.step()

            if(lookResult is not None):
                if(isinstance(lookResult, bool)):
                    self.robot.lookValue = lookResult
                else:
                    controlValue, openValue = lookResult
                    if(controlValue.validity == Result.UNRECOVERABLE_PARADOX):
                        result = Result.UNRECOVERABLE_PARADOX
                        break
                    else:
                        if(controlValue.static):
                            self.robot.lookValue = (controlValue.currentValue and openValue) or not(controlValue.currentValue or openValue)
                        elif(len(controlValue.possibleValues) == 1):
                            value = controlValue.possibleValues[0]
                            self.robot.lookValue = (value and openValue) or not(value or openValue)
                        else:
                            key = self.state.getKeyForControlValue(controlValue)

                            subControllerTrue = self.copy(lookValue = openValue)
                            subControllerTrue.state.controlValueLog[key].assumeValue(True)

                            subControllerFalse = self.copy(lookValue = not(openValue))
                            subControllerFalse.state.controlValueLog[key].assumeValue(False)

                            resultWithTrue = subControllerTrue.run()
                            resultWithFalse = subControllerFalse.run()

                            return(resultWithTrue + resultWithFalse)

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

        tile = self.board.getTile(self.robot.x, self.robot.y)

        if(isinstance(tile, ControlTile)):
            tile.trigger(self.state, self.time)

        if(isinstance(tile, TransportTile)):
            self.robot.x, self.robot.y, self.time = tile.getDestination(self.state, self.time, self.robot)
            self.robot.discontinuePath()

            self.state.logRobot(self.robot, self.time)

        return(self.state.isValid, lookResult if instruction == Instruction.LOOK else None)

    def copy(self, lookValue = False):
        return(Controller(self.board, self.robot.copy(), self.instructions.copy(), state = self.state.copy(), time = self.time, lookValue = lookValue))
