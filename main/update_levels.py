from os import listdir, path, mkdir

from main import root_path

level_sheet_paths = {int(name[4: 6]): name for name in listdir(path.join(root_path, "level-sheets"))
                     if name[:4] == "set-" and not name.endswith(".numbers")}

for set_number in level_sheet_paths:
    level_sheet_set_path = path.join(root_path, "level-sheets", level_sheet_paths[set_number])

    level_set_path = path.join(root_path, "levels", f"set-{set_number:02}")
    if not path.exists(level_set_path):
        mkdir(level_set_path)
        mkdir(path.join(level_set_path, "resources"))
        with open(path.join(level_set_path, "resources", "set-colors.txt"), 'x') as file:
            file.write("1, 0, 0\n0.5, 0, 0\n0, 0, 0\n1, 0.5, 0.5")

    for map_file_name in listdir(level_sheet_set_path):
        map_file_name = str(map_file_name)
        level_number = int(map_file_name.lstrip(str(set_number)).rstrip("map.csv").strip("-"))
        level_path = path.join(root_path, "levels", f"set-{set_number:02}", f"level-{level_number:02}")
        if not path.exists(level_path):
            mkdir(level_path)
        with open(path.join(level_sheet_set_path, map_file_name), 'r') as source_file:
            with open(path.join(level_path, map_file_name), 'w') as dest_file:
                dest_file.write(source_file.read())

        for file_name in ("code.txt", "default_code.txt", "instruction_text.md", "solution.txt"):
            file_path = path.join(level_path, file_name)
            if not path.exists(file_path):
                with open(file_path, 'x'):
                    pass
