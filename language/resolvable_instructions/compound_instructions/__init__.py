from abc import ABC, abstractmethod

from language.resolvable_instructions import ResolvableInstruction


class CompoundInstruction(ResolvableInstruction, ABC):
    def __init__(self, inner=()):
        self.inner = inner

    @abstractmethod
    def get_display_name(self): ...

    def __eq__(self, other):
        return super().__eq__(other) and self.inner == other.inner

    def indented_inner_string(self):
        return "\t" + "\n\t".join("\n".join(map(str, self.inner)).splitlines())

    def __str__(self):
        return f"{self.get_display_name()}:\n{self.indented_inner_string() if len(self.inner) != 0 else '[EMPTY]'}"
