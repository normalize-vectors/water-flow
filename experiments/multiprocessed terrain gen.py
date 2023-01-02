import numpy as np
from perlin_noise import PerlinNoise
from multiprocessing import Pool

size = (100, 100)
step_factor = 0.4

noise1 = PerlinNoise(octaves=1, seed=1)
noise2 = PerlinNoise(octaves=6, seed=1)
noise3 = PerlinNoise(octaves=16, seed=1)


def gen_row(x):
    row = []
    display_row = []
    for y in range(size[1]):
        z = 100*noise1((x/size[0], y/size[1])) + 40*noise2((x, y)) + 5*noise3((x, y)) + 150
        h = round(step_factor*z)/step_factor
        row.append(z)
        display_row.append(h)
    return row + display_row


if __name__ = '__main__':
    with Pool(processes=10) as pool:
        f = pool.map(gen_row, range(size[0]))
    a = np.array(f, dtype=np.float16)
    ground, ground_display = np.split(a, 2, axis=1)
    del a
