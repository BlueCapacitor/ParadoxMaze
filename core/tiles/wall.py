from core.tiles.empty import EmptyTile


class WallTile(EmptyTile):

    def is_solid(self, _state, _time):
        return True

    def get_drawing(self, _state, _time):
        return (((0.25, 0.25, 0.25),
                 (0, 0, 0)))