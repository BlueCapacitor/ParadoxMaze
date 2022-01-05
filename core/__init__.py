class MultiIndex:
    def __init__(self, obj, factory):
        self.obj = obj
        self.factory = factory

    def __getitem__(self, slices):
        return self.factory(self.obj[s] for s in slices)


class TrueSingletonMeta(type):
    _instances = {}

    def __new__(mcs, name: str, types: tuple, cls_dict: dict,
                factory=None, use_automatic_factory: bool = False,
                args=None, kwargs=None):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()

        if len(types) == 0 and factory is None:
            if len(args) == 0 or use_automatic_factory:
                factory = type("<<SingletonMetaAutomaticClass>>", (), cls_dict)
            else:
                factory = object.__new__
        elif len(types) == 1:
            if use_automatic_factory:
                factory = type("<<SingletonMetaAutomaticClass>>", types, cls_dict)
            elif factory is None:
                factory = types[0]
            else:
                raise TypeError("Do not provide a type for a singleton with a factory function")
        elif len(types) > 1:
            if factory is None or use_automatic_factory:
                factory = type("<<SingletonMetaAutomaticClass>>", types, cls_dict)
            else:
                raise TypeError("Do not provide a type for a singleton with a factory function")

        out = factory(*args, **kwargs)

        for attr, value in cls_dict.items():
            setattr(out, attr, value)

        return out
