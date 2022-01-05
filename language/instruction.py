from abc import ABC, abstractmethod


class Instruction(ABC):
    @abstractmethod
    def __str__(self): ...

    def copy(self):
        return self
