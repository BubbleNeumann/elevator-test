from controllers.Semaphore import Semaphore


def main():
    semaphore = Semaphore()
    while True:
        if not semaphore.handle_console_input():
            break


if __name__ == '__main__':
    main()