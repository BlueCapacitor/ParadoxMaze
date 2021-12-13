from os import listdir, path

from main import root_path


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

        pass
