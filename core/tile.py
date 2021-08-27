from abc import ABC, abstractmethod
from typing import Optional, Union

from core.robot import Robot
from core.state import ControlValue, State
from core.typedef import Color, ControlID, PCoord, Coords, Time


def get_color_for_id(n: int) -> Color:
    color_shift: int = 7
    color: Color = Color([1, 1, 0])
    for _ in range((n * color_shift) % 12):
        color = shift_next_hue(color)
    return Color(color)


def shift_next_hue(prev: Color) -> Color:
    next_color: Color

    match sum(prev):
        case 1:
            one_index: int = prev.index(1)
            next_color = Color([0, 0, 0])
            next_color[one_index] = 1
            next_color[(one_index + 1) % 3] = 0.5
            return next_color

        case 1.5:
            one_index: int = prev.index(1)
            next_color = Color([0, 0, 0])
            next_color[one_index] = 1
            next_color[(one_index + 1) % 3] = 1 if prev[(one_index + 1) % 3] == 0.5 else 0
            return next_color

        case 2:
            zero_index: int = prev.index(0)
            next_color = Color([0, 0, 0])
            next_color[(zero_index + 1) % 3] = 0.5
            next_color[(zero_index + 2) % 3] = 1
            return next_color


class EmptyTile:
    is_static: bool = True
    is_time_travel: bool = False

    def __init__(self, x: PCoord, y: PCoord) -> None:
        self.x: PCoord = x
        self.y: PCoord = y

    def is_solid(self, state: State, time: Time) -> bool:
        return False

    def is_fatal(self, state: State, time: Time) -> bool:
        return self.is_solid(state, time)

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.75, 0.75, 0.75]),
                Color([1.0, 1.0, 1.0])]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return '', Color([0, 0, 0])

    def could_be_fatal(self, state: State, time: Time) -> bool:
        return False


class WallTile(EmptyTile):

    def is_solid(self, state: State, time: Time) -> bool:
        return True

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.25, 0.25, 0.25]),
                Color([0, 0, 0])]


class LavaTile(EmptyTile):

    def is_fatal(self, state: State, time: Time):
        return True

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([1, 0, 0]),
                Color([1, 0.25, 0])]


class HologramTile(EmptyTile):

    def is_fatal(self, state: State, time: Time):
        return False

    def is_solid(self, state: State, time: Time):
        return True

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.5, 0.5, 1]),
                Color([0.75, 0.75, 1])]


class TargetTile(EmptyTile):

    def get_colors(self, state: State, time: Time) -> list[Color]:
        for check_time in range(state.min_time, time + 1):
            for robot_trace in state.get_robots_at_time(check_time):
                if robot_trace.x == self.x and robot_trace.y == self.y:
                    return [Color([0.5, 0.5, 0.5]),
                            Color([0.5, 0.5, 0.5]),
                            Color([1, 1, 1])]
        return [Color([0.5, 0.5, 0.5]),
                Color([0.75, 0.75, 0.75]),
                Color([1, 1, 1])]


class DestinationTile(EmptyTile):

    def __init__(self, x: PCoord, y: PCoord, letter: str = '', color: Optional[Color] = None) -> None:
        super().__init__(x, y)

        self.letter: str = letter

        if color is None:
            color = get_color_for_id(ord(letter))

        self.on_color: Color = color
        self.off_color: Color = Color([0.5 + color[0] / 2, 0.5 + color[1] / 2, 0.5 + color[2] / 2])

    def get_colors(self, state: State, time: Time) -> list[Color]:
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return [Color([0.75, 0.75, 0.75]),
                        self.on_color]
        return [Color([0.75, 0.75, 0.75]),
                self.off_color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return self.letter, Color([0.25, 0.25, 0.25])


class TransportTile(EmptyTile, ABC):

    @abstractmethod
    def get_destination(self, state: State, robot: Robot) -> Coords:
        pass  # return Coords((new_x, new_y, new_time))


class PortalTile(TransportTile):

    def __init__(self, x: PCoord, y: PCoord, destination_tile: DestinationTile) -> None:
        super().__init__(x, y)
        self.destination_tile: DestinationTile = destination_tile

    def get_destination(self, state: State, robot: Robot) -> Coords:
        return Coords((self.destination_tile.x, self.destination_tile.y, robot.time))

    def get_colors(self, state: State, time: Time) -> list[Color]:
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return [Color([0, 0, 0]),
                        self.destination_tile.on_color]
        return [Color([0, 0, 0]),
                self.destination_tile.off_color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return self.destination_tile.letter.upper(), Color([0.25, 0.25, 0.25])


class TimeGateTile(TransportTile):
    is_time_travel = True

    def __init__(self, x: PCoord, y: PCoord, dt: Time) -> None:
        super().__init__(x, y)
        self.dt: Time = dt

    def get_destination(self, state: State, robot: Robot) -> Coords:
        return Coords((self.x, self.y, robot.time + self.dt))

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.25, 0, 0.75]) if self.dt < 0 else
                Color([0.75, 0.5, 0]) if self.dt > 0 else
                Color([0.75, 0.75, 0.75]),
                Color([0.25, 0.25, 0.25])]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.dt) if self.dt < 0 else '+' + str(self.dt), Color([1, 1, 1])


class CloseTimedDoorTile(EmptyTile):

    def __init__(self, x: PCoord, y: PCoord, trigger_time: Time) -> None:
        super().__init__(x, y)
        self.trigger_time: Time = trigger_time

    def is_solid(self, state: State, time: Time):
        return time >= self.trigger_time

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.5, 0.25, 0.25]),
                Color([0, 0, 0]) if time >= self.trigger_time else Color([1, 1, 1])]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return '' if time >= self.trigger_time else str(self.trigger_time - time), Color([0.25, 0.25, 0.25])


class OpenTimedDoorTile(EmptyTile):

    def __init__(self, x: PCoord, y: PCoord, trigger_time: Time) -> None:
        super().__init__(x, y)
        self.trigger_time: Time = trigger_time

    def is_solid(self, state: State, time: Time):
        return time < self.trigger_time

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.5, 0.5, 0.25]),
                Color([0, 0, 0]) if time < self.trigger_time else Color([1, 1, 1])]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return '' if time >= self.trigger_time else str(self.trigger_time - time), Color([0.75, 0.75, 0.75])


class TimePortalTile(TransportTile):
    is_time_travel: bool = True

    def __init__(self, x: PCoord, y: PCoord, dest_t: Time) -> None:
        super().__init__(x, y)
        self.dest_t: Time = dest_t

    def get_destination(self, state: State, robot: Robot) -> Coords:
        return Coords((self.x, self.y, self.dest_t))

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.0, 0.0, 0.25]),
                Color([0.25, 0.25, 0.25])]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.dest_t), Color([1, 1, 1])


class ControlTile(EmptyTile, ABC):

    @abstractmethod
    def trigger(self, state: State, time: Time) -> None:
        pass


class ButtonTile(ControlTile):

    def __init__(self, x: PCoord, y: PCoord, control_id: ControlID) -> None:
        super().__init__(x, y)
        self.control_id: ControlID = control_id

        self.color: Color = get_color_for_id(control_id)

    def trigger(self, state: State, time: Time) -> None:
        control_value: ControlValue = state.get_control_value(self.control_id, time)
        control_value.set_current_value(True, True)

    def get_colors(self, state: State, time: Time) -> list[Color]:
        for robot_trace in state.get_robots_at_time(time):
            if robot_trace.x == self.x and robot_trace.y == self.y:
                return [Color([0.5, 0.5, 0.5]),
                        Color([0.5, 0.5, 0.5]),
                        self.color]
        return [Color([0.5, 0.5, 0.5]),
                Color([0.75, 0.75, 0.75]),
                self.color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.control_id), Color([0, 0, 0])


class OnToggleTile(ControlTile):

    def __init__(self, x: PCoord, y: PCoord, control_id: ControlID) -> None:
        super().__init__(x, y)
        self.control_id: ControlID = control_id

        self.color: Color = get_color_for_id(control_id)

    def trigger(self, state: State, time: Time) -> None:
        state.set_sticky_value(self.control_id, time, True)

    def get_colors(self, state: State, time: Time) -> list[Color]:
        if state.get_control_value(self.control_id, time).current_value:
            return [Color([0.5, 0.5, 0.5]),
                    Color([0.5, 0.75, 0.5]),
                    self.color]
        return [Color([0.5, 0.5, 0.5]),
                Color([0.75, 1, 0.75]),
                self.color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.control_id), Color([0, 0, 0])


class OffToggleTile(ControlTile):

    def __init__(self, x: PCoord, y: PCoord, control_id: ControlID) -> None:
        super().__init__(x, y)
        self.control_id: ControlID = control_id

        self.color: Color = get_color_for_id(control_id)

    def trigger(self, state: State, time: Time) -> None:
        state.set_sticky_value(self.control_id, time, False)

    def get_colors(self, state: State, time: Time) -> list[Color]:
        if not state.get_control_value(self.control_id, time).current_value:
            return [Color([0.5, 0.5, 0.5]),
                    Color([0.5, 0.75, 0.5]),
                    self.color]
        return [Color([0.5, 0.5, 0.5]),
                Color([0.75, 1, 0.75]),
                self.color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.control_id), Color([0, 0, 0])


class NonStaticDoorTile(EmptyTile, ABC):
    is_static = False

    @abstractmethod
    def look(self, state: State, time: Time) -> Union[bool, tuple[ControlValue, bool]]:
        pass  # return control_value, looks_open_on_value

    @abstractmethod
    def crash_look(self, state: State, time: Time) -> Union[bool, tuple[ControlValue, bool]]:
        pass  # return control_value, open_on_value


class OpenLogicalDoorTile(NonStaticDoorTile):

    def __init__(self, x: PCoord, y: PCoord, control_id: ControlID) -> None:
        super().__init__(x, y)
        self.control_id: ControlID = control_id

        self.color: Color = get_color_for_id(control_id)

    def is_solid(self, state: State, time: Time):
        return not state.get_control_value(self.control_id, time).current_value

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.25, 0.5, 0.25]),
                Color([0, 0, 0]) if self.is_solid(state, time) else Color([1, 1, 1]),
                self.color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.control_id), Color([0, 0, 0])

    def look(self, state: State, time: Time) -> Union[bool, tuple[ControlValue, bool]]:
        if state.board.has_time_travel:
            return state.get_control_value(self.control_id, time), True
        else:
            return state.get_control_value(self.control_id, time).current_value

    def crash_look(self, state: State, time: Time) -> Union[bool, tuple[ControlValue, bool]]:
        return self.look(state, time)

    def could_be_fatal(self, state: State, time: Time) -> bool:
        control_value = state.get_control_value(self.control_id, time)
        return False in control_value.possible_values


class CloseLogicalDoorTile(NonStaticDoorTile):

    def __init__(self, x: PCoord, y: PCoord, control_id: ControlID) -> None:
        super().__init__(x, y)
        self.control_id: ControlID = control_id

        self.color: Color = get_color_for_id(control_id)

    def is_solid(self, state: State, time: Time):
        return state.get_control_value(self.control_id, time).current_value

    def get_colors(self, state: State, time: Time) -> list[Color]:
        return [Color([0.5, 0.25, 0.25]),
                Color([0, 0, 0]) if self.is_solid(state, time) else Color([1, 1, 1]),
                self.color]

    def get_text(self, state: State, time: Time) -> tuple[str, Color]:
        return str(self.control_id), Color([0, 0, 0])

    def look(self, state: State, time: Time) -> Union[bool, tuple[ControlValue, bool]]:
        if state.board.has_time_travel:
            return state.get_control_value(self.control_id, time), False
        else:
            return not state.get_control_value(self.control_id, time).current_value

    def crash_look(self, state: State, time: Time) -> Union[bool, tuple[ControlValue, bool]]:
        return self.look(state, time)

    def could_be_fatal(self, state: State, time: Time) -> bool:
        control_value = state.get_control_value(self.control_id, time)
        return False in control_value.possible_values
