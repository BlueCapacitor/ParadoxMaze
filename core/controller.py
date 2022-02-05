from language.primitive_instructions import PrimitiveInstruction
from core.state import State, Result
from tiles.abstract.control import ControlTile
from tiles.abstract.transport import TransportTile

number_of_robots = 1


class Controller(object):

    def __init__(self, board, robot, code, state=None, time=0, look_value=None):
        self.time = time

        self.board = board
        self.robot = robot

        if state is None:
            self.state = State(board)
            self.state.log_robot(self.robot, self.time)
        else:
            self.state = state

        self.code = code
        if look_value is not None:
            self.robot.look_value = look_value

    def run(self):
        global number_of_robots

        result = self.state.is_valid

        if result in (Result.FAIL, Result.UNRECOVERABLE_PARADOX):
            number_of_robots -= 1
            return [(result, self.state)]

        while self.robot.charge_remaining > 0:
            result, look_result, crash_look = self.step()

            # noinspection DuplicatedCode
            match look_result:
                case control_value, _ if control_value.validity == Result.UNRECOVERABLE_PARADOX:
                    result = Result.UNRECOVERABLE_PARADOX
                    break
                case control_value, safe_value if control_value.static:
                    look_result = control_value.current_value == safe_value
                case control_value, safe_value if len(control_value.possible_values) == 1:
                    look_result = tuple(control_value.possible_values)[0] == safe_value

            # noinspection DuplicatedCode
            match crash_look:
                case control_value, _ if control_value.validity == Result.UNRECOVERABLE_PARADOX:
                    result = Result.UNRECOVERABLE_PARADOX
                    break
                case control_value, safe_value if control_value.static:
                    crash_look = control_value.current_value == safe_value
                case control_value, safe_value if len(control_value.possible_values) == 1:
                    crash_look = tuple(control_value.possible_values)[0] == safe_value

            match look_result, crash_look:
                case None, bool():
                    pass

                case bool(), bool():
                    self.robot.look_value = look_result

                case (control_value, safe_value), bool():
                    number_of_robots += 1

                    key = self.state.get_key_for_control_value(control_value)

                    sub_controller_true = self.copy(look_value=safe_value)
                    sub_controller_true.state.control_value_log[key].assume_value(True)

                    sub_controller_false = self.copy(look_value=not safe_value)
                    sub_controller_false.state.control_value_log[key].assume_value(False)

                    result_with_true = sub_controller_true.run()
                    result_with_false = sub_controller_false.run()

                    return result_with_true + result_with_false

                case None | bool(), (control_value, _):
                    if isinstance(look_result, bool):
                        self.robot.look_value = look_result

                    number_of_robots += 1

                    key = self.state.get_key_for_control_value(control_value)

                    sub_controller_true = self.copy()
                    sub_controller_true.state.control_value_log[key].assume_value(True)

                    sub_controller_false = self.copy()
                    sub_controller_false.state.control_value_log[key].assume_value(False)

                    result_with_true = sub_controller_true.run()
                    result_with_false = sub_controller_false.run()

                    return result_with_true + result_with_false

                case (control_value_look, safe_value_look), (control_value_crash, _):
                    number_of_robots += 3

                    key_look = self.state.get_key_for_control_value(control_value_look)
                    key_crash = self.state.get_key_for_control_value(control_value_crash)

                    results = []
                    for assumed_value_look in (False, True):
                        for assumed_value_crash in (False, True):
                            sub_controller = self.copy(look_value=(assumed_value_look == safe_value_look))
                            sub_controller.state.control_value_log[key_look].assume_value(assumed_value_look)
                            sub_controller.state.control_value_log[key_crash].assume_value(assumed_value_crash)
                            results.append(sub_controller.run())

                    return sum(results, start=[])

            if result == Result.SUCCESS:
                break
            if result == Result.RECOVERABLE_PARADOX:
                continue
            if result == Result.UNRECOVERABLE_PARADOX:
                break
            if result == Result.NO_SUCCESS:
                continue
            if result == Result.FAIL:
                break

        if result == Result.RECOVERABLE_PARADOX:
            result = Result.UNRECOVERABLE_PARADOX
        if result == Result.NO_SUCCESS:
            result = Result.FAIL
        if result == Result.POTENTIAL_SUCCESS:
            result = Result.SUCCESS

        number_of_robots -= 1
        return [(result, self.state)]

    def step(self):
        instruction = self.code.peak()
        match instruction:
            case PrimitiveInstruction.SLEEP:
                self.robot.sleep()
            case PrimitiveInstruction.LEFT:
                self.robot.turn_left()
            case PrimitiveInstruction.RIGHT:
                self.robot.turn_right()
            case PrimitiveInstruction.FORWARD:
                self.robot.move_forward()
            case PrimitiveInstruction.LOOK:
                self.robot.sleep()

        self.time += 1

        self.state.log_robot(self.robot, self.time)

        crash_look = self.robot.crash_look(self.state, self.time)

        tile = self.board.get_tile(self.robot.x, self.robot.y)

        if isinstance(tile, ControlTile):
            tile.trigger(self.state, self.time)

        if isinstance(tile, TransportTile):
            self.robot.x, self.robot.y, self.time = tile.get_destination(self.state, self.robot)
            self.robot.discontinue_path()
            self.state.log_robot(self.robot, self.time)

        return (self.state.is_valid,
                self.robot.look(self.state, self.time) if instruction == PrimitiveInstruction.LOOK else None, crash_look)

    def copy(self, look_value=None):
        robot = self.robot.copy()
        return Controller(self.board, robot, self.code.copy_code(robot), state=self.state.copy(),
                          time=self.time, look_value=look_value)
