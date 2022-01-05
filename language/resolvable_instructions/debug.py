from language.resolvable_instructions import ResolvableInstruction
from language.resolvable_instructions.control_flow_anchors.continue_anchor import ContinueAnchor


class Debug(ResolvableInstruction):
    def resolve(self, code):
        print("## Debug ##")

    def __str__(self):
        return "debug"
