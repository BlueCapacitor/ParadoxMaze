from collections import deque

from language.instruction import Instruction
from language.primitive_instructions import PrimitiveInstruction
from language.resolvable_instructions import ResolvableInstruction
from language.resolvable_instructions.break_ import Break
from language.resolvable_instructions.compound_instructions import CompoundInstruction
from language.resolvable_instructions.compound_instructions.forever import Forever
from language.resolvable_instructions.compound_instructions.if_closed import IfClosed
from language.resolvable_instructions.compound_instructions.if_open import IfOpen
from language.resolvable_instructions.continue_ import Continue
from language.resolvable_instructions.debug import Debug
from language.resolvable_instructions.parametrized_compound_instructions import ParametrizedCompoundInstruction
from language.resolvable_instructions.parametrized_compound_instructions.custom_definition import CustomDefinition
from language.resolvable_instructions.parametrized_compound_instructions.repeat import Repeat
from language.resolvable_instructions.parametrized_instructions import ParametrizedInstruction
from language.resolvable_instructions.parametrized_instructions.function import Function
from language.resolvable_instructions.stop import Stop


class Code(deque):
    def __init__(self, robot, custom_definitions=None, code=None):
        self.robot = robot

        if custom_definitions is None:
            self.custom_definitions = dict()
        else:
            self.custom_definitions = dict(custom_definitions)

        if code is None:
            super().__init__()
            self.set_default_instruction_names()

        elif isinstance(code, Code):
            super().__init__(instruction.copy() for instruction in code)
            self.instruction_names = dict(code.instruction_names)

        elif isinstance(code, str):
            super().__init__()
            self.set_default_instruction_names()
            self.extend(self.parse(code))

    def set_default_instruction_names(self):
        self.instruction_names = {}
        # noinspection PyTypeChecker
        for instruction in PrimitiveInstruction:
            self.instruction_names[instruction.value] = instruction
        self.instruction_names["repeat"] = Repeat
        self.instruction_names["forever"] = Forever
        self.instruction_names["ifOpen"] = IfOpen
        self.instruction_names["ifClosed"] = IfClosed

        self.instruction_names["break"] = Break
        self.instruction_names["continue"] = Continue
        self.instruction_names["stop"] = Stop

        self.instruction_names["debug"] = Debug

        self.instruction_names["def"] = CustomDefinition
        self.instruction_names["fun"] = Function

    def parse(self, code_str):
        location = 0

        out = []

        while location < len(code_str):
            read_buffer = ""

            while code_str[location] not in (";", "{", "}", "(", ")"):

                if code_str[location] not in (" ", "\n", "\t"):
                    read_buffer += code_str[location]

                if len(read_buffer) >= 2 and read_buffer[-2:] == "//":
                    read_buffer = read_buffer[:-2]
                    while location < len(code_str) and code_str[location] != "\n":
                        location += 1

                location += 1

                if location >= len(code_str) and read_buffer == "":
                    break

                assert (location <= len(code_str) - 1), "unexpected end of phrase"

            else:
                if read_buffer == "":
                    location += 1

                elif read_buffer in self.instruction_names.keys():
                    block_type = self.instruction_names[read_buffer]
                    if isinstance(block_type, PrimitiveInstruction):
                        out.append(block_type)
                        location += 1

                    elif issubclass(block_type, ParametrizedCompoundInstruction):
                        assert code_str[location] == "(",\
                            f"{read_buffer} should be followed by (, not {code_str[location]}"
                        parameter_string = self.isolate_delimited_range(code_str[location + 1:], "(", ")")
                        location += 2 + len(parameter_string)

                        assert code_str[location] == "{",\
                            f"{read_buffer}(_) should be followed by {{, not {code_str[location]}"
                        inner_code_str = self.isolate_delimited_range(code_str[location + 1:], "{", "}")
                        location += 2 + len(inner_code_str)

                        inner = self.parse(inner_code_str)

                        block = block_type(parameter_string, inner=inner)

                        out.append(block)

                    elif issubclass(block_type, ParametrizedInstruction):
                        assert code_str[location] == "(",\
                            f"{read_buffer} should be followed by (, not {code_str[location]}"
                        parameter_string = self.isolate_delimited_range(code_str[location + 1:], "(", ")")
                        location += 2 + len(parameter_string)

                        assert code_str[location] == ";", \
                            f"{read_buffer}({parameter_string}) should be followed by ;, not {code_str[location]}"
                        location += 1

                        block = block_type(parameter_string)

                        out.append(block)

                    elif issubclass(block_type, CompoundInstruction):
                        assert code_str[location] == "{",\
                            f"{read_buffer} should be followed by {{, not {code_str[location]}"
                        inner_code_str = self.isolate_delimited_range(code_str[location + 1:], "{", "}")
                        location += 2 + len(inner_code_str)

                        inner = self.parse(inner_code_str)

                        block = block_type(inner=inner)

                        out.append(block)

                    elif issubclass(block_type, Instruction):
                        block = block_type()
                        out.append(block)
                        location += 1

                else:
                    assert False, f"Unrecognized command: \"{read_buffer}\""

        return out

    def next_instruction(self):
        while self:
            instruction = self.popleft()
            if isinstance(instruction, PrimitiveInstruction):
                return instruction
            elif isinstance(instruction, ResolvableInstruction):
                instruction.resolve(self)

        return PrimitiveInstruction.SLEEP

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

    def copy_code(self, robot):
        return type(self)(robot, custom_definitions=self.custom_definitions, code=self)

    def __str__(self):
        return "\n".join(map(str, self))