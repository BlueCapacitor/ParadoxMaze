"""
Created on Oct 10, 2020

@author: gosha
"""

from core.instruction_set import Instruction
from core.state import State, Result
from core.tile import TransportTile, ControlTile

number_of_robots = 1


class Controller(object):

    def __init__(self, board, robot, instructions, state=None):
        self.board = board
        self.robot = robot

        if state is None:
            self.state = State(board)
            self.state.log_robot(self.robot, self.time)
        else:
            self.state = state

        self.instructions = instructions

    def run(self):
        global number_of_robots

        result = None

        while self.robot.charge_remaining > 0:
            result, look_result, crash_look = self.step()

            if look_result is not None and isinstance(crash_look, bool):
                if isinstance(look_result, bool):
                    self.robot.look_value = look_result
                else:
                    control_value, safe_value = look_result
                    if control_value.validity == Result.UNRECOVERABLE_PARADOX:
                        result = Result.UNRECOVERABLE_PARADOX
                        break
                    else:
                        if control_value.static:
                            self.robot.look_value = (control_value.current_value and safe_value) or not (
                                        control_value.current_value or safe_value)
                        elif len(control_value.possible_values) == 1:
                            value = control_value.possible_values[0]
                            self.robot.look_value = (value and safe_value) or not (value or safe_value)
                        else:
                            number_of_robots += 1

                            key = self.state.get_key_for_control_value(control_value)

                            sub_controller_true = self.copy(look_value=safe_value)
                            sub_controller_true.state.control_value_log[key].assume_value(True)

                            sub_controller_false = self.copy(look_value=not safe_value)
                            sub_controller_false.state.control_value_log[key].assume_value(False)

                            result_with_true = sub_controller_true.run()
                            result_with_false = sub_controller_false.run()

                            return result_with_true + result_with_false

            if look_result is None and not (isinstance(crash_look, bool)):
                control_value, safe_value = crash_look
                if control_value.validity == Result.UNRECOVERABLE_PARADOX:
                    result = Result.UNRECOVERABLE_PARADOX
                    break
                else:
                    if control_value.static:
                        safe = (control_value.current_value and safe_value) or not (
                                    control_value.current_value or safe_value)
                        result |= Result.FAIL if not safe else Result.SUCCESS
                    elif len(control_value.possible_values) == 1:
                        value = tuple(control_value.possible_values)[0]
                        safe = (value and safe_value) or not (value or safe_value)
                        result |= Result.FAIL if not safe else Result.SUCCESS
                    else:
                        number_of_robots += 1

                        key = self.state.get_key_for_control_value(control_value)

                        sub_controller_true = self.copy()
                        sub_controller_true.state.control_value_log[key].assume_value(True)

                        sub_controller_false = self.copy()
                        sub_controller_false.state.control_value_log[key].assume_value(False)

                        result_with_true = sub_controller_true.run()
                        result_with_false = sub_controller_false.run()

                        return result_with_true + result_with_false

                # TODO: Check for both look_result is not None and not(isinstance(crash_look, bool))
                #  (split controller into 4)

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
        instruction = self.instructions.next_instruction(self.robot)
        if instruction == Instruction.SLEEP:
            self.robot.sleep()
        if instruction == Instruction.LEFT:
            self.robot.turn_left()
        if instruction == Instruction.RIGHT:
            self.robot.turn_right()
        if instruction == Instruction.FORWARD:
            self.robot.move_forward()
        look_result = None
        if instruction == Instruction.LOOK:
            look_result = self.robot.look(self.state)
        if instruction == Instruction.DEBUG:
            print("@@@@ Debug @@@@")
            return Result.NO_SUCCESS, None

        self.state.log_robot(self.robot)

        crash_look = self.robot.crash_look(self.state)

        tile = self.board.get_tile(self.robot.x, self.robot.y)

        if isinstance(tile, ControlTile):
            tile.trigger(self.state, self.robot)

        if isinstance(tile, TransportTile):
            self.robot.x, self.robot.y, self.robot.time = tile.get_destination(self.state, self.robot)
            self.robot.discontinue_path()
            self.state.log_robot(self.robot)

        return self.state.is_valid, look_result if instruction == Instruction.LOOK else None, crash_look

    def copy(self, look_value=None):
        return Controller(self.board, self.robot.copy(), self.instructions.copy(), state=self.state.copy())
