from enum import Enum


class ElevatorState(Enum):
    """
    Enum values represent id of status and amount of time (in seconds) required to perform an action.
    STAYS_WITH_CLOSED_DOORS is the default state of the cabin, so it doesn't need a time specification.
    """
    GOING_UP = (0, 5)
    GOING_DOWN = (1, 5)
    OPENING_DOORS = (2, 3)
    CLOSING_DOORS = (3, 3)
    STAYS_WITH_OPEN_DOORS = (4, 10)
    STAYS_WITH_CLOSED_DOORS = (5, -1)
