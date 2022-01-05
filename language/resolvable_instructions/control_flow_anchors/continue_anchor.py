from language.resolvable_instructions import ResolvableInstruction


class ContinueAnchor(ResolvableInstruction):
    def resolve(self, code):
        pass

    def __str__(self):
        return "<<continue anchor>>"
