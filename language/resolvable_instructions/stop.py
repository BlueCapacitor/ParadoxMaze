from language.resolvable_instructions import ResolvableInstruction
from language.resolvable_instructions.control_flow_anchors.break_anchor import BreakAnchor


class Stop(ResolvableInstruction):
    def resolve(self, code):
        code.clear()

    def __str__(self):
        return "stop"
