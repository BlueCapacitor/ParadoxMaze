from tiles import Drawings
from tiles.abstract.transport import TransportTile


class PortalTile(TransportTile):
    needs_refresh = True

    def __init__(self, x, y, destination_tile):
        super().__init__(x, y)
        self.destination_tile = destination_tile

    def get_destination(self, _state, time, _robot):
        return self.destination_tile.x, self.destination_tile.y, time

    def get_drawing(self, state, time):
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return ((0, 0, 0),
                        self.destination_tile.on_color,
                        (Drawings.TEXT, self.destination_tile.letter.upper(), (0.25, 0.25, 0.25)))
        return ((0, 0, 0),
                self.destination_tile.off_color,
                (Drawings.TEXT, self.destination_tile.letter.upper(), (0.25, 0.25, 0.25)))
