from models.Level import Level
from models.ElevatorState import ElevatorState


class LevelsController:
    """
    The module allows to avoid circular import between Semaphore and ElevatorCabin when updating levels' displays.
    """
    LEVEL_STACK = [
        Level(
            i,
            Level.INITIAL_ELEVATOR_STATE,
            Level.INITIAL_ELEVATOR_STATE,
            Level.INITIAL_ELEVATOR_LEVEL,
            Level.INITIAL_ELEVATOR_LEVEL
        ) for i in range(Level.MIN_LEVEL, Level.MAX_LEVEL + 1)
    ]

    wait_list = []  # unmanaged calls

    @staticmethod
    def update_levels_status(e_id: int, cur_level: int, cur_state: ElevatorState):
        """
        Called from ElevatorCabin execution loop on cabin level change.
        :param cur_state:
        :param cur_level:
        :param e_id: which elevator has changed it's state.
        """
        if e_id == 0:
            for level in LevelsController.LEVEL_STACK:
                level.e1_level = cur_level
                level.e1_state = cur_state
        else:
            for level in LevelsController.LEVEL_STACK:
                level.e2_level = cur_level
                level.e2_state = cur_state
