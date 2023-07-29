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
        self.level_button_pressed = []
        self.task_queue = []  # a way of communication between the elevator cabin and the Semaphore
        self.quit = False

    def press_level_button(self, level_num: int):
        self.level_button_pressed.append(level_num)

    def press_door_open_button(self, mutex: Lock):
        mutex.acquire()
        match self.state:
            case es.CLOSING_DOORS:
                self.state = es.OPENING_DOORS
                self.task_queue[:0] = []

        mutex.release()


    def press_door_close_button(self):
        if self.state == es.OPENING_DOORS or self.state == es.STAYS_WITH_OPEN_DOORS:
            self.state = es.CLOSING_DOORS
        if len(self.level_button_pressed) == 0:
            self.state = es.STAYS_WITH_CLOSED_DOORS
            return

    @staticmethod
    def press_dispatcher_call_button():
        print('Congrats! You can now talk to the dispatcher!')

    def update_state(self, new_state: es, id: int):
        self.state = new_state
        print(f'Elevator {id} (currently on the level {self.cur_level_num}) \
              was assigned status {es(self.state).name}')

    def exec_loop(self, id: int, mutex: Lock):
        while True:
            if self.quit:  # quit value is set from Semaphore
                break

            mutex.acquire()
            if len(self.task_queue) == 0:
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
                    case es.GOING_DOWN:
                        self.cur_level_num -= 1

                mutex.acquire()
                LevelsController.update_levels_status(id, self.cur_level_num, self.state)

            # if the elevator is done closing doors, and it has no further tasks,
            # this means that it now stays with closed doors
            if self.state == es.CLOSING_DOORS:
                if len(LevelsController.wait_list) == 0:
                    self.update_state(es.STAYS_WITH_CLOSED_DOORS, id)
                    LevelsController.update_levels_status(id, self.cur_level_num, self.state)
                else:
                    level = LevelsController.wait_list[0]
                    dist = self.cur_level_num - level
                    LevelsController.wait_list.remove(level)
                    if dist != 0:
                        task_from_wait_list = [es.OPENING_DOORS, es.STAYS_WITH_OPEN_DOORS, es.CLOSING_DOORS]
                        task_from_wait_list[:0] = [es.GOING_UP if dist < 0 else es.GOING_DOWN] * abs(dist)
                        self.task_queue.extend(task_from_wait_list)


            mutex.release()
