from enum import Enum, auto
from functools import cache

greek_alphabet = tuple("αβγδεζηθικλμνξοπρστυφχψω")


class Drawings(Enum):
    RECT = 1
    CIRCLE = 2
    FLARE = 3
    TEXT = 4
    REG_POLY = 5
    CORNERS = 6


@cache
def get_color_for_id(n):
    color_shift = 7
    color = [1, 1, 0]
    for _ in range((n * color_shift) % 12):
        color = shift_next_hue(color)
    return [max(0.001, val) for val in color]


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
