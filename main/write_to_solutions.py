from os import listdir, path

from core.controller import Controller
from core.state import Result
from language.code import Code
from main import PrintOut, PrintProgress, root_path
from ui.utilities.csv_map import CSVMap


def write_to_solutions():
    level_sets = listdir(path.join(root_path, "levels"))
    level_sets.sort()
    level_sets_dict = {int(level_set.lstrip("set-")): level_set for level_set in level_sets if level_set[:4] == "set-"}

    num_tested = 0
    num_success = 0

    for set_num, level_set in level_sets_dict.items():
        set_path = path.join(root_path, "levels", level_set)
        levels = list(map(str, listdir(set_path)))
        levels.sort()
        levels_dict = {int(level.lstrip("level-")): level for level in levels if level[:6] == "level-"}
        for level_num, level in levels_dict.items():
            level_path = path.join(set_path, level)

            with open(path.join(level_path, "code.txt"), 'r') as code_file,\
                    open(path.join(level_path, f"{set_num}-{level_num}-map.csv"), 'r') as map_file:
                code_str = code_file.read()
                map_text = map_file.read()

                csv_map = CSVMap(map_text)

                robot = csv_map.build_robot()
                board = csv_map.build_board()
                code = Code(robot, code=code_str)
                controller = Controller(board, robot, code)

                results = controller.run()

                overall = Result.SUCCESS
                for result, _ in results:
                    if result != Result.UNRECOVERABLE_PARADOX:
                        overall |= result

                num_tested += 1
                if overall == Result.SUCCESS:
                    num_success += 1
                    with open(path.join(level_path, "solution.txt"), 'w') as solution_file:
                        solution_file.write(code_str)
                else:
                    print(f"{set_num:02}-{level_num:02}: Fail", file=PrintOut())

                PrintProgress().clear()
                print(f"\t{set_num:02}-{level_num:02} | {num_success} / {num_tested}", file=PrintProgress())

    PrintProgress().clear()
    print(f"\nDone | {num_success} / {num_tested} | {round(100 * num_success / num_tested, 2)}%", file=PrintOut())
