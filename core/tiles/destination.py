from core.tiles import Drawings, get_color_for_id
from core.tiles.empty import EmptyTile


class DestinationTile(EmptyTile):

    def __init__(self, x, y, letter='', color=None):
        super().__init__(x, y)

        self.letter = letter

        if color is None:
            color = get_color_for_id(ord(letter))

        self.on_color = color
        self.off_color = (0.5 + color[0] / 2, 0.5 + color[1] / 2, 0.5 + color[2] / 2)

    def get_drawing(self, state, time):
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return ((0.75, 0.75, 0.75),
                        self.on_color,
                        (Drawings.TEXT, self.letter, (0.25, 0.25, 0.25)))
        return ((0.75, 0.75, 0.75),
                self.off_color,
                (Drawings.TEXT, self.letter, (0.25, 0.25, 0.25)))
