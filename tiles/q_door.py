from core import MultiIndex
from tiles import Drawings, get_color_for_id, greek_alphabet
from tiles.abstract.non_static_door import NonStaticDoorTile


class QDoor(NonStaticDoorTile):
    is_time_travel = True

    def __init__(self, x, y, control_id, properties):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)
        self.letter = greek_alphabet[control_id]
        self.properties = properties

        self.inner_colors = MultiIndex(((1, 1, 1), (0.5, 0.5, 1), (1, 0.25, 0), (0.001, 0.001, 0.001)), tuple)[
            self.properties[0][0] * 2 + self.properties[0][1], self.properties[1][0] * 2 + self.properties[1][1]]
        self.outer_colors = MultiIndex(((0.75, 0.75, 0.75), (0.25, 0.25, 1), (1, 0, 0), (0.25, 0.25, 0.25)), tuple)[
            self.properties[0][0] * 2 + self.properties[0][1], self.properties[1][0] * 2 + self.properties[1][1]]

    def get_value(self, state):
        return state.get_q_control_value(self.control_id).current_value

    # def get_drawing(self, state, time):
    #     return ((1, 0, 0.5),
    #             self.inner_colors[not self.is_solid(state, time)],
    #             (Drawings.RECT, 1.25, self.outer_colors[self.is_solid(state, time)]),
    #             (Drawings.RECT, 1, self.inner_colors[not self.is_solid(state, time)]),
    #             (Drawings.CIRCLE, 3 / 8, self.color),
    #             (Drawings.TEXT, self.letter if self.polarity else f"~{self.letter}", (0, 0, 0)))

    def get_drawing(self, state, time):
        return (self.outer_colors[not self.get_value(state)],
                self.inner_colors[not self.get_value(state)],
                (Drawings.CIRCLE, 7 / 16, self.inner_colors[self.get_value(state)]),
                (Drawings.CIRCLE, 3 / 8, self.color),
                (Drawings.CORNERS, 16 / 47, 5 / 47, self.outer_colors[self.get_value(state)]),
                # (Drawings.CORNERS, 16 / 47, 3 / 47, (1, 0.001, 0.5)),
                (Drawings.TEXT, self.letter, (0, 0, 0)))

    def look(self, state, time):
        if self.properties[0][1] != self.properties[1][1]:
            return state.get_q_control_value(self.control_id), self.properties[1][1]
        else:
            return not self.properties[0][1]

    def crash_look(self, state, time):
        if self.properties[0][0] != self.properties[1][0]:
            return state.get_q_control_value(self.control_id), self.properties[1][0]
        else:
            return not self.properties[0][0]

    def could_be_fatal(self, state, time):
        control_value = state.get_q_control_value(self.control_id)
        return any(self.properties[value][0] for value in control_value.possible_values)
