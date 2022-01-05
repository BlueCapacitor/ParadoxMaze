from language.resolvable_instructions import ResolvableInstruction
from language.resolvable_instructions.control_flow_anchors.continue_anchor import ContinueAnchor


class Continue(ResolvableInstruction):
    def resolve(self, code):
        assert ContinueAnchor() in code
        while code.popleft() != ContinueAnchor():
            pass

    def __str__(self):
        return "continue"
