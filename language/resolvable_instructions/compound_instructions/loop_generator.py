from language.resolvable_instructions.compound_instructions import CompoundInstruction
from language.resolvable_instructions.control_flow_anchors.continue_anchor import ContinueAnchor


class LoopGenerator(CompoundInstruction):
    def __init__(self, num, inner=()):
        super().__init__(inner=inner)
        self.num = num

    def resolve(self, code):
        if self.num > 0:
            code.appendleft(self)
            code.appendleft(ContinueAnchor())
            code.extendleft(self.inner[::-1])
            self.num -= 1

    def get_display_name(self):
        return f"loop generator [{self.num}]"

    def copy(self):
        return LoopGenerator(self.num, inner=self.inner)
