from tiles import Drawings
from tiles.empty import EmptyTile
from tools.template import template


class TargetTile(EmptyTile):
    needs_refresh = True

    def get_drawing(self, state, time):
        for check_time in range(state.min_time, time + 1):
            if len(state.robot_log[(template.x, template.y, template.time), (self.x, self.y, check_time)]) > 0:
                return ((0.5, 0.5, 0.5),
                        (0.5, 0.5, 0.5),
                        (Drawings.REG_POLY, 4, 3 / 8, (1, 1, 1)))
        return ((0.5, 0.5, 0.5),
                (0.75, 0.75, 0.75),
                (Drawings.REG_POLY, 4, 3 / 8, (1, 1, 1)))
