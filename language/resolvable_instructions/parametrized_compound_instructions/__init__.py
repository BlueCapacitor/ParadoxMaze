from abc import ABC

from language.resolvable_instructions.compound_instructions import CompoundInstruction
from language.resolvable_instructions.parametrized_instructions import ParametrizedInstruction


class ParametrizedCompoundInstruction(CompoundInstruction, ParametrizedInstruction, ABC):
    def __init__(self, parameter, inner=()):
        ParametrizedInstruction.__init__(self, parameter)
        CompoundInstruction.__init__(self, inner)

    def __eq__(self, other):
        return ParametrizedInstruction.__eq__(self, other) and CompoundInstruction.__eq__(self, other)

    def __str__(self):
        return f"{self.get_display_name()}({self.parameter}):" \
               f"\n{self.indented_inner_string() if len(self.inner) != 0 else '[EMPTY]'} "
