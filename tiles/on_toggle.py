from tiles import Drawings, get_color_for_id
from tiles.abstract.control import ControlTile


class OnToggleTile(ControlTile):
    needs_refresh = True

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def trigger(self, state, time):
        state.set_sticky_value(self.control_id, time, True)

    def get_drawing(self, state, time):
        if state.get_control_value(self.control_id, time).current_value:
            return ((0.5, 0.5, 0.5),
                    (0.5, 0.75, 0.5),
                    (Drawings.REG_POLY, 4, 3 / 8, self.color),
                    (Drawings.TEXT, self.control_id, (0, 0, 0)))
        return ((0.5, 0.5, 0.5),
                (0.75, 1, 0.75),
                (Drawings.REG_POLY, 4, 3 / 8, self.color),
                (Drawings.TEXT, self.control_id, (0, 0, 0)))

    def get_text(self, _state, _time):
        return self.control_id, (0, 0, 0)
