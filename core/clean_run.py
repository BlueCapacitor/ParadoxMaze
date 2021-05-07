"""
Created on Oct 10, 2020

@author: gosha
"""

from core.state import State, Result
from core.tile import ControlTile


def clean_run(state):
    board = state.board
    clean_state = State(board)

    for charge in range(state.max_charge, state.min_charge - 1, -1):
        robot_trace_time_pairs = state.get_all_robots_with_charge(charge)

        for robot_trace, time in robot_trace_time_pairs:
            clean_state.log_robot_trace(robot_trace.copy(), time)

            tile = board.get_tile(robot_trace.x, robot_trace.y)
            if isinstance(tile, ControlTile):
                tile.trigger(clean_state, time)

        if (clean_state.is_valid | Result.NO_SUCCESS) != Result.NO_SUCCESS:
            break

        if state.is_valid == Result.POTENTIAL_SUCCESS and \
                (clean_state.is_valid | Result.POTENTIAL_SUCCESS) == Result.POTENTIAL_SUCCESS:
            break

    return clean_state
