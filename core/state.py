from enum import Enum

from tiles.target import TargetTile
from tools.table import Table
from tools.template import template


class State:
    robot_log_dimensions = [
                template.time,
                template.charge_remaining,
                template.continuity_id,
                (template.time, template.continuity_id),
                (template.x, template.y),
                (template.x, template.y, template.time)
            ]
    robot_log_reduce_dimensions = [
                Table.reduce_max(template.charge_remaining),
                Table.reduce_min(template.charge_remaining),
                Table.reduce_max(template.time),
                Table.reduce_min(template.time)
            ]

    def __init__(self, board, robot_log=None, control_value_log=None, sticky_values=None):
        self.board = board
        if robot_log is None:
            self.robot_log = Table(State.robot_log_dimensions, State.robot_log_reduce_dimensions)
        elif isinstance(robot_log, (list, tuple)):
            self.robot_log = Table(State.robot_log_dimensions, State.robot_log_reduce_dimensions, items=robot_log)
        else:
            self.robot_log = robot_log

        if control_value_log is None:
            self.control_value_log = {}
        else:
            self.control_value_log = dict(
                map(lambda entry: (entry[0], entry[1].copy()), control_value_log.items()))

        if sticky_values is None:
            self.sticky_values = {}
        else:
            self.sticky_values = dict(sticky_values)

    def copy(self):
        return (State(self.board,
                      self.robot_log.copy(),
                      self.control_value_log,
                      dict(self.sticky_values)))

    def log_robot(self, robot):
        self.log_robot_trace(robot.make_trace())

    def log_robot_trace(self, robot_trace):
        self.robot_log.append(robot_trace)

    def get_control_value(self, control_id, time):
        if (control_id, time) not in self.control_value_log.keys():
            current_value = False

            self.control_value_log[(control_id, time)] = ControlValue(self, time, control_id, current_value)

        return self.control_value_log[(control_id, time)]

    def get_q_control_value(self, q_control_id):
        if (q_control_id, "Q") not in self.control_value_log.keys():
            current_value = False

            self.control_value_log[(q_control_id, "Q")] = ControlValue(self, "Q", q_control_id, current_value)

        return self.control_value_log[(q_control_id, "Q")]

    def get_key_for_control_value(self, control_value):
        for key in self.control_value_log.keys():
            if self.control_value_log[key] == control_value:
                return key

    def set_sticky_value(self, control_id, time, value):
        self.sticky_values[(control_id, time)] = value

    @property
    def is_valid(self):
        out = Result.NO_SUCCESS

        for control_id, time in self.control_value_log.keys():
            control_value = self.control_value_log[(control_id, time)]
            out |= control_value.validity

        targets = {tile: False for tile in self.board.get_targets()}

        for time in self.robot_log.keys():
            for robot_trace in self.robot_log[time]:
                tile = self.board.get_tile(robot_trace.x, robot_trace.y)
                if tile.is_fatal(self, time) and tile.is_static:
                    out = self.fail_and_finalize(out)
                    break
                if not tile.is_static:
                    crash_look = tile.crash_look(self, time)
                    if isinstance(crash_look, bool):
                        if not crash_look:
                            out = self.fail_and_finalize(out)
                    else:
                        control_value, safe_value = crash_look
                        if control_value.static and control_value.current_value != safe_value:
                            out = self.fail_and_finalize(out)
                        if len(control_value.possible_values) == 1 and \
                                tuple(control_value.possible_values)[0] != safe_value:
                            out = self.fail_and_finalize(out)

                if not self.board.check_bounds(robot_trace):
                    out = self.fail_and_finalize(out)
                    break
                if isinstance(tile, TargetTile):
                    targets[tile] = True
                    continue

        if out == Result.NO_SUCCESS and all(targets.values()):
            out = Result.POTENTIAL_SUCCESS

        return out

    @staticmethod
    def fail_and_finalize(result):
        result |= Result.FAIL
        if result == Result.RECOVERABLE_PARADOX:
            result = Result.UNRECOVERABLE_PARADOX
        return result

    @property
    def max_time(self):
        return self.robot_log.reduce(Table.reduce_max(template.time))

    @property
    def min_time(self):
        return self.robot_log.reduce(Table.reduce_min(template.time))

    @property
    def max_charge(self):
        return self.robot_log.reduce(Table.reduce_max(template.current_charge))

    @property
    def min_charge(self):
        return self.robot_log.reduce(Table.reduce_min(template.current_charge))


class Result(Enum):
    SUCCESS = (1, 1)
    POTENTIAL_SUCCESS = (2, 1)
    NO_SUCCESS = (3, 4)
    FAIL = (4, 4)
    RECOVERABLE_PARADOX = (5, 6)
    UNRECOVERABLE_PARADOX = (6, 6)

    def __new__(cls, value, finalize_value):
        new = object.__new__(cls)
        new._value_ = value
        new.finalize_value = finalize_value
        return new

    def __or__(self, other):
        return self if self.value > other.value else other

    @staticmethod
    def get(value):
        for result in Result:
            if result.value == value:
                return result

    @property
    def finalized(self):
        return Result.get(self.finalize_value)


class ControlValue:
    def __init__(self, state, time, control_id, current_value, possible_values=None, static=False):
        if possible_values is None:
            possible_values = {True, False}

        self.state = state
        self.time = time
        self.control_id = control_id
        self._current_value = current_value
        self.possible_values = possible_values
        self.static = static

    def set_current_value(self, value, static):
        if not self.static:
            self._current_value = value
            self.static = static

    @property
    def current_value(self):
        value = self._current_value

        if self.time != "Q":
            max_time = None
            for ((control_id, time), sticky_value) in self.state.sticky_values.items():
                if control_id == self.control_id and (max_time is None or time > max_time) and time <= self.time:
                    value = sticky_value
                    max_time = time

        return value

    @property
    def validity(self):
        if not self.state.board.needs_nondeterministic_controller:
            return Result.SUCCESS
        if self.current_value in self.possible_values:
            return Result.SUCCESS
        else:
            if self.static or len(self.possible_values) == 0:
                return Result.UNRECOVERABLE_PARADOX
            else:
                return Result.RECOVERABLE_PARADOX

    def assume_value(self, value):
        self.possible_values &= {value}
        if self.time == "Q":
            self._current_value = value

    def copy(self, state=None, time=None):
        return ControlValue(self.state if state is None else state, self.time if time is None else time,
                            self.control_id, self._current_value, set(self.possible_values), self.static)
