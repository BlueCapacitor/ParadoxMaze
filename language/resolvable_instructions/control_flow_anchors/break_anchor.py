from language.resolvable_instructions import ResolvableInstruction


class BreakAnchor(ResolvableInstruction):
    def resolve(self, code):
        pass

    def __str__(self):
        return "<<break anchor>>"
