from os import path

root_path = path.dirname(path.abspath(path.join(__file__, path.pardir)))


class SingletonMeta(type):
    _instances = {}

    def __init__(cls, name, bases, cls_dict):
        SingletonMeta._instances[cls] = super(SingletonMeta, cls).__call__()
        super(SingletonMeta, cls).__init__(name, bases, cls_dict)

    def __call__(cls):
        return SingletonMeta._instances[cls]


class PrintOut(metaclass=SingletonMeta):
    # noinspection PyMethodMayBeStatic
    def write(self, new):
        print("\b" * PrintProgress().length)
        print(new)
        print(PrintProgress().text)


class PrintProgress(metaclass=SingletonMeta):
    def __init__(self):
        self.length = 0
        self.text = ""

    def write(self, new):
        self.length += len(new)
        self.text += new
        print(new)

    def clear(self):
        print("\b" * self.length)
        self.length = 0
        self.text = ""
