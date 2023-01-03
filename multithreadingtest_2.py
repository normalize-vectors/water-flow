"""Can't pickle local object 'main.<locals>.gen_row'"""
# as part of world generation
import numpy as np
from perlin_noise import PerlinNoise
from random import seed, shuffle
from multiprocessing import Pool
import time
seed(a=1)

class World:
    def __init__(self, size=(1024,1024), chunk_size=64):
        #region "Constants"
        #------------------------------------------------------------
        "CONSTANTS"
        self.cell_width = 6  # How many pixels wide each cell will appear
        self.size = size  # Defines the shape of the board
        self.chunk_size = chunk_size # Defines the chunk size
        self.chunk_count = self.size[0]/self.chunk_size
        self.water = np.zeros(size, dtype=np.float16)
        self.step_factor = 0.4
        #endregion
        # the noise layers ------------------------------------------
        self.noise1 = PerlinNoise(octaves=1, seed=1)
        self.noise2 = PerlinNoise(octaves=6, seed=1)
        self.noise3 = PerlinNoise(octaves=16, seed=1)

    # TERRAIN GENERATION
    #------------------------------------------------------------
    "TERRAIN GENERATION - WORLD"
    def gen_row(self, x):
        row = []
        display_row = []
        for y in range(self.size[1]):
            z = 100*self.noise1((x/self.size[0], y/self.size[1])) + 40*self.noise2((x, y)) + 5*self.noise3((x, y)) + 50
            h = round(self.step_factor*z)/self.step_factor
            row.append(z)
            display_row.append(h)
        return row + display_row
    #------------------------------------------------------------
    def terrain_generation(self):
        # Create the ground and ground_display matrix
        start = time.time()
        with Pool(processes=10) as pool:
            f = pool.map(self.gen_row, range(self.size[0]))
        a = np.array(f, dtype=np.float16)
        ground, ground_display = np.split(a, 2, axis=1)
        stop = time.time()
        print("World Generation Time: "+stop-start)
        return ground, ground_display
    #------------------------------------------------------------