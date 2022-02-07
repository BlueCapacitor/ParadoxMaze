from abc import ABC, abstractmethod

from language.instruction import Instruction


class ResolvableInstruction(Instruction, ABC):
    determinate = True

    @abstractmethod
    def resolve(self, code): ...

    def __eq__(self, other):
        return type(self) == type(other)
