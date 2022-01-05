from language.resolvable_instructions.parametrized_compound_instructions import ParametrizedCompoundInstruction


class CustomDefinition(ParametrizedCompoundInstruction):
    def resolve(self, code):
        code.custom_definitions[self.parameter] = self.inner

    def get_display_name(self):
        return "definition"
