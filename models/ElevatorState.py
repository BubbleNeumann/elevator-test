from enum import Enum


class ElevatorState(Enum):
    """
    Enum values represent id of status and amount of time (in seconds) required to perform an action.
    STAYS_WITH_CLOSED_DOORS is the default state of the cabin, so it doesn't need a time specification.
    """
    GOING_UP = (0, 2)
    GOING_DOWN = (1, 2)
    OPENING_DOORS = (2, 2)
    CLOSING_DOORS = (3, 2)
    STAYS_WITH_OPEN_DOORS = (4, 2)
    STAYS_WITH_CLOSED_DOORS = (5, -1)
