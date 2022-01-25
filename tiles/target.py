from tiles import Drawings
from tiles.empty import EmptyTile


class TargetTile(EmptyTile):
    needs_refresh = True

    def get_drawing(self, state, time):
        for check_time in range(state.min_time, time + 1):
            for robot_trace in state.get_robots_at_time(check_time):
                if robot_trace.x == self.x and robot_trace.y == self.y:
                    return ((0.5, 0.5, 0.5),
                            (0.5, 0.5, 0.5),
                            (Drawings.REG_POLY, 4, 3 / 8, (1, 1, 1)))
        return ((0.5, 0.5, 0.5),
                (0.75, 0.75, 0.75),
                (Drawings.REG_POLY, 4, 3 / 8, (1, 1, 1)))
