import argparse

from main.run import run
from main.update_levels import update_levels
from main.write_to_solutions import write_to_solutions

parser = argparse.ArgumentParser()
action_group = parser.add_mutually_exclusive_group()
action_group.add_argument("--update_levels", help="dev: update levels from level-sheets folders", action="store_true")
action_group.add_argument("--write_to_solutions",
                          help="dev: check all current programs and write them to solutions if they are correct",
                          action="store_true")

args = parser.parse_args()

if args.update_levels:
    update_levels()
elif args.write_to_solutions:
    write_to_solutions()
else:
    run()
