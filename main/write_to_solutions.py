from os import path

from core.controller import Controller
from core.state import Result
from language.code import Code
from main import PrintOut, PrintProgress, get_all_levels
from ui.utilities.csv_map import CSVMap


def write_to_solutions():
    num_tested = 0
    num_success = 0

    for level_dir in get_all_levels():
        level_path = level_dir["Level Path"]
        set_num = level_dir["Set Num"]
        level_num = level_dir["Level Num"]

        with open(path.join(level_path, "code.txt"), 'r') as code_file, \
                open(path.join(level_path, f"{set_num}-{level_num}-map.csv"), 'r') as map_file:
            code_str = code_file.read()
            if len(code_str) > 0:
                map_text = map_file.read()

                csv_map = CSVMap(map_text)

                robots = csv_map.build_robots(None)
                for robot in robots:
                    robot.code = Code(robot, code=code_str)

                board = csv_map.build_board()
                controller = Controller(board, robots)

                try:
                    results = controller.run()
                except Exception:
                    print(f"\n\nError on {set_num:02}-{level_num:02}")
                    raise

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
            else:
                num_tested += 1
                print(f"{set_num:02}-{level_num:02}: Empty", file=PrintOut())

            PrintProgress().clear()
            print(f"\t{set_num:02}-{level_num:02} | {num_success} / {num_tested}", file=PrintProgress())

    PrintProgress().clear()
    print(f"\nDone | {num_success} / {num_tested} | {round(100 * num_success / num_tested, 2)}%", file=PrintOut())
