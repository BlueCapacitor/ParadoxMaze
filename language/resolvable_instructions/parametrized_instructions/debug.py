from language.resolvable_instructions.parametrized_instructions import ParametrizedInstruction


class Debug(ParametrizedInstruction):
    def get_display_name(self):
        return "debug"

    def resolve(self, code):
        if " $ " in self.parameter:
            eval_segment = self.parameter.split(" $ ")[1:].join(" $ ")
            print(f"Debug({self.parameter}) -> {eval(eval_segment)}")
        else:
            print(f"Debug({self.parameter})")
