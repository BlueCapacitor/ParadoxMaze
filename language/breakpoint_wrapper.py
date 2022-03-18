from language.instruction import Instruction


class BreakpointWrapper(Instruction):
    def __init__(self, wrapped):
        super().__init__()
        self.wrapped = wrapped

    def __str__(self):
        return f"breakpoint -> {self.wrapped}"
