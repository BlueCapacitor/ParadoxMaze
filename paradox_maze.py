import argparse

from main.clear_all_code import clear_all_code
from main.run import run
from main.update_levels import update_levels
from main.write_solutions_to_code import write_solutions_to_code
from main.write_to_solutions import write_to_solutions

parser = argparse.ArgumentParser()
action_group = parser.add_mutually_exclusive_group()
action_group.add_argument("--update_levels",
                          help="dev: update levels from level-sheets folders",
                          action="store_true")
action_group.add_argument("--write_to_solutions",
                          help="dev: check all current programs and write them to solutions if they are correct",
                          action="store_true")
action_group.add_argument("--clear_all_code",
                          help="dev: clear the code from all levels",
                          action="store_true")
action_group.add_argument("--write_solutions_to_code",
                          help="dev: overwrite the code from all levels with the code stored in solution.txt",
                          action="store_true")

args = parser.parse_args()

if args.update_levels:
    update_levels()
elif args.write_to_solutions:
    write_to_solutions()
elif args.clear_all_code:
    clear_all_code()
elif args.write_solutions_to_code:
    write_solutions_to_code()
else:
    run()
