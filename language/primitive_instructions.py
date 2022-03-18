from enum import Enum

from language import AbstractEnumMeta
from language.instruction import Instruction


class PrimitiveInstruction(Instruction, Enum, metaclass=AbstractEnumMeta):
    SLEEP = "slp"
    FORWARD = "fd"
    LEFT = "lt"
    RIGHT = "rt"
    LOOK = "look"

    def __new__(cls, value):
        new = object.__new__(cls)
        new._value_ = value
        return new

    def __init__(self, _value):
        Enum.__init__(self)
        self.breakpoint_enabled = False

    def __str__(self):
        return self.value
