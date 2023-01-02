import numpy as np
from perlin_noise import PerlinNoise
from random import seed, shuffle
import time
from multiprocessing import *
seed(a=1)

class World:
    def __init__(self):
        self.cell_width = 6  # How many pixels wide each cell will appear
        self.size = (100,100)  # Defines the shape of the board
        self.chunk_size = 64

        self.water = np.zeros(self.size, dtype=np.float16)
        self.step_factor = 0.4

        self.noise1 = PerlinNoise(octaves=1, seed=1)
        self.noise2 = PerlinNoise(octaves=6, seed=1)
        self.noise3 = PerlinNoise(octaves=16, seed=1)

        start = time.time()
        with Pool(processes=10) as pool:
            f = pool.map(self.gen_row, range(self.size[0]))
        a = np.array(f, dtype=np.float16)
        self.ground, self.ground_display = np.split(a, 2, axis=1)
        stop = time.time()
        del a
        print(stop-start)

        self.chunk_count = self.size/self.chunk_size

    def gen_row(self, x):
        row = []
        display_row = []
        for y in range(self.size[1]):
            z = 100*self.noise1((x/self.size[0], y/self.size[1])) + 40*self.noise2((x, y)) + 5*self.noise3((x, y)) + 50
            h = round(self.step_factor*z)/self.step_factor
            row.append(z)
            display_row.append(h)
        return row + display_row

    def height(self, x, y):
        """Returns the height of the coordinate x,y. Height = height of ground + height of water"""
        return self.ground[x][y] + self.water[x][y]

    def adjacent_less_than(self, center, height):
        x, y = center
        adjacent_cells = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:  # Skip the center cell
                    continue
                if x + i < 0 or x + i >= self.size[0]: # Skip cells outside the board
                    continue
                if y + j < 0 or y + j >= self.size[1]: # Skip cells outside the baord
                    continue
                if self.ground[x + i][y + j] < height:
                    adjacent_cells.append((x + i, y + j, self.ground[x + i][y + j]))
        return adjacent_cells

    def water_movement(self, pos):
        """Transfer water from pos to one adjacent cell. Assumes that water only 
        flows due to a difference in height. Returns the XY coordinates of cells
        that were modified."""

        # TODO - "surface tension" - don't allow water to flow into a cell if the amount is
        # < some small number
        # and/or
        # TODO - make flow be based on a base constant, i.e. at least 1 water must flow,
        # in addition to the xfer coefficient

        # TODO water selects adjacent to flow into by which has lowest height

        # Information about the cell of water that is doing the moving
        x, y = pos
        center_height = self.height(x, y)
        center_ground = self.ground[x][y]
        center_water = self.water[x][y]

        # cohesion_threshold = 0.1
        # Stop water from moving if it is too small of a pixel
        # if cohesion_threshold > center_water:
        #     return [None]

        # A list of XYZ that water will flow to
        adjacent_cells = self.adjacent_less_than((x, y), center_height)

        # End this function call if there are no viable adjacent cells
        if len(adjacent_cells) == 0:
            return [None]

        shuffle(adjacent_cells)

        adjacent = adjacent_cells[0]

        # Difference in height between the center cell and the adjacent
        delta = center_height - adjacent[2]

        xfer_coefficient = 0.8
        cohesion_constant = 0.01

        if center_ground > adjacent[2]:
            max_water_xfer = center_water
            if delta > max_water_xfer:  # Scenario 3

                if max_water_xfer < cohesion_constant:
                    xfer = max_water_xfer
                    self.water[x][y] = 0
                    self.water[adjacent[0]][adjacent[1]] += xfer
                    # TODO remove x,y from water_cells
                else:
                    xfer = max_water_xfer*xfer_coefficient
                    self.water[x][y] -= xfer
                    self.water[adjacent[0]][adjacent[1]] += xfer

                return [pos, (adjacent[0], adjacent[1])]

        # Otherwise, water should be balanced between the 2 cells
        average_height = (center_height+adjacent[2])/2

        # This is the amount of water that will be necessary to give the two cells the same height
        water_xfer_to_balance = average_height - adjacent[2]

        # Water transfer for situations 1 & 2
        self.water[x][y] -= water_xfer_to_balance
        self.water[adjacent[0]][adjacent[1]] += water_xfer_to_balance

        # TODO add adjacent to water_cells

        # Return XY's of effected cells
        return [pos, (adjacent[0], adjacent[1])]

if __name__ == "__main__":
    world = World()
    print(world.chunks(world.ground, 10))