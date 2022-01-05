from tiles import Drawings
from tiles.abstract.transport import TransportTile


class TimePortalTile(TransportTile):
    is_time_travel = True

    def __init__(self, x, y, dest_t):
        super().__init__(x, y)
        self.dest_t = dest_t

    def get_destination(self, _state, time, _robot):
        return self.x, self.y, self.dest_t

    def get_drawing(self, _state, _time):
        return ((0.0, 0.5, 0.25),
                (0.25, 0.25, 0.25),
                (Drawings.TEXT, str(self.dest_t), (1, 1, 1)))
