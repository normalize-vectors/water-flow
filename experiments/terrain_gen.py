import numpy as np
from perlin_noise import PerlinNoise
from random import seed, randrange
from multiprocessing import Pool
import time

seed(1)

step_factor = 0.4  # Determines how the ground_display matrix is rounded

noise1 = PerlinNoise(randrange(1, 4), randrange(100))
noise2 = PerlinNoise(randrange(8, 16), randrange(100))
noise3 = PerlinNoise(randrange(24, 32), randrange(100))


def _gen_row(self, x):
    """
    Used to generate World.ground and World.ground_display. Returns one row of each concatenated together.
    """
    row = []
    display_row = []
    for y in range(self.size[1]):
        z = 120*self.noise1((x/self.size[0], y/self.size[1])) + 20*self.noise2((x/self.size[0],
                                                                               y/self.size[1])) + 5*self.noise3((x/self.size[0], y/self.size[1])) + 50
        h = round(self.step_factor*z)/self.step_factor
        row.append(z)
        display_row.append(h)
    return row + display_row


def terrain_generation(self):
    """
    Fill World.ground and World.ground_display with height data using perlin noise and multi-processing.
    """
    # More processes doesn't necessarily seem to make generation faster
    with Pool(processes=8) as pool:
        data = pool.map(self._gen_row, range(self.size[0]))
    concatenated_arrays = np.array(data, dtype=np.float16)
    self.ground, self.ground_display = np.split(concatenated_arrays, 2, axis=1)


start = time.time()


end = 