from os import path

from main import get_all_levels


def write_solutions_to_code():
    if input("Do you really want to overwrite all code? ")[0].lower() == "y":
        print("Writing solutions to code")

        for level_dict in get_all_levels():
            level_path = level_dict["Level Path"]
            with open(path.join(level_path, "code.txt"), 'w') as code_file,\
                    open(path.join(level_path, "solution.txt"), 'r') as solution_file:
                code_file.write(solution_file.read())

        print("Done")

    else:
        print("Canceled")
