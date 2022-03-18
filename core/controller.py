from collections import deque

from core.robot import DiscontinuityType
from language.breakpoint_wrapper import BreakpointWrapper
from language.primitive_instructions import PrimitiveInstruction
from core.state import ControlValue, State, Result
from tiles.abstract.control import ControlTile
from tiles.abstract.transport import TransportTile


class Controller:
    def __init__(self, board, robots, preserve_order=False, state=None):
        self.board = board
        if preserve_order or not board.needs_nondeterministic_controller:
            self.robot_queue = deque(robots)
        else:
            self.robot_queue = deque([robot for robot in robots if robot.peak != PrimitiveInstruction.LOOK] +
                                     [robot for robot in robots if robot.peak == PrimitiveInstruction.LOOK])

        if state is None:
            self.state = State(board)
            for robot in robots:
                self.state.log_robot(robot)
        else:
            self.state = state

    def run(self):
        if self.board.needs_nondeterministic_controller:
            return self.nondeterministic_run()
        else:
            return self.deterministic_run()

    def deterministic_run(self, stop_all_on_fail=False):
        validity = self.state.is_valid
        self.robot_queue.append(None)
        robots_to_look = deque()
        while self.robot_queue[0] != self.robot_queue[-1] and \
                ((not stop_all_on_fail) or validity | Result.NO_SUCCESS == Result.NO_SUCCESS):
            robot = self.robot_queue[0]

            if robot is None:
                for robot in robots_to_look:
                    look_value = self.look_robot(robot)
                    assert isinstance(look_value, bool)
                    robot.look_value = look_value

                robots_to_look.clear()

            else:
                if robot.charge_remaining <= 0:
                    self.robot_queue.popleft()
                else:
                    instruction = self.step_robot(robot)
                    if instruction == PrimitiveInstruction.LOOK:
                        robots_to_look.append(robot)

            validity = self.state.is_valid

            if stop_all_on_fail or robot is None:
                self.robot_queue.rotate(-1)
            else:
                crash_look = self.crash_look_robot(robot)
                assert isinstance(crash_look, bool)
                if crash_look:
                    self.robot_queue.rotate(-1)
                else:
                    self.robot_queue.popleft()

        return (validity.finalized, self.state),

    def nondeterministic_run(self):
        validity = self.state.is_valid

        while self.robot_queue:
            if validity == Result.UNRECOVERABLE_PARADOX:
                return (validity, self.state),

            robot = self.robot_queue[0]
            if (not robot.skip_step) and robot.peak == PrimitiveInstruction.LOOK:
                look_value = robot.passive_look(self.state)
                if isinstance(look_value, ControlValue) and not look_value.static and \
                        len(look_value.possible_values) != 1:
                    self.robot_queue.rotate(-1)
                    robot = self.robot_queue[0]

            if robot.charge_remaining <= 0:
                self.robot_queue.popleft()
                continue

            instruction = self.step_robot(robot)
            if instruction is None:
                continue

            split_needed = False
            crash_key = None
            crash_safe_value = None
            look_robot = None

            match self.crash_look_robot(robot):
                case True:
                    pass
                case False:
                    self.robot_queue.popleft()
                    continue
                case control_value, safe_value if control_value.static and control_value.current_value != safe_value:
                    self.robot_queue.popleft()
                    continue
                case control_value, safe_value if len(control_value.possible_values) == 1 and tuple(
                        control_value.possible_values)[0] != safe_value:
                    self.robot_queue.popleft()
                    continue

                case control_value, safe_value if not control_value.static and len(control_value.possible_values) > 1:
                    crash_key = self.state.get_key_for_control_value(control_value)
                    crash_safe_value = safe_value
                    split_needed = True

            if instruction == PrimitiveInstruction.LOOK:
                match self.look_robot(robot):
                    case bool() as look_value:
                        look_robot = (None, ((look_value, None),))
                    case control_value, _ if control_value.validity == Result.UNRECOVERABLE_PARADOX:
                        return (Result.UNRECOVERABLE_PARADOX, self.state),
                    case control_value, safe_value if control_value.static:
                        look_robot = (None, ((control_value.current_value == safe_value, None),))
                    case control_value, safe_value if len(control_value.possible_values) == 1:
                        look_robot = (None, ((tuple(control_value.possible_values)[0] == safe_value, None),))

                    case control_value, safe_value if len(control_value.possible_values) > 1:
                        key = self.state.get_key_for_control_value(control_value)
                        look_robot = (key, ((safe_value, True), (not safe_value, False)))
                        split_needed = True

            look_key, look_possibilities = look_robot or (None, ((None, None),))

            results = [] if split_needed else None
            for assumed_crash_value in (True, False) if crash_key is not None else (None,):
                for assumed_look_seen, assumed_look_value in look_possibilities:
                    sub_controller = self.copy() if split_needed else self

                    if look_robot is not None:
                        sub_controller.robot_queue[0].look_value = assumed_look_seen
                        if look_key is not None:
                            sub_controller.state.control_value_log[look_key].assume_value(assumed_look_value)

                    if crash_key is not None:
                        sub_controller.state.control_value_log[crash_key].assume_value(assumed_crash_value)
                        if assumed_crash_value != crash_safe_value:
                            sub_controller.robot_queue.popleft()

                    if split_needed:
                        results.append(sub_controller.run())

            if split_needed:
                return sum(results, start=())

            validity = self.state.is_valid

        validity = self.state.is_valid
        return (validity.finalized, self.state),

    def step_robot(self, robot):
        instruction = robot.get_next_instruction()
        if isinstance(instruction, BreakpointWrapper):
            instruction = instruction.wrapped
            breakpoint()

        if robot.skip_step:
            robot.skip_step = False
            return instruction

        match instruction:
            case PrimitiveInstruction.SLEEP:
                robot.sleep()
            case PrimitiveInstruction.LEFT:
                robot.turn_left()
            case PrimitiveInstruction.RIGHT:
                robot.turn_right()
            case PrimitiveInstruction.FORWARD:
                robot.move_forward()
            case PrimitiveInstruction.LOOK:
                robot.sleep()

        self.state.log_robot(robot)

        tile = self.board.get_tile(robot.x, robot.y)

        if isinstance(tile, ControlTile):
            tile.trigger(self.state, robot.time)

        if isinstance(tile, TransportTile):
            destinations = tile.get_destinations(self.state, robot)
            robot.code.appendleft(instruction)

            assert self.robot_queue.popleft() == robot

            robot.skip_step = True

            for destination in destinations:
                new_robot = robot.copy(discontinuity_type=DiscontinuityType.CHILD)
                new_robot.x, new_robot.y, new_robot.time = destination
                self.state.log_robot(new_robot)
                self.robot_queue.appendleft(new_robot)
            return None
        else:
            return instruction

    def look_robot(self, robot):
        return robot.passive_look(self.state)

    def crash_look_robot(self, robot):
        return robot.crash_look(self.state)

    def copy(self):
        return Controller(self.board, [robot.copy() for robot in self.robot_queue], preserve_order=True,
                          state=self.state.copy())
