from language.resolvable_instructions.compound_instructions import CompoundInstruction


class IfOpen(CompoundInstruction):
    def resolve(self, code):
        if code.robot.look_value:
            code.extendleft(self.inner[::-1])

    def get_display_name(self):
        return "ifOpen"
