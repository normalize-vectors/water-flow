import random
import time

mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

start_time = time.time()
for i in range(0, 100000):
    random.shuffle(mylist)
print(f"Random.shuffle completion time: {time.time() - start_time}")

mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

start_time = time.time()
for i in range(0, 100000):
    for i in range(0, len(mylist)):
        j = random.randint(0, len(mylist)-1)
        mylist[i], mylist[j] = mylist[j], mylist[i]
print(f"Auri shuffle completion time: {time.time() - start_time}")

mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def shuffle(lst):
    # Create a copy of the list
    shuffled = lst[:]

    # Iterate through the list in reverse order
    for i in range(len(shuffled) - 1, 0, -1):
        # Choose a random index from 0 to i
        j = random.randint(0, i)
        # Swap the elements at indices i and j
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

    return shuffled


start_time = time.time()
for i in range(0, 100000):
    shuffle(mylist)
print(f"GPT shuffle completion time: {time.time() - start_time}")
