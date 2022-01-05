from abc import ABC, abstractmethod

from language.resolvable_instructions import ResolvableInstruction


class ParametrizedInstruction(ResolvableInstruction, ABC):
    def __init__(self, parameter):
        super().__init__()
        self.parameter = parameter

    @abstractmethod
    def get_display_name(self): ...

    def __eq__(self, other):
        return super().__eq__(other) and self.parameter == other.parameter

    def __str__(self):
        return f"{self.get_display_name()}({self.parameter})"
