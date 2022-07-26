def print_name(prefix):
    print("Searching prefix:{}".format(prefix))
    while True:
        # yeild used to create coroutine
        name = yield
        if prefix in name:
            print(name)


if __name__ == '__main__':
    coroutine = print_name("Dear")
    coroutine.send(None)
    # coroutine.__next__()
    coroutine.send("James")
    coroutine.send("Mykhailo")
    coroutine.send("Vasyl")
    coroutine.send("Chornobay")
    coroutine.send("Dear James")
    coroutine.close()
