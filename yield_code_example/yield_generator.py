import time


def typical_generator(number):
    print('Start typical_generator')
    for i in range(number):
        time.sleep(1)
        yield i


print(typical_generator(10))
generator_instance = typical_generator(10)
print(generator_instance.__next__())
print(generator_instance.__next__())
print(generator_instance.__next__())
