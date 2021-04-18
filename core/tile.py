"""
Created on Oct 10, 2020

@author: gosha
"""
from abc import ABC, abstractmethod


def get_color_for_id(n):
    color_shift = 7
    color = [1, 1, 0]
    for _ in range((n * color_shift) % 12):
        color = shift_next_hue(color)
    return color


def shift_next_hue(prev):
    case = sum(prev)

    if case == 1:
        one_index = prev.index(1)
        next_color = [0, 0, 0]
        next_color[one_index] = 1
        next_color[(one_index + 1) % 3] = 0.5

        return next_color

    if case == 1.5:
        one_index = prev.index(1)
        next_color = [0, 0, 0]
        next_color[one_index] = 1
        next_color[(one_index + 1) % 3] = 1 if prev[(one_index + 1) % 3] == 0.5 else 0

        return next_color

    if case == 2:
        zero_index = prev.index(0)
        next_color = [0, 0, 0]
        next_color[(zero_index + 1) % 3] = 0.5
        next_color[(zero_index + 2) % 3] = 1

        return next_color


class EmptyTile(object):
    is_static = True
    is_time_travel = False

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_solid(self, _state, _time):
        return False

    def is_fatal(self, state, time):
        return self.is_solid(state, time)

    def get_colors(self, _state, _time):
        return (((0.75, 0.75, 0.75),
                 (1, 1, 1)))

    def get_text(self, _state, _time):
        return '', (0, 0, 0)

    def could_be_fatal(self, _state, _time):
        return False


class WallTile(EmptyTile):

    def is_solid(self, _state, _time):
        return True

    def get_colors(self, _state, _time):
        return (((0.25, 0.25, 0.25),
                 (0, 0, 0)))


class LavaTile(EmptyTile):

    def is_fatal(self, _state, _time):
        return True

    def get_colors(self, _state, _time):
        return (((1, 0, 0),
                 (1, 0.25, 0)))


class HologramTile(EmptyTile):

    def is_fatal(self, _state, _time):
        return False

    def is_solid(self, _state, _time):
        return True

    def get_colors(self, _state, _time):
        return (((0.5, 0.5, 1),
                 (0.75, 0.75, 1)))


class TargetTile(EmptyTile):

    def get_colors(self, state, time):
        for check_time in range(state.min_time, time + 1):
            for robot_trace in state.get_robots_at_time(check_time):
                if robot_trace.x == self.x and robot_trace.y == self.y:
                    return (((0.5, 0.5, 0.5),
                             (0.5, 0.5, 0.5),
                             (1, 1, 1)))
        return ((0.5, 0.5, 0.5),
                (0.75, 0.75, 0.75),
                (1, 1, 1))


class DestinationTile(EmptyTile):

    def __init__(self, x, y, letter='', color=None):
        super().__init__(x, y)

        self.letter = letter

        if color is None:
            color = get_color_for_id(ord(letter))

        self.on_color = color
        self.off_color = (0.5 + color[0] / 2, 0.5 + color[1] / 2, 0.5 + color[2] / 2)

    def get_colors(self, state, time):
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return (((0.75, 0.75, 0.75),
                         self.on_color))
        return (((0.75, 0.75, 0.75),
                 self.off_color))

    def get_text(self, _state, _time):
        return self.letter, (0.25, 0.25, 0.25)


class TransportTile(EmptyTile, ABC):

    @abstractmethod
    def get_destination(self, _state, _time, _robot):
        pass  # return((new_x, new_y, new_time))


class PortalTile(TransportTile):

    def __init__(self, x, y, destination_tile):
        super().__init__(x, y)
        self.destination_tile = destination_tile

    def get_destination(self, _state, time, _robot):
        return self.destination_tile.x, self.destination_tile.y, time

    def get_colors(self, state, time):
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return (((0, 0, 0),
                         self.destination_tile.on_color))
        return (((0, 0, 0),
                 self.destination_tile.off_color))

    def get_text(self, _state, _time):
        return self.destination_tile.letter.upper(), (0.25, 0.25, 0.25)


class TimeGateTile(TransportTile):
    is_time_travel = True

    def __init__(self, x, y, dt):
        super().__init__(x, y)
        self.dt = dt

    def get_destination(self, _state, time, _robot):
        return self.x, self.y, time + self.dt

    def get_colors(self, _state, _time):
        return (((0.25, 0, 0.75) if self.dt < 0 else (0.75, 0.5, 0) if self.dt > 0 else (0.75, 0.75, 0.75),
                 (0.25, 0.25, 0.25)))

    def get_text(self, _state, _time):
        return str(self.dt) if self.dt < 0 else '+' + str(self.dt), (1, 1, 1)


class CloseTimedDoorTile(EmptyTile):

    def __init__(self, x, y, trigger_time):
        super().__init__(x, y)
        self.trigger_time = trigger_time

    def is_solid(self, _state, time):
        return time >= self.trigger_time

    def get_colors(self, _state, time):
        return (((0.5, 0.25, 0.25),
                 (0, 0, 0) if time >= self.trigger_time else (1, 1, 1)))

    def get_text(self, _state, time):
        return '' if time >= self.trigger_time else str(self.trigger_time - time), (0.25, 0.25, 0.25)


class OpenTimedDoorTile(EmptyTile):

    def __init__(self, x, y, trigger_time):
        super().__init__(x, y)
        self.trigger_time = trigger_time

    def is_solid(self, _state, time):
        return time < self.trigger_time

    def get_colors(self, _state, time):
        return (((0.5, 0.5, 0.25),
                 (0, 0, 0) if time < self.trigger_time else (1, 1, 1)))

    def get_text(self, _state, time):
        return '' if time >= self.trigger_time else str(self.trigger_time - time), (0.75, 0.75, 0.75)


class TimePortalTile(TransportTile):
    is_time_travel = True

    def __init__(self, x, y, dest_t):
        super().__init__(x, y)
        self.dest_t = dest_t

    def get_destination(self, _state, _time, _robot):
        return self.x, self.y, self.dest_t

    def get_colors(self, _state, _time):
        return (((0.0, 0.0, 0.25),
                 (0.25, 0.25, 0.25)))

    def get_text(self, _state, _time):
        return str(self.dest_t), (1, 1, 1)


class ControlTile(EmptyTile, ABC):

    @abstractmethod
    def trigger(self, _state, _time):
        pass


class ButtonTile(ControlTile):

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def trigger(self, state, time):
        control_value = state.get_control_value(self.control_id, time)
        control_value.set_current_value(True, True)

    def get_colors(self, state, time):
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return (((0.5, 0.5, 0.5),
                         (0.5, 0.5, 0.5),
                         self.color))
        return ((0.5, 0.5, 0.5),
                (0.75, 0.75, 0.75),
                self.color)

    def get_text(self, _state, _time):
        return self.control_id, (0, 0, 0)


class OnToggleTile(ControlTile):

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def trigger(self, state, time):
        state.set_sticky_value(self.control_id, time, True)

    def get_colors(self, state, time):
        if state.get_control_value(self.control_id, time).current_value:
            return (((0.5, 0.5, 0.5),
                     (0.5, 0.75, 0.5),
                     self.color))
        return ((0.5, 0.5, 0.5),
                (0.75, 1, 0.75),
                self.color)

    def get_text(self, _state, _time):
        return self.control_id, (0, 0, 0)


class OffToggleTile(ControlTile):

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def trigger(self, state, time):
        state.set_sticky_value(self.control_id, time, False)

    def get_colors(self, state, time):
        if not state.get_control_value(self.control_id, time).current_value:
            return (((0.5, 0.5, 0.5),
                     (0.5, 0.75, 0.5),
                     self.color))
        return ((0.5, 0.5, 0.5),
                (0.75, 1, 0.75),
                self.color)

    def get_text(self, _state, _time):
        return self.control_id, (0, 0, 0)


class NonStaticDoorTile(EmptyTile, ABC):
    is_static = False

    @abstractmethod
    def look(self, _state, _time):
        pass  # return(control_value, looks_open_on_value)

    @abstractmethod
    def crash_look(self, _state, _time):
        pass  # return(control_value, open_on_value)


class OpenLogicalDoorTile(NonStaticDoorTile):

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def is_solid(self, state, time):
        return not state.get_control_value(self.control_id, time).current_value

    def get_colors(self, state, time):
        return (((0.25, 0.5, 0.25),
                 (0, 0, 0) if self.is_solid(state, time) else (1, 1, 1),
                 self.color))

    def get_text(self, _state, _time):
        return self.control_id, (0, 0, 0)

    def look(self, state, time):
        if state.board.has_time_travel:
            return state.get_control_value(self.control_id, time), True
        else:
            return state.get_control_value(self.control_id, time).current_value

    def crash_look(self, state, time):
        return self.look(state, time)

    def could_be_fatal(self, state, time):
        control_value = state.get_control_value(self.control_id, time)
        return False in control_value.possible_values


class CloseLogicalDoorTile(NonStaticDoorTile):

    def __init__(self, x, y, control_id):
        super().__init__(x, y)
        self.control_id = control_id

        self.color = get_color_for_id(control_id)

    def is_solid(self, state, time):
        return state.get_control_value(self.control_id, time).current_value

    def get_colors(self, state, time):
        return (((0.5, 0.25, 0.25),
                 (0, 0, 0) if self.is_solid(state, time) else (1, 1, 1),
                 self.color))

    def get_text(self, _state, _time):
        return self.control_id, (0, 0, 0)

    def look(self, state, time):
        if state.board.has_time_travel:
            return state.get_control_value(self.control_id, time), False
        else:
            return not state.get_control_value(self.control_id, time).current_value

    def crash_look(self, state, time):
        return self.look(state, time)

    def could_be_fatal(self, state, time):
        control_value = state.get_control_value(self.control_id, time)
        return False in control_value.possible_values
