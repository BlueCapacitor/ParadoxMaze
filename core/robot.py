from enum import Enum
from math import pi


class DiscontinuityType(Enum):
    NONE = 0
    SIBLING = 1
    CHILD = 2
    ROOT = 3


class ContinuityID(tuple):
    next_root_id = 0

    def __new__(cls, parent=None):
        if parent is None:
            ContinuityID.next_root_id += 1
            return tuple.__new__(cls, (ContinuityID.next_root_id - 1,))

        else:
            parent.next_child_id += 1
            return tuple.__new__(cls, parent + (parent.next_child_id - 1,))

    def __init__(self, parent=None):
        self.parent = parent
        self.next_child_id = 0

    def create_child(self):
        return ContinuityID(parent=self)

    def create_sibling(self):
        return ContinuityID(parent=self.parent)


class StaticRobot:
    def __init__(self, x, y, direction, charge_remaining, initial_charge, time=0, continuity_id=None, look_value=False):
        self.x = x
        self.y = y
        self.time = time
        self.charge_remaining = charge_remaining
        self.initial_charge = initial_charge
        self.direction = direction
        self.look_value = look_value
        if continuity_id is None:
            self.continuity_id = ContinuityID()
        else:
            self.continuity_id = continuity_id

    @property
    def forward_x(self):
        return self.x + self.direction.dx

    @property
    def forward_y(self):
        return self.y + self.direction.dy

    def copy(self, discontinuity_type=DiscontinuityType.NONE):
        return StaticRobot(self.x, self.y, self.direction, self.charge_remaining, self.initial_charge,
                           continuity_id=self.continuity_id, time=self.time, look_value=self.look_value)

    def static_crash_look(self, state):
        tile = state.board.get_tile(self.x, self.y)
        if tile.is_static:
            return not tile.is_fatal(state, self.time)
        else:
            match tile.crash_look(state, self.time):
                case control_value, safe_value:
                    return control_value.current_value == safe_value
                case value:
                    return value

    def __str__(self):
        return "<RobotTrace: (%s, %s) facing %s, charge: %s>" % (
            self.x, self.y, self.direction.str_name, self.charge_remaining)

    def __repr__(self):
        return str(self)


class Robot(StaticRobot):
    def __init__(self, x, y, direction, charge_remaining, initial_charge, code, time=0, continuity_id=None,
                 look_value=False, skip_step=False):
        super().__init__(x, y, direction, charge_remaining, initial_charge, look_value=look_value,
                         time=time, continuity_id=continuity_id)

        self.code = code
        self.skip_step = skip_step
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
        return tile.look(state, self.time) if not tile.is_static else not tile.is_solid(state, self.time)

    def crash_look(self, state):
        tile = state.board.get_tile(self.x, self.y)
        return tile.crash_look(state, self.time) if not tile.is_static else not tile.is_fatal(state, self.time)

    def turn_left(self):
        self.direction = self.direction.left()
        self.action()

    def turn_right(self):
        self.direction = self.direction.right()
        self.action()

    def move_forward(self):
        self.x, self.y = self.forward_x, self.forward_y
        self.action()

    def copy(self, discontinuity_type=DiscontinuityType.NONE):
        match discontinuity_type:
            case DiscontinuityType.CHILD:
                continuity_id = self.continuity_id.create_child()
            case DiscontinuityType.SIBLING:
                continuity_id = self.continuity_id.create_sibling()
            case DiscontinuityType.ROOT:
                continuity_id = ContinuityID()
            case _:
                continuity_id = self.continuity_id

        robot = Robot(self.x, self.y, self.direction, self.charge_remaining, self.initial_charge, None,
                      time=self.time, continuity_id=continuity_id, look_value=self.look_value, skip_step=self.skip_step)
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
