class EmptyTile:
    is_static = True
    needs_nondeterministic_controller = False
    needs_refresh = False

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_solid(self, _state, _time):
        return False

    def is_fatal(self, state, time):
        return self.is_solid(state, time)

    def get_drawing(self, _state, _time):
        return (((0.75, 0.75, 0.75),
                 (1, 1, 1)))

    def get_text(self, _state, _time):
        return '', (0, 0, 0)

    def could_be_fatal(self, _state, _time):
        return False
