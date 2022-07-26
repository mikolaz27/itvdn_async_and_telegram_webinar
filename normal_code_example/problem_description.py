import time

from funcy import print_durations


def call_youtube():
    time.sleep(5)


def call_database():
    time.sleep(5)


def call_external_url():
    time.sleep(5)


def typical_sync_function(some_data):
    print("calling youtube")
    call_youtube()
    print("calling database")
    call_database()
    print("calling external_url")
    call_external_url()
    return f"I sleep for {15} seconds."


with print_durations:
    typical_sync_function(10)
