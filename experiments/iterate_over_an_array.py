import numpy as np
import time


# Method 1
la = []
arraya = np.arange(150*150).reshape(150, 150)
start = time.time()
it = np.nditer(arraya, flags=['multi_index'])
for x in it:
    if x > 10000:
        la.append(it.multi_index)
stop = time.time()
print(stop - start)

# Method 2
lb = []
arrayb = np.arange(150*150).reshape(150, 150)

start = time.time()
for i in range(150):
    for j in range(150):
        if arrayb[i][j] > 10000:
            lb.append((i, j))
stop = time.time()
print(stop - start)
