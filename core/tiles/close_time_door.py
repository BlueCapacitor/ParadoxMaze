from core.tiles import Drawings
from core.tiles.empty import EmptyTile


class CloseTimedDoorTile(EmptyTile):

    def __init__(self, x, y, trigger_time):
        super().__init__(x, y)
        self.trigger_time = trigger_time

    def is_solid(self, _state, time):
        return time >= self.trigger_time

    def get_drawing(self, _state, time):
        if time < self.trigger_time:
            return ((0.5, 0.25, 0.25),
                    (1, 1, 1),
                    (Drawings.TEXT, str(self.trigger_time - time), (0.25, 0.25, 0.25)))
        else:
            return ((0.5, 0.25, 0.25),
                    (0, 0, 0),
                    (Drawings.TEXT, str(self.trigger_time - time), (0.75, 0.75, 0.75)))
