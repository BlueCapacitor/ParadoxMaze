from core.tiles.empty import EmptyTile


class LavaTile(EmptyTile):

    def is_fatal(self, _state, _time):
        return True

    def get_drawing(self, _state, _time):
        return (((1, 0, 0),
                 (1, 0.25, 0)))
