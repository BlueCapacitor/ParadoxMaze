from language.resolvable_instructions.compound_instructions import CompoundInstruction


class IfClosed(CompoundInstruction):
    determinate = False

    def resolve(self, code):
        if not code.robot.look_value:
            code.extendleft(self.inner[::-1])

    def get_display_name(self):
        return "ifClosed"
