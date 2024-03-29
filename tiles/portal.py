from tiles import Drawings, get_color_for_id
from tiles.abstract.transport import TransportTile
from tiles.destination import DestinationTile


class PortalTile(TransportTile):
    needs_refresh = True

    def __init__(self, x, y, letter):
        super().__init__(x, y)
        self.letter = letter

        color = get_color_for_id(ord(letter.lower()))
        self.on_color = color
        self.off_color = (0.5 + color[0] / 2, 0.5 + color[1] / 2, 0.5 + color[2] / 2)

    def get_destinations(self, state, robot):
        return ((destination_tile.x, destination_tile.y, robot.time) for destination_tile in state.board.list_tiles
                if isinstance(destination_tile, DestinationTile) and destination_tile.letter == self.letter.lower())

    def get_drawing(self, state, time):
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return ((0, 0, 0),
                        self.on_color,
                        (Drawings.TEXT, self.letter, (0.25, 0.25, 0.25)))
        return ((0, 0, 0),
                self.off_color,
                (Drawings.TEXT, self.letter, (0.25, 0.25, 0.25)))
