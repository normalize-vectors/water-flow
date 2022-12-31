import numpy as np
from access_test_import import b, Array_Holder
import time
import random

a = np.empty((1000, 1000), dtype=np.float64)


class Other_Array_Holder():
    def __init__(self):
        self.d = np.empty((1000, 1000), dtype=np.float64)


test_quantity = 1000000


# Test local array
start = time.time()
for i in range(test_quantity):
    x = random.randint(0, 999)
    y = random.randint(0, 999)
    j = a[x][y]
stop = time.time()
print(f"Finished local array test in {stop-start}s")


# Test external array
start = time.time()
for i in range(test_quantity):
    x = random.randint(0, 999)
    y = random.randint(0, 999)
    j = b[x][y]
stop = time.time()
print(f"Finished external array test in {stop-start}s")

# Test local array in a class
arrb = Other_Array_Holder()
start = time.time()
for i in range(test_quantity):
    x = random.randint(0, 999)
    y = random.randint(0, 999)
    j = arrb.d[x][y]
stop = time.time()
print(f"Finished local array in class test in {stop-start}s")

# Test external array in a class
arr = Array_Holder()
start = time.time()
for i in range(test_quantity):
    x = random.randint(0, 999)
    y = random.randint(0, 999)
    j = arr.c[x][y]
stop = time.time()
print(f"Finished external array in class test in {stop-start}s")
