from language.resolvable_instructions import ResolvableInstruction


class Stop(ResolvableInstruction):
    def resolve(self, code):
        code.clear()

    def __str__(self):
        return "stop"
