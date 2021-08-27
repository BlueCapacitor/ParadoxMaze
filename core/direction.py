from __future__ import annotations

from enum import Enum
from math import pi


class Direction(Enum):
    RIGHT: Direction = (0, 1, 0, "right")
    UP: Direction = (1, 0, -1, "up")
    LEFT: Direction = (2, -1, 0, "left")
    DOWN: Direction = (3, 0, 1, "down")

    def __new__(cls, val: int, _dx: int, _dy: int, _str_name: str) -> Direction:
        obj = object.__new__(cls)
        obj._value_ = val
        return obj

    def __init__(self, _val: int, dx: int, dy: int, str_name: str) -> None:
        self.dx = dx
        self.dy = dy
        self.str_name = str_name
        self.angle = self.value * pi / 2

    def left(self) -> Direction:
        return Direction((self.value + 1) % 4)

    def right(self) -> Direction:
        return Direction((self.value - 1) % 4)

    def opposite(self) -> Direction:
        return Direction((self.value + 2) % 4)

