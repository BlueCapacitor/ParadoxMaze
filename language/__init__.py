from abc import ABCMeta
from enum import EnumMeta

from core import TrueSingletonMeta


class AbstractEnumMeta(ABCMeta, EnumMeta):
    pass


# noinspection PyMethodOverriding,PyMethodParameters,PyMethodMayBeStatic,PyPep8Naming
class int_infinity(int, use_automatic_factory=True, metaclass=TrueSingletonMeta):
    __class__ = int

    def __eq__(*args):
        other = args[-1]
        return other is int_infinity

    def __lt__(*args):
        return False

    def __le__(*args):
        other = args[-1]
        if other == 0:
            return False
        return other == int_infinity

    def __gt__(*args):
        other = args[-1]
        if other == 0:
            return True
        return other != int_infinity

    def __ge__(*args):
        return True

    def __add__(*args):
        return int_infinity

    def __sub__(*args):
        return int_infinity

    def __mul__(*args):
        other = args[-1]
        if other == 0:
            raise ValueError("Can not multiply infinity by zero")
        else:
            return int_infinity

    def __floordiv__(*args):
        other = args[-1]
        if other == int_infinity:
            raise ValueError("Can not divide infinity by infinity")
        elif other == 0:
            raise ValueError("Can not divide infinity by zero")
        return int_infinity

    def __truediv__(*args):
        other = args[-1]
        if other == int_infinity:
            raise ValueError("Can not divide infinity by infinity")
        elif other == 0:
            raise ValueError("Can not divide infinity by zero")
        return int_infinity

    def __str__(*args):
        return "∞"

    def __repr__(*args):
        return "<infinity>"

    def __bool__(*args):
        return True
