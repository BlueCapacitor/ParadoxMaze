'''
Created on Oct 10, 2020

@author: gosha
'''

from abc import ABC, abstractmethod
from enum import Enum


class InstructionSet(object):

    def __init__(self, instructionStr, done = False, instructions = None, stack = None):
        self.instructionStr = instructionStr
        self.done = done

        if(instructions is None):
            self.instructionNames = {}
            for instruction in Instruction:
                self.instructionNames[instruction.value] = instruction
            self.instructionNames["function:"] = ParseObject
            self.instructionNames["repeat"] = Repeat
            self.instructionNames["forever"] = Forever
            self.instructionNames["ifOpen"] = IfOpen
            self.instructionNames["ifClosed"] = IfClosed

            self.instructions = ParseObject()
            self.parse(self.instructions, instructionStr)
        else:
            self.instructions = instructions

        if(stack is None):
            self.stack = [-1]
        else:
            self.stack = stack

    def copy(self):
        return(InstructionSet(self.instructionStr, done = self.done, instructions = self.instructions.copy(), stack = list(self.stack)))

    def parse(self, parseObject, code):
        location = 0

        while(location < len(code)):
            readBuffer = ''
            while(code[location] not in (';', '{', '}', '(', ')')):

                if(code[location] not in (' ', '\n', '\t')):
                    readBuffer += code[location]

                if(len(readBuffer) >= 2 and readBuffer[-2:] == "//"):
                    readBuffer = readBuffer[:-2]
                    while(location < len(code) and code[location] != '\n'):
                        location += 1

                location += 1

                if(location >= len(code) and readBuffer == ''):
                    break

                assert (location <= len(code) - 1), "unexpected end of phrase"

            else:
                if(readBuffer in self.instructionNames.keys()):
                    blockType = self.instructionNames[readBuffer]
                    if(blockType in tuple(Instruction)):
                        parseObject.addBlock(blockType)
                        location += 1

                    elif(blockType == Forever):
                        assert code[location] == '{', "forever should be followed by {, not %s" % (code[location])
                        blockCode = self.isolateDelimitedRange(code[location + 1:], '{', '}')
                        location += 2 + len(blockCode)

                        block = Forever()
                        self.parse(block, blockCode)
                        parseObject.addBlock(block)

                    elif(blockType == Repeat):
                        assert code[location] == '(', "repeat should be followed by (, not %s" % (code[location])
                        repeatNumberString = self.isolateDelimitedRange(code[location + 1:], '(', ')')
                        location += 2 + len(repeatNumberString)
                        assert code[location] == '{', "repeat(_) should be followed by {, not %s" % (code[location])
                        blockCode = self.isolateDelimitedRange(code[location + 1:], '{', '}')
                        location += 2 + len(blockCode)

                        block = Repeat(int(repeatNumberString))
                        self.parse(block, blockCode)
                        parseObject.addBlock(block)

                    elif(blockType == IfOpen):
                        assert code[location] == '{', "ifOpen should be followed by {, not %s" % (code[location])
                        blockCode = self.isolateDelimitedRange(code[location + 1:], '{', '}')
                        location += 2 + len(blockCode)

                        block = IfOpen()
                        self.parse(block, blockCode)
                        parseObject.addBlock(block)

                    elif(blockType == IfClosed):
                        assert code[location] == '{', "ifClosed should be followed by {, not %s" % (code[location])
                        blockCode = self.isolateDelimitedRange(code[location + 1:], '{', '}')
                        location += 2 + len(blockCode)

                        block = IfClosed()
                        self.parse(block, blockCode)
                        parseObject.addBlock(block)

                else:
                    assert False, "Unrecognized command: '%s'" % (readBuffer)

    def isolateDelimitedRange(self, code, openDelimiter, closeDelimiter):
        depth = 1
        for i in range(len(code)):
            char = code[i]
            if(char == closeDelimiter):
                depth -= 1

            if(char == openDelimiter):
                depth += 1

            if(depth == 0):
                return(code[:i])

    def nextInstruction(self, robot):
        if(self.done):
            return(Instruction.SLEEP)

        try:
            self.stepStack(robot)
        except StopIteration:
            self.done = True
            return(Instruction.SLEEP)

        out = self.getStackItem(self.stack, self.instructions)

        if(out == Instruction.STOP):
            self.done = True
            return(Instruction.SLEEP)

        return(out)

    def stepStack(self, robot):
        self.stepAndPop()

        while(True):
            if(isinstance((item := self.getStackItem(self.stack, self.instructions)), Conditional) and not item.evaluateCondition(robot)):  # @IgnorePep8
                self.stepAndPop()

            if(self.getStackItem(self.stack, self.instructions) == Instruction.BREAK and len(self.stack) > 1):
                self.stack = self.stack[:-1]
                while(len(self.stack) > 1 and not(isinstance(self.getStackItem(self.stack, self.instructions), Loop))):
                    self.stack = self.stack[:-1]

                self.stepAndPop()

            needed = self.stepUpStackIfNeeded()
            if(not(needed)):
                break

    def stepAndPop(self):
        self.stack[-1] += 1

        while(self.popStackIfNeeded()):
            pass

    def popStackIfNeeded(self):
        if(len(self.stack) == 0):
            raise StopIteration
        containerObject = self.getStackItem(self.stack[:-1], self.instructions)
        if(self.stack[-1] >= len(containerObject.code)):
            if(isinstance(containerObject, Loop) and not containerObject.done):
                containerObject.loopDone()
                self.stack[-1] = 0
            else:
                self.popStack()
            return(True)
        return(False)

    def popStack(self):
        self.stack = self.stack[:-1]
        if(len(self.stack) == 0):
            raise StopIteration
        self.stack[-1] += 1

    def stepUpStackIfNeeded(self):
        if(len(self.stack) == 0):
            raise StopIteration
        block = self.getStackItem(self.stack, self.instructions)
        if(isinstance(block, ParseObject)):
            self.stepUpStack()
            if(isinstance(block, Loop)):
                block.loopEntered()

            return(True)

        return(False)

    def stepUpStack(self):
        self.stack.append(0)

    def getStackItem(self, stack, instruction):
        for blockNum in stack:
            instruction = instruction.code[blockNum]
        return(instruction)

    def syntaxError(self, message = ''):
        lineNumber = len(self.instructionStr[:self.readPointer].split('\n'))
        offset = len(self.instructionStr[:self.readPointer].split('\n')[-1])
        lineText = self.instructionStr.split('\n')[lineNumber - 1]

        raise SyntaxError(message, ("<instructions>", lineNumber, offset, lineText))


class ParseObject(object):

    def __init__(self, code = []):
        self.code = list(code)

    def copy(self):
        return(type(self)(code = list(map(lambda block: block.copy(), self.code))))

    def addBlock(self, block):
        self.code.append(block)

    def __str__(self):
        return(type(self).__name__ + '\n' + '\n'.join(map(lambda block: "  " + "\n  ".join(str(block).split('\n')), self.code)))


class Loop(ABC, ParseObject):

    @property
    @abstractmethod
    def done(self):
        pass

    def loopDone(self):
        pass

    def loopEntered(self):
        pass


class Forever(Loop):

    @property
    def done(self):
        return(False)


class Repeat(Loop):

    def __init__(self, repeatNum, code = []):
        super().__init__(code = code)
        self.repeatNum = repeatNum

    def copy(self):
        return(type(self)(self.repeatNum, code = list(map(lambda block: block.copy(), self.code))))

    def loopDone(self):
        self.remaining -= 1

    def loopEntered(self):
        self.remaining = self.repeatNum - 1

    @property
    def done(self):
        return(self.remaining <= 0)


class Conditional(ABC, ParseObject):

    @abstractmethod
    def evaluateCondition(self, _robot):
        pass


class IfOpen(Conditional):

    def evaluateCondition(self, robot):
        return(robot.lookValue)


class IfClosed(Conditional):

    def evaluateCondition(self, robot):
        return(not(robot.lookValue))


class Instruction(Enum):
    SLEEP = "slp"
    FORWARD = "fd"
    LEFT = "lt"
    RIGHT = "rt"
    LOOK = "look"
    DEBUG = "debug"
    BREAK = "break"
    STOP = "stop"

    def copy(self):
        return(self)

    def __str__(self):
        return(self.value)
