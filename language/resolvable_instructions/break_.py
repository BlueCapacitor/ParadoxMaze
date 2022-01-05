from language.resolvable_instructions import ResolvableInstruction
from language.resolvable_instructions.control_flow_anchors.break_anchor import BreakAnchor


class Break(ResolvableInstruction):
    def resolve(self, code):
        assert BreakAnchor() in code
        while code.popleft() != BreakAnchor():
            pass

    def __str__(self):
        return "break"
