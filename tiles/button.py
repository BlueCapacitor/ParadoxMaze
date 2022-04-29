from tiles import Drawings, get_color_for_id
from tiles.abstract.control import ControlTile
from tools.template import template


class ButtonTile(ControlTile):
    needs_refresh = True

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def trigger(self, state, time):
        control_value = state.get_control_value(self.control_id, time)
        control_value.set_current_value(True, True)

    def get_drawing(self, state, time):
        if len(state.robot_log[(template.x, template.y, template.time), (self.x, self.y, time)]) > 0:
            return ((0.5, 0.5, 0.5),
                    (0.5, 0.5, 0.5),
                    (Drawings.REG_POLY, 4, 3 / 8, self.color),
                    (Drawings.TEXT, self.control_id, (0, 0, 0)))
        else:
            return ((0.5, 0.5, 0.5),
                    (0.75, 0.75, 0.75),
                    (Drawings.REG_POLY, 4, 3 / 8, self.color),
                    (Drawings.TEXT, self.control_id, (0, 0, 0)))
