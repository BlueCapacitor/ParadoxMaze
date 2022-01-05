from enum import Enum

from language import AbstractEnumMeta
from language.instruction import Instruction


class PrimitiveInstruction(Instruction, Enum, metaclass=AbstractEnumMeta):
    SLEEP = "slp"
    FORWARD = "fd"
    LEFT = "lt"
    RIGHT = "rt"
    LOOK = "look"

    def __str__(self):
        return self.value
