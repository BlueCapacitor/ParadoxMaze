from dataclasses import dataclass, replace
from typing import Any

from direction import Direction


@dataclass
class StaticRobot:
    time: int
    x: int
    y: int
    direction: Direction

    prev_time: int
    prev_x: int
    prev_y: int
    prev_direction: Direction

    charge_remaining: int
    initial_charge: int

    look_value: bool = False

    sleeping: bool = False
    looking: bool = False

    @property
    def forward_x(self) -> int:
        return self.x + self.direction.dx

    @property
    def forward_y(self) -> int:
        return self.y + self.direction.dy

    def copy(self) -> Any:
        return replace(self)


@dataclass
class Robot(StaticRobot):
    def sleep(self) -> None:
        self._step()
        self.sleeping = True
        self.looking = False

    def look(self, state) -> Any:  # TODO return type (and make it cleaner)
        self._step()
        tile = state.board.get_tile(self.forward_x, self.forward_y)
        self.sleeping = False
        self.looking = True
        return tile.look(state, self.time) if not tile.is_static else not (tile.is_solid(state, self.time))

    def turn_left(self) -> None:
        self._step()
        self.direction = self.direction.left()
        self.sleeping = False
        self.looking = False

    def turn_right(self) -> None:
        self._step()
        self.direction = self.direction.right()
        self.sleeping = False
        self.looking = False

    def move_forward(self) -> None:
        self._step()
        self.x, self.y = self.forward_x, self.forward_y
        self.sleeping = False
        self.looking = False

    def _step(self) -> None:
        self.prev_time = self.time
        self.prev_x = self.x
        self.prev_y = self.y
        self.prev_direction = self.direction

        self.charge_remaining -= 1
        self.time += 1

    def crash_look(self, state) -> Any:  # TODO return type (and make it cleaner)
        tile = state.board.get_tile(self.x, self.y)
        return tile.crash_look(state, self.time) if not tile.is_static else not (tile.is_fatal(state, self.time))

    def make_trace(self) -> StaticRobot:
        return super().copy()
