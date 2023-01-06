import numpy as np
from perlin_noise import PerlinNoise
from random import seed, randrange
from multiprocessing import Pool
import time

seed(1)

size = (200, 200)


step_factor = 0.4  # Determines how the ground_display matrix is rounded

noise1 = PerlinNoise(randrange(1, 4), randrange(100))
noise2 = PerlinNoise(randrange(8, 16), randrange(100))
noise3 = PerlinNoise(randrange(24, 32), randrange(100))

ground = None
ground_display = None


def _gen_row(x):
    """
    Used to generate World.ground and World.ground_display. Returns one row of each concatenated together.
    """
    row = []
    display_row = []
    for y in range(size[1]):
        z = 120*noise1((x/size[0], y/size[1])) + 20*noise2((x/size[0], y/size[1])) + \
            5*noise3((x/size[0], y/size[1])) + 50
        h = round(step_factor*z)/step_factor
        row.append(z)
        display_row.append(h)
    return row + display_row


def terrain_generation():
    """
    Fill World.ground and World.ground_display with height data using perlin noise and multi-processing.
    """
    # More processes doesn't necessarily seem to make generation faster
    with Pool(processes=10) as pool:
        data = pool.map(_gen_row, range(size[0]))
    concatenated_arrays = np.array(data, dtype=np.float16)
    ground, ground_display = np.split(concatenated_arrays, 2, axis=1)


start = time.time()

terrain_generation()

print(f"World gen took {time.time()-start}s")
