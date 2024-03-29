from language import int_infinity
from language.resolvable_instructions.compound_instructions import CompoundInstruction
from language.resolvable_instructions.control_flow_anchors.break_anchor import BreakAnchor
from language.resolvable_instructions.compound_instructions.loop_generator import LoopGenerator


class Forever(CompoundInstruction):
    def resolve(self, code):
        code.appendleft(BreakAnchor())
        code.appendleft(LoopGenerator(int_infinity, self.inner))

    def get_display_name(self):
        return "forever"
