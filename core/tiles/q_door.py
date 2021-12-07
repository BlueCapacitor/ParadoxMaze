from core.tiles import Drawings, get_color_for_id, greek_alphabet
from core.tiles.abstract.non_static_door import NonStaticDoorTile


class QDoor(NonStaticDoorTile):
    is_time_travel = True

    def __init__(self, x, y, control_id, polarity):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)
        self.letter = greek_alphabet[control_id]
        self.polarity = polarity

    def is_solid(self, state, _time):
        return self.polarity == state.get_q_control_value(self.control_id).current_value

    def get_drawing(self, state, time):
        return ((1, 0, 0.5),
                (0, 0, 0) if self.is_solid(state, time) else (1, 1, 1),
                (Drawings.CIRCLE, 3 / 8, self.color),
                (Drawings.TEXT, self.letter if self.polarity else f"~{self.letter}", (0, 0, 0)))

    def look(self, state, time):
        return state.get_q_control_value(self.control_id), not self.polarity

    def crash_look(self, state, time):
        return self.look(state, time)

    def could_be_fatal(self, state, time):
        control_value = state.get_q_control_value(self.control_id)
        return self.polarity in control_value.possible_values
