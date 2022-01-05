from language.resolvable_instructions.parametrized_instructions import ParametrizedInstruction


class Function(ParametrizedInstruction):
    def resolve(self, code):
        assert self.parameter in code.custom_definitions, f"Undefined function: {self.parameter}"
        code.extendleft(code.custom_definitions[self.parameter][::-1])

    def get_display_name(self):
        return "function"
