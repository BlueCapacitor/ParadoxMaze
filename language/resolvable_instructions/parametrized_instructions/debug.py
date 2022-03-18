from language.resolvable_instructions.parametrized_instructions import ParametrizedInstruction


class Debug(ParametrizedInstruction):
    def get_display_name(self):
        return "debug"

    def resolve(self, code):
        bp = self.parameter.endswith(" (*)")
        if bp:
            self.parameter = self.parameter[:-4]

        if " $ " in self.parameter:
            eval_segment = " $ ".join(self.parameter.split(" $ ")[1:])
            print(f"Debug({self.parameter}) -> {eval(eval_segment)}" + " (*)" * bp)
        else:
            print(f"Debug({self.parameter})" + " (*)" * bp)

        if bp:
            breakpoint()
