from core.state import State, Result


def clean_run(result_tuple):
    result, state = result_tuple

    match result:
        case Result.SUCCESS:
            return result, state

        case Result.UNRECOVERABLE_PARADOX:
            board = state.board
            clean_state = State(board, control_value_log=state.control_value_log, sticky_values=state.sticky_values)

            for charge in range(state.max_charge, state.min_charge - 1, -1):
                robot_trace_time_pairs = state.get_all_robots_with_charge(charge)

                for robot_trace, time in robot_trace_time_pairs:
                    clean_state.log_robot_trace(robot_trace.copy(), time)

                if clean_state.is_valid == Result.UNRECOVERABLE_PARADOX:
                    break

            return result, clean_state

        case Result.FAIL:
            board = state.board
            clean_state = State(board, control_value_log=state.control_value_log, sticky_values=state.sticky_values)
            hidden_continuity_ids = set()

            for charge in range(state.max_charge, state.min_charge - 1, -1):
                robot_trace_time_pairs = state.get_all_robots_with_charge(charge)

                for robot_trace, time in robot_trace_time_pairs:
                    for hidden_continuity_id in hidden_continuity_ids:
                        if len(robot_trace.continuity_id) > len(hidden_continuity_id) and \
                                robot_trace.continuity_id[:len(hidden_continuity_id)] == hidden_continuity_id:
                            continue

                    clean_state.log_robot_trace(robot_trace.copy(), time)

                    if not robot_trace.static_crash_look(state, time):
                        hidden_continuity_ids.add(robot_trace.continuity_id)

            return result | clean_state.is_valid, clean_state
