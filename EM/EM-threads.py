from threading import Thread
import os
import math

# https://www.youtube.com/watch?v=ecKWiaHCEKs


def calc():
    for i in range(0, 4000000):
        math.sqrt(i)


threads = []

for i in range(os.cpu_count()):
    print("Registering thread %d" % i)
    threads.append(Thread(target=calc))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
