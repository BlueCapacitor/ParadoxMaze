from abc import ABCMeta
from enum import EnumMeta

from core import TrueSingletonMeta


class AbstractEnumMeta(ABCMeta, EnumMeta):
    pass


# noinspection PyMethodOverriding,PyMethodParameters,PyMethodMayBeStatic,PyPep8Naming
class infinity(int, use_automatic_factory=True, metaclass=TrueSingletonMeta):
    __class__ = int

    def __eq__(*args):
        other = args[-1]
        return other is infinity

    def __lt__(*args):
        return False

    def __le__(*args):
        other = args[-1]
        if other == 0:
            return False
        return other == infinity

    def __gt__(*args):
        other = args[-1]
        if other == 0:
            return True
        return other != infinity

    def __ge__(*args):
        return True

    def __add__(*args):
        return infinity

    def __sub__(*args):
        return infinity

    def __mul__(*args):
        other = args[-1]
        if other == 0:
            raise ValueError("Can not multiply infinity by zero")
        else:
            return infinity

    def __floordiv__(*args):
        other = args[-1]
        if other == infinity:
            raise ValueError("Can not divide infinity by infinity")
        elif other == 0:
            raise ValueError("Can not divide infinity by zero")
        return infinity

    def __truediv__(*args):
        other = args[-1]
        if other == infinity:
            raise ValueError("Can not divide infinity by infinity")
        elif other == 0:
            raise ValueError("Can not divide infinity by zero")
        return infinity

    def __str__(*args):
        return "∞"

    def __repr__(*args):
        return "<infinity>"

    def __bool__(*args):
        return True

