from enum import Enum
from math import pi


class StaticRobot:
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
    def __init__(self, x, y, direction, charge_remaining, initial_charge, code, time=0, continuity_id=0,
                 look_value=False):
        super().__init__(x, y, direction, charge_remaining, initial_charge, continuity_id=continuity_id,
                         look_value=look_value)

        self.code = code
        self.time = time
        self._peak = None

    @property
    def peak(self):
        if self._peak is None:
            peak = self.code.peak()
            self._peak = peak if peak is not None else False

        if self._peak is False:
            return

        return self._peak

    def get_next_instruction(self):
        self._peak = None
        return self.code.get_next_instruction()

    def action(self):
        self.charge_remaining -= 1
        self.time += 1

    def sleep(self):
        self.action()

    def passive_look(self, state):
        tile = state.board.get_tile(self.forward_x, self.forward_y)
        return tile.look(state, self.time) if not tile.is_static else not (tile.is_solid(state, self.time))

    # def look(self, state):
    #     self.action()
    #     return self.passive_look(state)

    def crash_look(self, state):
        tile = state.board.get_tile(self.x, self.y)
        return tile.crash_look(state, self.time) if not tile.is_static else not (tile.is_fatal(state, self.time))

    def turn_left(self):
        self.direction = self.direction.left()
        self.action()

    def turn_right(self):
        self.direction = self.direction.right()
        self.action()

    def move_forward(self):
        self.x, self.y = self.forward_x, self.forward_y
        self.action()

    def discontinue_path(self):
        self.continuity_id += 1

    def copy(self):
        robot = Robot(self.x, self.y, self.direction, self.charge_remaining, self.initial_charge, None,
                      time=self.time, continuity_id=self.continuity_id, look_value=self.look_value)
        robot.code = self.code.copy_code(robot)
        return robot

    def make_trace(self):
        return super().copy()


# noinspection PyArgumentList
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
