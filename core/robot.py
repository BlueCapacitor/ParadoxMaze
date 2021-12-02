from enum import Enum
from math import pi


class StaticRobot(object):

    def __init__(self, x, y, direction, charge_remaining, initial_charge, continuity_id=0, look_value=False):
        self.x = x
        self.y = y
        self.charge_remaining = charge_remaining
        self.initial_charge = initial_charge
        self.direction = direction
        self.continuity_id = continuity_id
        self.look_value = look_value

    @property
    def forward_x(self):
        return self.x + self.direction.dx

    @property
    def forward_y(self):
        return self.y + self.direction.dy

    def copy(self):
        return StaticRobot(self.x, self.y, self.direction, self.charge_remaining, self.initial_charge,
                           continuity_id=self.continuity_id, look_value=self.look_value)

    def __str__(self):
        return "<RobotTrace: (%s, %s) facing %s, charge: %s>" % (
            self.x, self.y, self.direction.str_name, self.charge_remaining)

    def __repr__(self):
        return str(self)


class Robot(StaticRobot):

    def __init__(self, x, y, direction, charge_remaining, initial_charge, continuity_id=0, look_value=False):
        super().__init__(x, y, direction, charge_remaining, initial_charge, continuity_id=continuity_id,
                         look_value=look_value)

    def sleep(self):
        self.charge_remaining -= 1

    def look(self, state, time):
        self.charge_remaining -= 1
        tile = state.board.get_tile(self.forward_x, self.forward_y)
        return tile.look(state, time) if not tile.is_static else not (tile.is_solid(state, time))

    def crash_look(self, state, time):
        tile = state.board.get_tile(self.x, self.y)
        return tile.crash_look(state, time) if not tile.is_static else not (tile.is_fatal(state, time))

    def turn_left(self):
        self.direction = self.direction.left()
        self.charge_remaining -= 1

    def turn_right(self):
        self.direction = self.direction.right()
        self.charge_remaining -= 1

    def move_forward(self):
        self.x, self.y = self.forward_x, self.forward_y
        self.charge_remaining -= 1

    def discontinue_path(self):
        self.continuity_id += 1

    def copy(self):
        return Robot(self.x, self.y, self.direction, self.charge_remaining, self.initial_charge,
                     continuity_id=self.continuity_id, look_value=self.look_value)

    def make_trace(self):
        return super().copy()


class Direction(Enum):
    RIGHT = (0, 1, 0, "right")
    UP = (1, 0, -1, "up")
    LEFT = (2, -1, 0, "left")
    DOWN = (3, 0, 1, "down")

    def __new__(cls, val, _dx, _dy, _str_name):
        obj = object.__new__(cls)
        obj._value_ = val
        return obj

    def __init__(self, _val, dx, dy, str_name):
        self.dx = dx
        self.dy = dy
        self.str_name = str_name
        self.angle = self.value * pi / 2

    def left(self):
        return Direction((self.value + 1) % 4)

    def right(self):
        return Direction((self.value - 1) % 4)

    def opposite(self):
        return Direction((self.value + 2) % 4)
