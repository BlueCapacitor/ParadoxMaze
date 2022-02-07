from core.state_v2 import State, Result


def clean_run(state):
    board = state.board
    clean_state = State(board, control_value_log=state.control_value_log, sticky_values=state.sticky_values)

    for charge in range(state.max_charge, state.min_charge - 1, -1):
        robot_trace_time_pairs = state.get_all_robots_with_charge(charge)

        for robot_trace, time in robot_trace_time_pairs:
            clean_state.log_robot_trace(robot_trace.copy(), time)

        if clean_state.is_valid in (Result.FAIL, Result.UNRECOVERABLE_PARADOX):
            break

    return clean_state
