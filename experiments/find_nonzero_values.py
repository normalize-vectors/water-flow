import numpy as np
import time

"""    While the nonzero values can be obtained with ``a[nonzero(a)]``, it is
    recommended to use ``x[x.astype(bool)]`` or ``x[x != 0]`` instead, which
    will correctly handle 0-d arrays."""

array_size = 1000

# Method 1
array_1 = np.eye(array_size, dtype=np.float16)

start = time.time()
ans_1 = np.nonzero(array_1)
stop = time.time()
print(stop - start)


# Method 2
array_2 = np.eye(array_size, dtype=np.float16)

ans_2 = []

start = time.time()
for x in range(150):
    for y in range(150):
        if array_2[x][y] != 0:
            ans_2.append((x, y))
stop = time.time()
print(stop - start)


# Method 3
array_3 = np.eye(array_size, dtype=np.float16)

start = time.time()
ans_3 = np.argwhere(array_3)
stop = time.time()
print(stop - start)
