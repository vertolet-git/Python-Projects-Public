import multiprocessing
import time

# https://www.youtube.com/watch?v=fKl2JW_qrso

start = time.perf_counter()

# Manual way


def do_something(seconds):
    print(f"Sleeping {seconds} second(s)...")
    time.sleep(seconds)
    print("Done sleeping...")


"""
p1 = multiprocessing.Process(target=do_something)
p2 = multiprocessing.Process(target=do_something)

p1.start()
p2.start()

p1.join()
p2.join()
"""

# Multiple times

processes = []

for _ in range(10):
    p = multiprocessing.Process(target=do_something, args=[1.5])
    p.start()
    processes.append(p)

for process in processes:
    process.join()

finish = time.perf_counter()

print(f"Finished in {round(finish-start, 2)} second(s)")
