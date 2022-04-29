from enum import Enum
from typing import Any


class Template:
    class Source(Enum):
        NONE = 1
        GETATTR = 2
        CALL = 3
        GETITEM = 4

    def __init__(self, parent=None, source=None):
        self.parent = parent
        self.source: list[Any] = source if source is not None else [Template.Source.NONE]

    def __getattr__(self, item):
        return self.new_child(Template.Source.GETATTR, item)

    def __call__(self, *args, **kwargs):
        return self.new_child(Template.Source.CALL, args, kwargs)

    def __getitem__(self, item):
        return self.new_child(Template.Source.GETITEM, item)

    def new_child(self, *args):
        return type(self)(parent=self, source=args)

    def replicate(self, item):
        match self.source[0]:
            case Template.Source.NONE:
                return item
            case Template.Source.GETATTR:
                return getattr(self.parent.replicate(item), self.source[1])
            case Template.Source.CALL:
                return self.parent.replicate(item)(*self.source[1], **self.source[2])
            case Template.Source.GETITEM:
                return self.parent.replicate(item)[self.source[1]]

    def is_equivalent(self, other):
        return self.source == other.source and (self.parent is None or (other.parent is not None and
                                                                        self.parent.is_equivalent(other.parent)))

    def split_from_any(self, others, recursive=False):
        for index, other in enumerate(others):
            if self.is_equivalent(other):
                return index, Template()

        if recursive and (parent_split := self.parent.split_from_any(others, recursive=recursive)):
            return parent_split[0], Template(parent=parent_split[1], source=self.source)

    def __str__(self):
        match self.source[0]:
            case Template.Source.NONE:
                return "<PlaceHolder>"
            case Template.Source.GETATTR:
                return f"{str(self.parent)}.{self.source[1]}"
            case Template.Source.CALL:
                args_str_list = list(repr(arg) if isinstance(arg, str) else str(arg) for arg in self.source[1]) +\
                                [f'{name}: {repr(value) if isinstance(value, str) else value}'
                                 for name, value in self.source[2].items()]
                args_str = ", ".join(args_str_list)
                return f"{str(self.parent)}({args_str})"
            case Template.Source.GETITEM:
                return f"{str(self.parent)}" \
                       f"[{repr(self.source[1]) if isinstance(self.source[1], str) else self.source[1]}]"

    def __add__(self, *args, **kwargs):
        return self.__getattr__("__add__")(*args, **kwargs)

    def __sub__(self, *args, **kwargs):
        return self.__getattr__("__sub__")(*args, **kwargs)

    def __mul__(self, *args, **kwargs):
        return self.__getattr__("__mul__")(*args, **kwargs)

    def __truediv__(self, *args, **kwargs):
        return self.__getattr__("__truediv__")(*args, **kwargs)

    def __floordiv__(self, *args, **kwargs):
        return self.__getattr__("__floordiv__")(*args, **kwargs)

    def __mod__(self, *args, **kwargs):
        return self.__getattr__("__mod__")(*args, **kwargs)

    def __divmod__(self, *args, **kwargs):
        return self.__getattr__("__divmod__")(*args, **kwargs)

    def __radd__(self, *args, **kwargs):
        return self.__getattr__("__radd__")(*args, **kwargs)

    def __rsub__(self, *args, **kwargs):
        return self.__getattr__("__rsub__")(*args, **kwargs)

    def __rmul__(self, *args, **kwargs):
        return self.__getattr__("__rmul__")(*args, **kwargs)

    def __rtruediv__(self, *args, **kwargs):
        return self.__getattr__("__rtruediv__")(*args, **kwargs)

    def __rfloordiv__(self, *args, **kwargs):
        return self.__getattr__("__rfloordiv__")(*args, **kwargs)

    def __rmod__(self, *args, **kwargs):
        return self.__getattr__("__rmod__")(*args, **kwargs)

    def __rdivmod__(self, *args, **kwargs):
        return self.__getattr__("__rdivmod__")(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self.__getattr__("__eq__")(*args, **kwargs)

    def __lt__(self, *args, **kwargs):
        return self.__getattr__("__lt__")(*args, **kwargs)

    def __gt__(self, *args, **kwargs):
        return self.__getattr__("__gt__")(*args, **kwargs)

    def __neg__(self, *args, **kwargs):
        return self.__getattr__("__neg__")(*args, **kwargs)

    def __abs__(self, *args, **kwargs):
        return self.__getattr__("__abs__")(*args, **kwargs)

    def __and__(self, *args, **kwargs):
        return self.__getattr__("__and__")(*args, **kwargs)

    def __or__(self, *args, **kwargs):
        return self.__getattr__("__or__")(*args, **kwargs)

    def __invert__(self, *args, **kwargs):
        return self.__getattr__("__invert__")(*args, **kwargs)

    def __xor__(self, *args, **kwargs):
        return self.__getattr__("__xor__")(*args, **kwargs)

    def __rand__(self, *args, **kwargs):
        return self.__getattr__("__rand__")(*args, **kwargs)

    def __ror__(self, *args, **kwargs):
        return self.__getattr__("__ror__")(*args, **kwargs)

    def __rxor__(self, *args, **kwargs):
        return self.__getattr__("__rxor__")(*args, **kwargs)

    def __pow__(self, *args, **kwargs):
        return self.__getattr__("__pow__")(*args, **kwargs)

    def __rpow__(self, *args, **kwargs):
        return self.__getattr__("__rpow__")(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return self.__getattr__("__ne__")(*args, **kwargs)

    def __cmp__(self, *args, **kwargs):
        return self.__getattr__("__cmp__")(*args, **kwargs)


template = Template()
