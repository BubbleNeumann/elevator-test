from models.Level import Level
from models.ElevatorState import ElevatorState as es
from controllers.LevelsController import LevelsController

import time
from threading import Lock


class ElevatorCabin:
    def __init__(self, cur_level_num: int, state: es):
        if cur_level_num < Level.MIN_LEVEL or cur_level_num > Level.MAX_LEVEL:
            raise Exception("Wrong level number.")
        self.cur_level_num = cur_level_num
        self.state = state
        self.prev_moving_direction = None  # so if elevator is moving up, it keeps going up until there are no calls from above levels
        self.level_button_pressed = []
        self.task_queue = []  # a way of communication between the elevator cabin and the Semaphore
        self.quit = False

    def press_level_button(self, level_num: int, e_id: int, mutex: Lock):
        if level_num > Level.MAX_LEVEL or level_num < Level.MIN_LEVEL:
            raise Exception('Wrong level_num parameter')
        print(f'e{e_id + 1}: Button {level_num} was pressed')
        mutex.acquire()
        self.level_button_pressed.append(level_num)
        mutex.release()

    def press_door_open_button(self, e_id: int, mutex: Lock):
        mutex.acquire()
        print(f'e{e_id + 1} door open button was pressed')
        match self.state:
            case es.CLOSING_DOORS | es.STAYS_WITH_CLOSED_DOORS:
                self.state = es.OPENING_DOORS
                self.task_queue[:0] = [es.STAYS_WITH_OPEN_DOORS, es.CLOSING_DOORS]
            case es.STAYS_WITH_OPEN_DOORS:
                self.task_queue[:0] = [es.STAYS_WITH_OPEN_DOORS]

        mutex.release()

    def press_door_close_button(self, e_id: int, mutex: Lock):
        print(f'e{e_id + 1} door close button was pressed')
        mutex.acquire()
        if self.state == es.STAYS_WITH_OPEN_DOORS:
            self.state = es.CLOSING_DOORS
        mutex.release()

    @staticmethod
    def press_dispatcher_call_button():
        print('Congrats! You can now talk to the dispatcher!')

    def update_state(self, new_state: es, id: int):
        self.state = new_state
        print(f'Elevator {id + 1} (currently on the level {self.cur_level_num}) \
              was assigned status {es(self.state).name}')

    def get_task_from_wait_lists(self):
        target_level = None
        dist = 0
        if len(self.level_button_pressed) > 0:
            target_i = 0
            if self.prev_moving_direction == es.GOING_DOWN:  # prefer levels below, which are closest to the current
                self.level_button_pressed.sort()
                while self.level_button_pressed[target_i] > self.cur_level_num and target_i < (len(self.level_button_pressed) - 1):
                    target_i += 1
            elif self.prev_moving_direction == es.GOING_UP:  # prefer levels above, which are closest to the current
                self.level_button_pressed.sort(reverse=True)
                while self.level_button_pressed[target_i] < self.cur_level_num and target_i < (len(self.level_button_pressed) - 1):
                    target_i += 1

            target_level = self.level_button_pressed[target_i]
            dist = self.cur_level_num - target_level
            self.level_button_pressed.remove(target_level)
        elif len(LevelsController.wait_list) > 0:
            level = LevelsController.wait_list[0]
            dist = self.cur_level_num - level
            LevelsController.wait_list.remove(
                level)  # removes level num from the list even if there were several entries with the same value
        if dist != 0:
            task_from_wait_list = [es.OPENING_DOORS, es.STAYS_WITH_OPEN_DOORS, es.CLOSING_DOORS]
            task_from_wait_list[:0] = [es.GOING_UP if dist < 0 else es.GOING_DOWN] * abs(dist)
            self.task_queue.extend(task_from_wait_list)

    def exec_loop(self, id: int, mutex: Lock):
        while True:
            if self.quit:  # quit value is set from Semaphore
                break

            mutex.acquire()
            if len(self.task_queue) == 0:
                if len(self.level_button_pressed) > 0:
                    self.get_task_from_wait_lists()
                else:
                    mutex.release()  # we don't need access to the task queue at this point
                    time.sleep(1)
                    continue

            while len(self.task_queue) > 0:
                self.update_state(new_state=self.task_queue.pop(0), id=id)
                mutex.release()  # so that semaphore could assign new tasks at the time
                time.sleep(self.state.value[1])

                match self.state:
                    case es.GOING_UP:
                        self.cur_level_num += 1
                        self.prev_moving_direction = es.GOING_UP
                    case es.GOING_DOWN:
                        self.cur_level_num -= 1
                        self.prev_moving_direction = es.GOING_DOWN

                mutex.acquire()
                LevelsController.update_levels_status(id, self.cur_level_num, self.state)

            # if the elevator is done closing doors, and it has no further tasks,
            # this means that it now stays with closed doors
            if self.state == es.CLOSING_DOORS:
                if len(LevelsController.wait_list) == 0 and len(self.level_button_pressed) == 0:
                    self.update_state(es.STAYS_WITH_CLOSED_DOORS, id)
                    LevelsController.update_levels_status(id, self.cur_level_num, self.state)
                else:  # if one of the wait lists is not empty
                    self.get_task_from_wait_lists()

            mutex.release()
