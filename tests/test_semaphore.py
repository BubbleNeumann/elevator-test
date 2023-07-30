import time
import unittest

from controllers.Semaphore import Semaphore
from controllers.LevelsController import LevelsController as lc
from models.ElevatorState import ElevatorState as es


class SemaphoreTest(unittest.TestCase):
    """
    Intermediate statuses are not checked since timings are not consistent due to multithreading.
    End status wait time is over-calculated.
    """
    def setUp(self) -> None:
        self.semaphore = Semaphore()

    def tearDown(self) -> None:
        self.semaphore.exec_command('quit')

    def test_second_elevator_goes_up(self):
        self.semaphore.exec_command('level 2 --call')
        time.sleep(es.GOING_UP.value[1] + es.OPENING_DOORS.value[1])
        self.assertEqual(self.semaphore.e2.cur_level_num, 2)

    def test_assign_task_to_first_elevator_when_second_one_is_busy(self):
        self.semaphore.exec_command('level 3 --call')  # task gets assign to the second elevator by default
        self.semaphore.exec_command('level 2 --call')
        time.sleep(es.GOING_UP.value[1] * 2 + es.OPENING_DOORS.value[1] + es.OPENING_DOORS.value[1])
        self.assertEqual(self.semaphore.e1.cur_level_num, 2)
        self.assertEqual(self.semaphore.e2.cur_level_num, 3)

    def test_assign_task_when_both_elevators_are_busy(self):
        self.semaphore.exec_command('level 3 --call')
        self.semaphore.exec_command('level 2 --call')
        self.semaphore.exec_command('level 4 --call')
        time.sleep(1)
        self.assertEqual(lc.wait_list[0], 4)  # check if the task was queued properly
        time.sleep(
            es.GOING_UP.value[1] * 3
            + es.OPENING_DOORS.value[1] * 2
            + es.STAYS_WITH_OPEN_DOORS.value[1] * 2
            + es.CLOSING_DOORS.value[1] * 2
        )
        self.assertEqual(self.semaphore.e1.cur_level_num, 4)

    def test_cabin_level_button(self):
        """
        An elevator is called from the second floor.
        Two passengers get in the elevator on the second floor
        and press buttons of the 3rd and 4th levels inside the cabin.
        """
        self.semaphore.exec_command('level 2 --call')
        time.sleep(es.GOING_UP.value[1] + es.OPENING_DOORS.value[1])
        self.semaphore.exec_command('cabin 1 --press-button 3')
        self.assertEqual(self.semaphore.e2.level_button_pressed[0], 3)
        self.semaphore.exec_command('cabin 1 --press-button 4')
        self.assertEqual(self.semaphore.e2.level_button_pressed[1], 4)

    def test_levels_status_update(self):
        self.semaphore.exec_command('level 2 --call')
        time.sleep(es.GOING_UP.value[1] + es.OPENING_DOORS.value[1])
        self.assertEqual(lc.LEVEL_STACK[0].e2_level, 2)

    def test_initial_test_case(self):
        self.semaphore.exec_command('level 1 --call')
        time.sleep(es.OPENING_DOORS.value[1] + es.STAYS_WITH_OPEN_DOORS.value[1])
        self.semaphore.exec_command('cabin 1 --press-button 14')
        self.semaphore.exec_command('level 15 --call')
        time.sleep(es.GOING_UP.value[1] * 15 + es.OPENING_DOORS.value[1] + es.STAYS_WITH_OPEN_DOORS.value[1])
        self.semaphore.exec_command('cabin 0 --press-button 1')
        time.sleep(es.GOING_DOWN.value[1] * 15 + es.OPENING_DOORS.value[1] + es.STAYS_WITH_OPEN_DOORS.value[1])
        self.assertEqual(self.semaphore.e1.cur_level_num, 1)
        self.assertEqual(self.semaphore.e2.cur_level_num, 14)


if __name__ == '__main__':
    unittest.main()
