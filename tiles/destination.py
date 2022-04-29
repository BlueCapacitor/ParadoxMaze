from tiles import Drawings, get_color_for_id
from tiles.empty import EmptyTile
from tools.template import template


class DestinationTile(EmptyTile):
    needs_refresh = True

    def __init__(self, x, y, letter='', color=None):
        super().__init__(x, y)

        self.letter = letter

        if color is None:
            color = get_color_for_id(ord(letter))

        self.on_color = color
        self.off_color = (0.5 + color[0] / 2, 0.5 + color[1] / 2, 0.5 + color[2] / 2)

    def get_drawing(self, state, time):
        if len(state.robot_log[(template.x, template.y, template.time), (self.x, self.y, time)]) > 0:
            return ((0.75, 0.75, 0.75),
                    self.on_color,
                    (Drawings.TEXT, self.letter, (0.25, 0.25, 0.25)))
        else:
            return ((0.75, 0.75, 0.75),
                    self.off_color,
                    (Drawings.TEXT, self.letter, (0.25, 0.25, 0.25)))
