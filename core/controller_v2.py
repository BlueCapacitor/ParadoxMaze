from collections import deque

from language.primitive_instructions import PrimitiveInstruction
from core.state_v2 import ControlValue, State, Result
from tiles.abstract.control import ControlTile
from tiles.abstract.transport import TransportTile


class Controller:

    def __init__(self, board, robots, state=None):
        self.board = board
        self.robots = robots
        self.robot_queue = deque([robot for robot in self.robots if robot.peak != PrimitiveInstruction.LOOK] +
                                 [robot for robot in self.robots if robot.peak == PrimitiveInstruction.LOOK])

        if state is None:
            self.state = State(board)
            for robot in self.robots:
                self.state.log_robot(robot)
        else:
            self.state = state

    def run(self):
        validity = self.state.is_valid

        while self.robot_queue:
            if validity == Result.UNRECOVERABLE_PARADOX:
                return (validity, self.state),

            robot = self.robot_queue[0]
            if robot.peak == PrimitiveInstruction.LOOK:
                look_value = robot.passive_look(self.state)
                if isinstance(look_value, ControlValue) and not look_value.static and \
                        len(look_value.possible_values) != 1:
                    self.robot_queue.rotate(-1)
                    robot = self.robot_queue[0]

            if robot.charge_remaining <= 0:
                self.robot_queue.popleft()
                continue

            instruction = self.step_robot(robot)

            split_needed = False
            crash_key = None
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

                case control_value, _ if not control_value.static and len(control_value.possible_values) > 1:
                    crash_key = self.state.get_key_for_control_value(control_value)
                    split_needed = True

            if instruction == PrimitiveInstruction.LOOK:
                robot_index = self.robots.index(robot)

                match self.look_robot(robot):
                    case bool() as look_value:
                        look_robot = (robot_index, None, ((look_value, None),))
                    case control_value, _ if control_value.validity == Result.UNRECOVERABLE_PARADOX:
                        return (Result.UNRECOVERABLE_PARADOX, self.state),
                    case control_value, safe_value if control_value.static:
                        look_robot = (robot_index, None, ((control_value.current_value == safe_value, None),))
                    case control_value, safe_value if len(control_value.possible_values) == 1:
                        look_robot = (robot_index, None,
                                      ((tuple(control_value.possible_values)[0] == safe_value, None),))

                    case control_value, safe_value if len(control_value.possible_values) > 1:
                        key = self.state.get_key_for_control_value(control_value)
                        look_robot = (robot_index, key, ((safe_value, True), (not safe_value, False)))
                        split_needed = True

            look_robot_index, look_key, look_possibilities = look_robot or (None, None, ((None, None),))

            results = [] if split_needed else None
            for assumed_crash_value in (True, False) if crash_key is not None else (None,):
                for assumed_look_seen, assumed_look_value in look_possibilities:
                    sub_controller = self.copy() if split_needed else self

                    if crash_key is not None:
                        sub_controller.state.control_value_log[crash_key].assume_value(assumed_crash_value)

                    if look_robot is not None:
                        sub_controller.robots[look_robot_index].look_value = assumed_look_seen
                        if look_key is not None:
                            sub_controller.state.control_value_log[look_key].assume_value(assumed_look_value)

                    if split_needed:
                        results.append(sub_controller.run())

            if split_needed:
                return sum(results, start=())

            validity = self.state.is_valid

        return (validity.finalized, self.state),

    def step_robot(self, robot):
        instruction = robot.get_next_instruction()
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
            robot.x, robot.y, robot.time = tile.get_destination(self.state, robot)
            robot.discontinue_path()
            self.state.log_robot(robot)

        return instruction

    def look_robot(self, robot):
        return robot.passive_look(self.state)

    def crash_look_robot(self, robot):
        return robot.crash_look(self.state)

    def copy(self):
        return Controller(self.board, [robot.copy() for robot in self.robots], state=self.state.copy())
