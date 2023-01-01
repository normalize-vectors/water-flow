import numpy as np
import time

# Method 1
arraya = np.empty((5000, 5000), dtype=np.float16)

start = time.time()
for row in arraya:
    for cell in row:
        a = cell
        cell = 1
stop = time.time()
print(stop - start)

# Method 2
arrayb = np.empty((5000, 5000), dtype=np.float16)

start = time.time()
for i in range(5000):
    for j in range(5000):
        a = arrayb[i][j]
        arrayb[i][j] = 1
stop = time.time()
print(stop - start)
