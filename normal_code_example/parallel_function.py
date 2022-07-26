import threading
import time

from funcy import print_durations

TIME_TO_SLEEP = 6


def other_typical_sync_function(n):
    time.sleep(n / 2)
    print(f"I sleep for {n / 2} seconds.")


def typical_sync_function(n):
    time.sleep(n)
    print(f"I sleep for {n} seconds.")


with print_durations:
    t1 = threading.Thread(target=other_typical_sync_function,
                          args=(TIME_TO_SLEEP,))
    t2 = threading.Thread(target=typical_sync_function, args=(TIME_TO_SLEEP,))
    t1.start()
    t2.start()

    t1.join()
    t2.join()


