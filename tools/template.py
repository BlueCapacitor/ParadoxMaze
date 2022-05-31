import operator
from collections import deque
from enum import Enum
from itertools import chain
from math import prod
from typing import Any


class Template:
    class Source(Enum):
        NONE = 1
        GETATTR = 2
        CALL = 3
        GETITEM = 4
        COLLECTION = 5
        SET = 6
        FUNC = 7
        SWITCH = 8
        NOT = 9
        OR = 10
        AND = 11

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source: list[Any] = source if source is not None else [Template.Source.NONE]

    def __getattr__(self, item):
        return self.new_child(Template.Source.GETATTR, item)

    def __call__(self, *args, **kwargs):
        return self.new_child(Template.Source.CALL, args, kwargs)

    def __getitem__(self, item):
        return self.new_child(Template.Source.GETITEM, item)

    @classmethod
    def tuple(cls, *elements):
        return cls(parent=None, source=(Template.Source.COLLECTION, elements))

    @classmethod
    def list(cls, *elements):
        return cls(parent=None, source=(Template.Source.COLLECTION, list(elements)))

    @classmethod
    def set(cls, *elements):
        return cls(parent=None, source=(Template.Source.SET, False, elements))

    @classmethod
    def frozenset(cls, *elements):
        return cls(parent=None, source=(Template.Source.SET, True, elements))

    @classmethod
    def dict(cls, **items):
        return cls(parent=None, source=(Template.Source.COLLECTION, items))

    @classmethod
    def func(cls, func, *args, func_name=None, infix_func=False, reverse_args=False, **kwargs):
        return cls(parent=None, source=(Template.Source.FUNC, func, args if not reverse_args else args[::-1],
                                        kwargs, func_name, infix_func))

    @classmethod
    def switch(cls, guard, *branches, default=None, **named_branches):
        return cls(parent=None, source=(Template.Source.SWITCH, guard, branches, named_branches, default))

    @classmethod
    def switch_dict(cls, guard, branches, default=None):
        return cls(parent=None, source=(Template.Source.SWITCH, guard, [], branches, default))

    @classmethod
    def is_(cls, a, b):
        return Template.func(operator.is_, a, b)

    @classmethod
    def not_(cls, a):
        return cls(parent=None, source=(Template.Source.NOT, a))

    @classmethod
    def or_(cls, a, b):
        return cls(parent=None, source=(Template.Source.OR, a, b))

    @classmethod
    def and_(cls, a, b):
        return cls(parent=None, source=(Template.Source.AND, a, b))

    @classmethod
    def min(cls, *args, **kwargs):
        return Template.func(min, *args, **kwargs)

    @classmethod
    def max(cls, *args, **kwargs):
        return Template.func(max, *args, **kwargs)

    @classmethod
    def sum(cls, iterable, /, start=0):
        return Template.func(sum, iterable, start=start)

    @classmethod
    def prod(cls, iterable, /, start=0):
        return Template.func(prod, iterable, start=start)

    @classmethod
    def any(cls, iterable, /):
        return Template.func(any, iterable)

    @classmethod
    def all(cls, iterable, /):
        return Template.func(all, iterable)

    def new_child(self, *args):
        return type(self)(parent=self, source=args)

    def replicate(self, default=None, **items):
        match self.source[0]:
            case Template.Source.NONE:
                return items.get(self.parent, default)
            case Template.Source.GETATTR:
                return getattr(self.parent.replicate(default, **items), self.source[1])
            case Template.Source.CALL:
                return self.parent.replicate(default, **items)(
                    *Template.replicate_param(self.source[1], default, items),
                    **Template.replicate_param(self.source[2], default, items))
            case Template.Source.GETITEM:
                return self.parent.replicate(default, **items).__getitem__(
                    Template.replicate_param(self.source[1], default, items))
            case Template.Source.COLLECTION:
                return Template.replicate_param(self.source[1], default, items)
            case Template.Source.SET:
                tup = Template.replicate_param(self.source[2], default, items)
                return frozenset(tup) if self.source[1] else set(tup)
            case Template.Source.FUNC:
                return Template.replicate_param(self.source[1], default, items)(
                    *Template.replicate_param(self.source[2], default, items),
                    **Template.replicate_param(self.source[3], default, items))
            case Template.Source.SWITCH:
                key = Template.replicate_param(self.source[1], default, items)
                return Template.replicate_param(self.source[3][key], default, items) if key in self.source[3] \
                    else Template.replicate_param(self.source[2][key], default, items) \
                    if isinstance(key, int) and 0 <= key < len(self.source[2]) \
                    else Template.replicate_param(self.source[4], default, items)
            case Template.Source.NOT:
                return not Template.replicate_param(self.source[1], default, items)
            case Template.Source.OR:
                return Template.replicate_param(self.source[1], default, items) or \
                       Template.replicate_param(self.source[2], default, items)
            case Template.Source.AND:
                return Template.replicate_param(self.source[1], default, items) and \
                       Template.replicate_param(self.source[2], default, items)

    @staticmethod
    def substitute(obj: Any, default=None, **items):
        match obj:
            case Template():
                match obj.parent, obj.source[0]:
                    case str(), Template.Source.NONE if obj.parent in items:
                        return items[obj.parent]
                    case _, Template.Source.NONE if default is not None:
                        return default
                    case _:
                        return Template(Template.substitute(obj.parent, default, **items),
                                        Template.substitute(obj.source, default, **items))
            case list() | tuple() | deque() | set() | frozenset():
                return type(obj)(Template.substitute(element, default, **items) for element in obj)
            case dict():
                return {key: Template.substitute(value, default, **items) for key, value in obj.items()}
            case slice():
                return slice(*Template.substitute((obj.start, obj.stop, obj.step), default, **items))
            case _:
                return obj

    @staticmethod
    def is_equivalent(a: Any, b: Any):
        match a, b:
            case Template(), Template():
                return Template.is_equivalent(a.source, b.source) and Template.is_equivalent(a.parent, b.parent)
            case (list(), list()) | (tuple(), tuple()) | (deque(), deque()):
                return len(a) == len(b) and all(Template.is_equivalent(x, y) for x, y in zip(a, b))
            case (set(), set()) | (frozenset(), frozenset()):
                return all((total := sum(equivalences := tuple(Template.is_equivalent(x, y) for y in b))) and
                           total == sum(Template.is_equivalent(b[equivalences.index(True)], x2) for x2 in x) for x in a)
            case dict(), dict():
                return len(a) == len(b) and all(Template.is_equivalent(x, b[key]) for x, key in a.items())
            case slice(), slice():
                return Template.is_equivalent((a.start, a.stop, a.step), (b.start, b.stop, b.step))
            case _:
                return a == b

    def split_from_any(self, others, recursive=False):
        for index, other in enumerate(others):
            if Template.is_equivalent(self, other):
                return index, Template()

        if recursive and (parent_split := self.parent.split_from_any(others, recursive=recursive)):
            return parent_split[0], Template(parent=parent_split[1], source=self.source)

    @staticmethod
    def replicate_param(param, default, items):
        match param:
            case Template():
                return param.replicate(default, **items)
            case tuple() | list() | set() | frozenset():
                return type(param)(Template.replicate_param(element, default, items) for element in param)
            case dict():
                return {key: Template.replicate_param(val, default, items) for key, val in param.items()}
            case slice():
                return slice(Template.replicate_param(param.start, default, items),
                             Template.replicate_param(param.stop, default, items),
                             Template.replicate_param(param.step, default, items))
            case _:
                return param

    def __str__(self):
        match self.source[0]:
            case Template.Source.NONE:
                return "Template()" if self.parent is None else f"Template({self.parent})"
            case Template.Source.GETATTR:
                return f"{self.parent}.{self.source[1]}"
            case Template.Source.CALL:
                return Template.func_call_str(repr(self.parent), False, *self.source[1:])
            case Template.Source.GETITEM:
                return f"{self.parent}[{self.source[1]}]"
            case Template.Source.COLLECTION:
                return str(self.source[1])
            case Template.Source.SET:
                if self.source[1]:
                    return f"frozenset({{{', '.join(str(element) for element in self.source[2])}}})"
                else:
                    return f"{{{', '.join(str(element) for element in self.source[2])}}}"
            case Template.Source.FUNC:
                return Template.func_call_str(self.source[1].__name__ if self.source[4] is None else self.source[4],
                                              self.source[5], self.source[2], self.source[3])
            case Template.Source.SWITCH:
                match len(self.source[2]), len(self.source[3]):
                    case 0, 0:
                        return repr(self.source[4])
                    case 1, 0:
                        return f"({self.source[4]} if {self.source[1]} else {self.source[2][0]})"
                    case 0, 1:
                        key, value = tuple(self.source[3].items())[0]
                        return f"({key} if {self.source[1]} == {value} else {self.source[4]})"
                    case _:
                        switch_dict = ", ".join(f"{key} -> {value}"
                                                for key, value in chain(enumerate(self.source[2]),
                                                                        self.source[3].items()))
                        return f"(switch {self.source[1]}: {switch_dict}; {self.source[4]})"
            case Template.Source.NOT:
                return f"(not {self.source[1]})"
            case Template.Source.OR:
                return f"({self.source[1]} or {self.source[2]})"
            case Template.Source.AND:
                return f"({self.source[1]} and {self.source[2]})"

    @staticmethod
    def func_call_str(func_name, infix_func, args, kwargs):
        if infix_func:
            return f"{args[0] !r} {func_name} {args[1]}"
        else:
            if len(args) == 0:
                return f"{func_name}({', '.join(f'{key}={value}' for key, value in kwargs.items())})"
            else:
                if len(kwargs) == 0:
                    return f"{func_name}({', '.join(str(arg) for arg in args)})"
                else:
                    return f"{func_name}({', '.join(str(arg) for arg in args)}, " \
                           f"{', '.join(f'{key}={value !r}' for key, value in kwargs.items())})"

    def __repr__(self):
        match self.parent, self.source:
            case None, [Template.Source.NONE]:
                return "Template()"
            case None, _:
                return f"Template({self.source})"
            case str(), [Template.Source.NONE]:
                return f"Template(\"{self.parent}\")"
            case _:
                return f"Template({self.parent}, {self.source !r})"

    @staticmethod
    def template_repr(obj):
        match obj:
            case Template():
                return repr(obj)
            case set(__len__=0):
                return "set()"
            case dict(__len__=0):
                return "dict()"
            case tuple() | list() | deque() | set() | frozenset():
                brackets = Template.get_brackets(obj)
                return f"{brackets[0]}{', '.join(Template.template_repr(element) for element in obj)}{brackets[1]}"
            case dict():
                return f"{{{', '.join(f'{key}: {Template.template_repr(value)}' for key, value in obj.items())}}}"
            case slice():
                return f"slice({Template.template_repr(obj.start)}, " \
                       f"{Template.template_repr(obj.stop)}, " \
                       f"{Template.template_repr(obj.step)})"
            case _:
                return repr(obj)

    @staticmethod
    def template_str(obj):
        match obj:
            case Template():
                return str(obj)
            case set(__len__=0):
                return "set()"
            case dict(__len__=0):
                return "dict()"
            case tuple() | list() | deque() | set() | frozenset():
                brackets = Template.get_brackets(obj)
                return f"{brackets[0]}{', '.join(Template.template_str(element) for element in obj)}{brackets[1]}"
            case dict():
                return f"{{{', '.join(f'{key}: {Template.template_str(value)}' for key, value in obj.items())}}}"
            case slice():
                return f"slice({Template.template_str(obj.start)}, " \
                       f"{Template.template_str(obj.stop)}, " \
                       f"{Template.template_str(obj.step)})"
            case _:
                return repr(obj)

    @staticmethod
    def get_brackets(obj):
        match obj:
            case tuple():
                return "(", ")"
            case list():
                return "[", "]"
            case deque():
                return "deque([", "])"
            case set():
                return "{", "}"
            case frozenset():
                return "frozenset({", "})"
            case _:
                return "", ""

    def _add_(self, *args, **kwargs):
        return self.__getattr__("__add__")(*args, **kwargs)

    def __add__(self, *args, **kwargs):
        return Template.func(operator.add, self, *args, func_name="+", infix_func=True, **kwargs)

    def _sub_(self, *args, **kwargs):
        return self.__getattr__("__sub__")(*args, **kwargs)

    def __sub__(self, *args, **kwargs):
        return Template.func(operator.sub, self, *args, func_name="-", infix_func=True, **kwargs)

    def _mul_(self, *args, **kwargs):
        return self.__getattr__("__mul__")(*args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return Template.func(operator.mul, self, *args, func_name="*", infix_func=True, **kwargs)

    def _truediv_(self, *args, **kwargs):
        return self.__getattr__("__truediv__")(*args, **kwargs)

    def __truediv__(self, *args, **kwargs):
        return Template.func(operator.truediv, self, *args, func_name="/", infix_func=True, **kwargs)

    def _floordiv_(self, *args, **kwargs):
        return self.__getattr__("__floordiv__")(*args, **kwargs)

    def __floordiv__(self, *args, **kwargs):
        return Template.func(operator.floordiv, self, *args, func_name="//", infix_func=True, **kwargs)

    def _mod_(self, *args, **kwargs):
        return self.__getattr__("__mod__")(*args, **kwargs)

    def __mod__(self, *args, **kwargs):
        return Template.func(operator.mod, self, *args, func_name="%", infix_func=True, **kwargs)

    def __divmod__(self, *args, **kwargs):
        return self.__getattr__("__divmod__")(*args, **kwargs)

    def _radd_(self, *args, **kwargs):
        return self.__getattr__("__radd__")(*args, **kwargs)

    def __radd__(self, *args, **kwargs):
        return Template.func(operator.add, self, *args, func_name="+", infix_func=True, reverse_args=True, **kwargs)

    def _rsub_(self, *args, **kwargs):
        return self.__getattr__("__rsub__")(*args, **kwargs)

    def __rsub__(self, *args, **kwargs):
        return Template.func(operator.sub, self, *args, func_name="-", infix_func=True, reverse_args=True, **kwargs)

    def _rmul_(self, *args, **kwargs):
        return self.__getattr__("__rmul__")(*args, **kwargs)

    def __rmul__(self, *args, **kwargs):
        return Template.func(operator.mul, self, *args, func_name="*", infix_func=True, reverse_args=True, **kwargs)

    def _rtruediv_(self, *args, **kwargs):
        return self.__getattr__("__rtruediv__")(*args, **kwargs)

    def __rtruediv__(self, *args, **kwargs):
        return Template.func(operator.truediv, self, *args, func_name="/", infix_func=True, reverse_args=True, **kwargs)

    def _rfloordiv_(self, *args, **kwargs):
        return self.__getattr__("__rfloordiv__")(*args, **kwargs)

    def __rfloordiv__(self, *args, **kwargs):
        return Template.func(operator.floordiv, self, *args, func_name="//", infix_func=True, reverse_args=True,
                             **kwargs)

    def _rmod_(self, *args, **kwargs):
        return self.__getattr__("__rmod__")(*args, **kwargs)

    def __rmod__(self, *args, **kwargs):
        return Template.func(operator.mod, self, *args, func_name="%", infix_func=True, reverse_args=True, **kwargs)

    def __rdivmod__(self, *args, **kwargs):
        return self.__getattr__("__rdivmod__")(*args, **kwargs)

    def _eq_(self, *args, **kwargs):
        return self.__getattr__("__eq__")(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return Template.func(operator.eq, self, *args, func_name="==", infix_func=True, **kwargs)

    def _lt_(self, *args, **kwargs):
        return self.__getattr__("__lt__")(*args, **kwargs)

    def __lt__(self, *args, **kwargs):
        return Template.func(operator.lt, self, *args, func_name="<", infix_func=True, **kwargs)

    def _gt_(self, *args, **kwargs):
        return self.__getattr__("__gt__")(*args, **kwargs)

    def __gt__(self, *args, **kwargs):
        return Template.func(operator.gt, self, *args, func_name=">", infix_func=True, **kwargs)

    def _le_(self, *args, **kwargs):
        return self.__getattr__("__le__")(*args, **kwargs)

    def __le__(self, *args, **kwargs):
        return Template.func(operator.le, self, *args, func_name="<=", infix_func=True, **kwargs)

    def _ge_(self, *args, **kwargs):
        return self.__getattr__("__ge__")(*args, **kwargs)

    def __ge__(self, *args, **kwargs):
        return Template.func(operator.ge, self, *args, func_name=">=", infix_func=True, **kwargs)

    def __neg__(self, *args, **kwargs):
        return self.__getattr__("__neg__")(*args, **kwargs)

    def __abs__(self, *args, **kwargs):
        return self.__getattr__("__abs__")(*args, **kwargs)

    def _and_(self, *args, **kwargs):
        return self.__getattr__("__and__")(*args, **kwargs)

    def __and__(self, *args, **kwargs):
        return Template.func(operator.and_, self, *args, func_name="&", infix_func=True, **kwargs)

    def _or_(self, *args, **kwargs):
        return self.__getattr__("__or__")(*args, **kwargs)

    def __or__(self, *args, **kwargs):
        return Template.func(operator.or_, self, *args, func_name="|", infix_func=True, **kwargs)

    def __invert__(self, *args, **kwargs):
        return Template.func(operator.invert, self, *args, func_name="~", **kwargs)

    def _invert_(self, *args, **kwargs):
        return self.__getattr__("__invert__")(*args, **kwargs)

    def _xor_(self, *args, **kwargs):
        return self.__getattr__("__xor__")(*args, **kwargs)

    def __xor__(self, *args, **kwargs):
        return Template.func(operator.xor, self, *args, func_name="^", infix_func=True, **kwargs)

    def __rand__(self, *args, **kwargs):
        return Template.func(operator.and_, self, *args, func_name="&", infix_func=True, reverse_args=True, **kwargs)

    def __ror__(self, *args, **kwargs):
        return Template.func(operator.or_, self, *args, func_name="|", infix_func=True, reverse_args=True, **kwargs)

    def __rxor__(self, *args, **kwargs):
        return Template.func(operator.xor, self, *args, func_name="^", infix_func=True, reverse_args=True, **kwargs)

    def _rand_(self, *args, **kwargs):
        return self.__getattr__("__rand__")(*args, **kwargs)

    def _ror_(self, *args, **kwargs):
        return self.__getattr__("__ror__")(*args, **kwargs)

    def _rxor_(self, *args, **kwargs):
        return self.__getattr__("__rxor__")(*args, **kwargs)

    def _pow_(self, *args, **kwargs):
        return self.__getattr__("__pow__")(*args, **kwargs)

    def __pow__(self, *args, **kwargs):
        return Template.func(operator.pow, self, *args, func_name="**", infix_func=True, **kwargs)

    def _rpow_(self, *args, **kwargs):
        return self.__getattr__("__rpow__")(*args, **kwargs)

    def __rpow__(self, *args, **kwargs):
        return Template.func(operator.add, self, *args, func_name="**", infix_func=True, reverse_args=True, **kwargs)

    def _ne_(self, *args, **kwargs):
        return self.__getattr__("__ne__")(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return Template.func(operator.ne, self, *args, func_name="!=", infix_func=True, **kwargs)

    def __round__(self, *args, **kwargs):
        return self.__getattr__("__round__")(*args, **kwargs)


template = Template()
