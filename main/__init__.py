from os import listdir, path

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
        print("\b" * PrintProgress().length, end="")
        print(new, end="")
        print(PrintProgress().text, end="")


class PrintProgress(metaclass=SingletonMeta):
    def __init__(self):
        self.length = 0
        self.text = ""

    def write(self, new):
        new = "".join(c for c in new if c != '\n')
        self.length += len(new)
        self.text += new
        print(new, end="")

    def clear(self):
        print("\b" * self.length, end="")
        self.length = 0
        self.text = ""


def get_all_levels():
    out = []

    level_sets = listdir(path.join(root_path, "levels"))
    level_sets.sort()
    level_sets_dict = {int(level_set.lstrip("set-")): level_set for level_set in level_sets if level_set[:4] == "set-"}

    for set_num, level_set in level_sets_dict.items():
        set_path = path.join(root_path, "levels", level_set)
        levels = list(map(str, listdir(set_path)))
        levels.sort()
        levels_dict = {int(level.lstrip("level-")): level for level in levels if level[:6] == "level-"}
        for level_num, level in levels_dict.items():
            level_path = path.join(set_path, level)
            out.append({"Level Path": level_path,
                        "Level Num": level_num,
                        "Set Path": set_path,
                        "Set Num": set_num})
    return out
