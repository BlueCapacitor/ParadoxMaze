from abc import ABC, abstractmethod
from enum import Enum


class InstructionSet(object):

    def __init__(self, instruction_str, done=False, instructions=None, stack=None):
        self.instruction_str = instruction_str
        self.done = done

        if instructions is None:
            self.instruction_names = {}
            for instruction in Instruction:
                self.instruction_names[instruction.value] = instruction
            self.instruction_names["function:"] = ParseObject
            self.instruction_names["repeat"] = Repeat
            self.instruction_names["forever"] = Forever
            self.instruction_names["ifOpen"] = IfOpen
            self.instruction_names["ifClosed"] = IfClosed

            self.instructions = ParseObject()
            self.parse(self.instructions, instruction_str)
        else:
            self.instructions = instructions

        if stack is None:
            self.stack = [-1]
        else:
            self.stack = stack

    def copy(self):
        return (InstructionSet(self.instruction_str, done=self.done, instructions=self.instructions.copy(),
                               stack=list(self.stack)))

    def parse(self, parse_object, code):
        location = 0

        while location < len(code):
            read_buffer = ""
            while code[location] not in (";", "{", "}", "(", ")"):

                if code[location] not in (" ", "\n", "\t"):
                    read_buffer += code[location]

                if len(read_buffer) >= 2 and read_buffer[-2:] == "//":
                    read_buffer = read_buffer[:-2]
                    while location < len(code) and code[location] != "\n":
                        location += 1

                location += 1

                if location >= len(code) and read_buffer == "":
                    break

                assert (location <= len(code) - 1), "unexpected end of phrase"

            else:
                if read_buffer in self.instruction_names.keys():
                    block_type = self.instruction_names[read_buffer]
                    if block_type in tuple(Instruction):
                        parse_object.add_block(block_type)
                        location += 1

                    elif block_type == Forever:
                        assert code[location] == "{", "forever should be followed by {, not %s" % (code[location])
                        block_code = self.isolate_delimited_range(code[location + 1:], "{", "}")
                        location += 2 + len(block_code)

                        block = Forever()
                        self.parse(block, block_code)
                        parse_object.add_block(block)

                    elif block_type == Repeat:
                        assert code[location] == "(", "repeat should be followed by (, not %s" % (code[location])
                        repeat_number_string = self.isolate_delimited_range(code[location + 1:], "(", ")")
                        location += 2 + len(repeat_number_string)
                        assert code[location] == "{", "repeat(_) should be followed by {, not %s" % (code[location])
                        block_code = self.isolate_delimited_range(code[location + 1:], "{", "}")
                        location += 2 + len(block_code)

                        block = Repeat(int(repeat_number_string))
                        self.parse(block, block_code)
                        parse_object.add_block(block)

                    elif block_type == IfOpen:
                        assert code[location] == "{", "ifOpen should be followed by {, not %s" % (code[location])
                        block_code = self.isolate_delimited_range(code[location + 1:], "{", "}")
                        location += 2 + len(block_code)

                        block = IfOpen()
                        self.parse(block, block_code)
                        parse_object.add_block(block)

                    elif block_type == IfClosed:
                        assert code[location] == "{", "ifClosed should be followed by {, not %s" % (code[location])
                        block_code = self.isolate_delimited_range(code[location + 1:], "{", "}")
                        location += 2 + len(block_code)

                        block = IfClosed()
                        self.parse(block, block_code)
                        parse_object.add_block(block)

                else:
                    assert False, "Unrecognized command: \"%s\"" % read_buffer

    @staticmethod
    def isolate_delimited_range(code, open_delimiter, close_delimiter):
        depth = 1
        for i in range(len(code)):
            char = code[i]
            if char == close_delimiter:
                depth -= 1

            if char == open_delimiter:
                depth += 1

            if depth == 0:
                return code[:i]

    def next_instruction(self, robot):
        if self.done:
            return Instruction.SLEEP

        try:
            self.step_stack(robot)
        except StopIteration:
            self.done = True
            return Instruction.SLEEP

        out = self.get_stack_item(self.stack, self.instructions)

        if out == Instruction.STOP:
            self.done = True
            return Instruction.SLEEP

        return out

    def step_stack(self, robot):
        self.step_and_pop()

        while True:
            if (isinstance((item := self.get_stack_item(self.stack, self.instructions)),
                           Conditional) and not item.evaluate_condition(robot)):  # @IgnorePep8
                self.step_and_pop()

            if self.get_stack_item(self.stack, self.instructions) == Instruction.BREAK and len(self.stack) > 1:
                self.stack = self.stack[:-1]
                while len(self.stack) > 1 and not\
                        (isinstance(self.get_stack_item(self.stack, self.instructions), Loop)):
                    self.stack = self.stack[:-1]

                self.step_and_pop()

            needed = self.step_up_stack_if_needed()
            if not needed:
                break

    def step_and_pop(self):
        self.stack[-1] += 1

        while self.pop_stack_if_needed():
            pass

    def pop_stack_if_needed(self):
        if len(self.stack) == 0:
            raise StopIteration
        container_object = self.get_stack_item(self.stack[:-1], self.instructions)
        if self.stack[-1] >= len(container_object.code):
            if isinstance(container_object, Loop) and not container_object.done:
                container_object.loop_done()
                self.stack[-1] = 0
            else:
                self.pop_stack()
            return True
        return False

    def pop_stack(self):
        self.stack = self.stack[:-1]
        if len(self.stack) == 0:
            raise StopIteration
        self.stack[-1] += 1

    def step_up_stack_if_needed(self):
        if len(self.stack) == 0:
            raise StopIteration
        block = self.get_stack_item(self.stack, self.instructions)
        if isinstance(block, ParseObject):
            self.step_up_stack()
            if isinstance(block, Loop):
                block.loop_entered()

            return True

        return False

    def step_up_stack(self):
        self.stack.append(0)

    @staticmethod
    def get_stack_item(stack, instruction):
        for block_num in stack:
            instruction = instruction.code[block_num]
        return instruction


class ParseObject(object):

    def __init__(self, code=()):
        self.code = list(code)

    def copy(self):
        return type(self)(code=list(map(lambda block: block.copy(), self.code)))

    def add_block(self, block):
        self.code.append(block)

    def __str__(self):
        return (type(self).__name__ + "\n" + "\n".join(
            map(lambda block: "  " + "\n  ".join(str(block).split("\n")), self.code)))


class Loop(ABC, ParseObject):

    @property
    @abstractmethod
    def done(self):
        pass

    def loop_done(self):
        pass

    def loop_entered(self):
        pass


class Forever(Loop):

    @property
    def done(self):
        return False


class Repeat(Loop):

    def __init__(self, repeat_num, code=(), remaining=None):
        super().__init__(code=code)
        self.repeat_num = repeat_num
        self.remaining = remaining

    def copy(self):
        return (
            type(self)(self.repeat_num,
                       code=list(map(lambda block: block.copy(), self.code)),
                       remaining=self.remaining))

    def loop_done(self):
        self.remaining -= 1

    def loop_entered(self):
        self.remaining = self.repeat_num - 1

    @property
    def done(self):
        return self.remaining <= 0


class Conditional(ABC, ParseObject):

    @abstractmethod
    def evaluate_condition(self, _robot):
        pass


class IfOpen(Conditional):

    def evaluate_condition(self, robot):
        return robot.look_value


class IfClosed(Conditional):

    def evaluate_condition(self, robot):
        return not robot.look_value


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
        return self

    def __str__(self):
        return self.value
