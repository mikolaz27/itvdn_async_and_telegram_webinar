import time
from funcy import print_durations


def other_typical_sync_function(n):
    time.sleep(n / 2)
    print(f"I sleep for {n / 2} seconds.")


def typical_sync_function(n):
    time.sleep(n)
    print(f"I sleep for {n} seconds.")


with print_durations:
    typical_sync_function(5)
    other_typical_sync_function(8)
