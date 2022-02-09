from tiles import Drawings
from tiles.abstract.transport import TransportTile


class TimeGateTile(TransportTile):
    is_time_travel = True

    def __init__(self, x, y, dt):
        super().__init__(x, y)
        self.dt = dt

    def get_destinations(self, _state, robot):
        return (self.x, self.y, robot.time + self.dt),

    def get_drawing(self, _state, _time):
        return ((0.25, 0, 0.75) if self.dt < 0 else (0.75, 0.5, 0) if self.dt > 0 else (0.75, 0.75, 0.75),
                (0.25, 0.25, 0.25),
                (Drawings.TEXT, str(self.dt) if self.dt < 0 else '+' + str(self.dt), (1, 1, 1)))

