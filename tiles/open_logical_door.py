from tiles import Drawings, get_color_for_id
from tiles.abstract.non_static_door import NonStaticDoorTile


class OpenLogicalDoorTile(NonStaticDoorTile):
    needs_refresh = True

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def is_solid(self, state, time):
        return not state.get_control_value(self.control_id, time).current_value

    def get_drawing(self, state, time):
        return ((0.25, 0.5, 0.25),
                (0, 0, 0) if self.is_solid(state, time) else (1, 1, 1),
                (Drawings.REG_POLY, 4, 3 / 8, self.color),
                (Drawings.TEXT, self.control_id, (0, 0, 0)))

    def look(self, state, time):
        if state.board.needs_nondeterministic_controller:
            return state.get_control_value(self.control_id, time), True
        else:
            return state.get_control_value(self.control_id, time).current_value

    def crash_look(self, state, time):
        return self.look(state, time)

    def could_be_fatal(self, state, time):
        control_value = state.get_control_value(self.control_id, time)
        return False in control_value.possible_values
