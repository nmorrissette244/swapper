import time


def deadline():
    deadline = int(time.time()) + (10 * 60)
    return deadline


print(deadline())
