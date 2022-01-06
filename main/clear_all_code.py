from os import path

from main import get_all_levels

def clear_all_code():
    if input("Do you really want to clear all code? ")[0].lower() == "y":
        print("Clearing")

        for level_dict in get_all_levels():
            level_path = level_dict["Level Path"]
            with open(path.join(level_path, "code.txt"), 'w') as code_file:
                code_file.truncate()

        print("Done")

    else:
        print("Canceled")