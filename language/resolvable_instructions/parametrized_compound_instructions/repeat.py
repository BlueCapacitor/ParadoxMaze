from language.resolvable_instructions.control_flow_anchors.break_anchor import BreakAnchor
from language.resolvable_instructions.compound_instructions.loop_generator import LoopGenerator
from language.resolvable_instructions.parametrized_compound_instructions import ParametrizedCompoundInstruction


class Repeat(ParametrizedCompoundInstruction):
    def resolve(self, code):
        code.appendleft(BreakAnchor())
        code.appendleft(LoopGenerator(int(self.parameter), self.inner))

    def get_display_name(self):
        return "repeat"
