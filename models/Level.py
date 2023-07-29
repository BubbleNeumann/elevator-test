from models.ElevatorState import ElevatorState


class Level:
    MAX_LEVEL = 20
    MIN_LEVEL = 1
    INITIAL_ELEVATOR_STATE = ElevatorState.STAYS_WITH_CLOSED_DOORS
    INITIAL_ELEVATOR_LEVEL = 1

    def __init__(
            self,
            num: int,
            e1_state: ElevatorState,
            e2_state: ElevatorState,
            e1_level: int,
            e2_level: int
    ) -> None:
        if num < Level.MIN_LEVEL or num > Level.MAX_LEVEL:
            raise Exception('Wrong level number.')

        self.num = num
        self.e1_state = e1_state
        self.e2_state = e2_state
        self.e1_level = e1_level
        self.e2_level = e2_level

    def call_elevator(self):
        """
        Has no internal logic since semaphore already has all the info it needs.
        :return:
        """
        print(f'Elevator was called from level {self.num}')

    def __str__(self) -> str:
        return f'l{self.num}: e1[{self.e1_level},{self.e1_state}] e2[{self.e2_level},{self.e2_state}]'