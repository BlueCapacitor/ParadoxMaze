from core.tiles.empty import EmptyTile


class HologramTile(EmptyTile):

    def is_fatal(self, _state, _time):
        return False

    def is_solid(self, _state, _time):
        return True

    def get_drawing(self, _state, _time):
        return (((0.5, 0.5, 1),
                 (0.75, 0.75, 1)))
