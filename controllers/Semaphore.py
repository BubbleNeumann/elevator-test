from models.Level import Level
from models.ElevatorState import ElevatorState as es
from models.ElevatorCabin import ElevatorCabin
from controllers.LevelsController import LevelsController

from threading import Thread, Lock


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance


@singleton
class Semaphore:
    """
    Assigns tasks to elevator cabins.
    Tracks time needed for each task, handles interrupts.
    """

    def __init__(self):
        self.e1 = ElevatorCabin(Level.INITIAL_ELEVATOR_LEVEL, Level.INITIAL_ELEVATOR_STATE)
        self.e2 = ElevatorCabin(Level.INITIAL_ELEVATOR_LEVEL, Level.INITIAL_ELEVATOR_STATE)

        self.mutex = Lock()
        self.elevator1_t = Thread(target=self.e1.exec_loop, args=[0, self.mutex])
        self.elevator2_t = Thread(target=self.e2.exec_loop, args=[1, self.mutex])
        self.elevator1_t.start()
        self.elevator2_t.start()

    def assign_executor(self, level_num: int):
        """
        Add tasks to task lists of the elevators.
        :param level_num:
        :return:
        """
        self.mutex.acquire()  # so that elevator object does not interrupt the assignment
        if len(LevelsController.wait_list) > 0:
            LevelsController.wait_list.append(level_num)
            self.mutex.release()
            return

        command_set = [es.OPENING_DOORS, es.STAYS_WITH_OPEN_DOORS, es.CLOSING_DOORS]

        e1_dist = self.e1.cur_level_num - level_num
        e2_dist = self.e2.cur_level_num - level_num

        # check if there is an available elevator
        # if both elevators are available -> assign the task to the nearest one
        if len(self.e1.task_queue) == 0 and len(self.e2.task_queue) == 0:
            if abs(e1_dist) < abs(e2_dist):  # then executor = e1
                command_set[:0] = [es.GOING_UP if e1_dist < 0 else es.GOING_DOWN] * abs(e1_dist)
                self.e1.task_queue.extend(command_set)
            else:  # executor = e2
                command_set[:0] = [es.GOING_UP if e2_dist < 0 else es.GOING_DOWN] * abs(e2_dist)
                self.e2.task_queue.extend(command_set)

            self.mutex.release()
            return

        # if only first elevator is available
        if len(self.e1.task_queue) == 0:
            command_set[:0] = [es.GOING_UP if e1_dist < 0 else es.GOING_DOWN] * abs(e1_dist)
            self.e1.task_queue.extend(command_set)
            self.mutex.release()
            return

        # if only second elevator is available
        if len(self.e2.task_queue) == 0:
            command_set[:0] = [es.GOING_UP if e2_dist < 0 else es.GOING_DOWN] * abs(e2_dist)
            self.e2.task_queue.extend(command_set)
            self.mutex.release()
            return

        # if both elevators are busy
        LevelsController.wait_list.append(level_num)
        self.mutex.release()

    def handle_console_input(self) -> bool:
        inp = input().split()
        match inp[0]:
            case 'level':
                if inp[1].isdigit() and Level.MIN_LEVEL <= int(inp[1]) <= Level.MAX_LEVEL:
                    match inp[2]:
                        case '--call':
                            LevelsController.LEVEL_STACK[int(inp[1]) - 1].call_elevator()
                            self.assign_executor(int(inp[1]))
                        case '--status':
                            print(LevelsController.LEVEL_STACK[int(inp[1]) - 1])
                        case _:
                            print('Level action was not specified or specified incorrectly')
                else:
                    print(f'Incorrect level parameter: {inp[1]}')
            case 'cabin':
                if inp[1].isdigit() and (int(inp[1]) == 0 or int(inp[1]) == 1) and inp[2] == '--press-button':
                    match inp[3]:
                        case 'open':
                            pass
                        case 'close':
                            pass
                        case 'call-dispatcher':
                            if int(inp[1]) == 0:
                                self.e1.press_dispatcher_call_button()
                            else:
                                self.e2.press_dispatcher_call_button()
                    pass
                else:
                    print(f'Incorrect cabin parameter: {inp[1]} {inp[2]}')
            case 'help':
                with open('resources/help.msg') as f:
                    print(f.read())
            case 'quit':
                self.e1.quit = True
                self.e2.quit = True
                self.elevator1_t.join()
                self.elevator2_t.join()
                return False
            case _:
                print(f'Unknown caller: {inp[0]}')
        return True
