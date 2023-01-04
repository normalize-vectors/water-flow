import numpy as np
from perlin_noise import PerlinNoise
from random import seed, randrange
from multiprocessing import Pool
import chunk

seed(a=1)
class World:
    def __init__(self, size):
        self.size = size  # Defines the shape of the board

        self.water = np.zeros(self.size, dtype=np.float16)

        self.step_factor = 0.4  # Determines how the ground_display matrix is rounded

        # Noise objects used for world generation
        self.noise1 = PerlinNoise(1, 71)
        self.noise2 = PerlinNoise(8, 81)
        self.noise3 = PerlinNoise(24, 91)

        self.terrain_generation()  # Creates and populates self.ground and self.ground_display

        # Dictionaries of color values populated by main
        self.ground_color = {}
        self.water_color = {}

        self.water_cells = set()

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

        self.matrix = self.ground

    def height(self, x, y):
        """Returns the height of the coordinate x,y. Height = height of ground + height of water"""
        return self.ground[x, y] + self.water[x, y]

    def adjacent_less_than(self, pos, reference_height):
        """Returns all cells adjacent to pos that are shorter than reference height."""

        x, y = pos

        coordinates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        to_return = []
        for coord in coordinates:
            X, Y = coord
            # Check if the coordinate of interest is inside the grid
            if (0 <= X <= self.size[0]-1) and (0 <= Y <= self.size[0]-1):
                height = self.height(X, Y)

                # Don't return this XYZ if
                if height >= reference_height:
                    continue

                to_return.append((X, Y, height))
        return to_return

    def find_water(self):
        """Returns a list of every water pixel on the map. Slow."""
        return np.argwhere(self.water)

    def water_movement(self, pos):
        """Transfer water from pos to one adjacent cell. Assumes that water only
        flows due to a difference in height. Returns the XY coordinates of cells
        that were modified."""

        # TODO water selects adjacent to flow into by which has lowest height

        # Information about the cell of water that is doing the moving
        x, y = pos
        center_height = self.height(x, y)
        center_ground = self.ground[x, y]
        center_water = self.water[x, y]

        # A list of XYZ that water will flow to
        adjacent_cells = self.adjacent_less_than((x, y), center_height)

        # End this function call if there are no viable adjacent cells
        l = len(adjacent_cells)
        if l == 0:
            return [None]

        adjacent = adjacent_cells[randrange(l)]

        # Difference in height between the center cell and the adjacent
        delta = center_height - adjacent[2]

        xfer_coefficient = 0.8

        # If the amount of water that would be left behind is smaller than this, then all water will be moved
        cohesion_constant = 0.01

        def cohesive_xfer(xfer):
            self.water[x, y] = 0
            self.water_cells.remove((x, y))
            self.water[adjacent[0], adjacent[1]] += xfer

        def scenario_1_2():
            # Handles resolution of scenarios 1 and 2

            average_height = (center_height+adjacent[2])/2

            # This is the amount of water that will be necessary to give the two cells the same height
            xfer_to_balance = average_height - adjacent[2]

            self.water[x, y] -= xfer_to_balance
            self.water[adjacent[0], adjacent[1]] += xfer_to_balance

            # This is a deprecated implementation of cohesive_xfer for scenarios 1 and 2
            # It is interesting, but not very water like. Makes the water too cohesive to be water
            # if water_xfer_to_balance < cohesion_constant:
            #     cohesive_xfer(center_water)
            # else:
            #     self.water[x][y] -= water_xfer_to_balance
            #     self.water[adjacent[0]][adjacent[1]] += water_xfer_to_balance

        def scenario_3():
            # Handles resolution of scenario 3
            if max_water_xfer < cohesion_constant:
                xfer = max_water_xfer
                cohesive_xfer(xfer)
            else:
                xfer = max_water_xfer*xfer_coefficient
                self.water[x, y] -= xfer
                self.water[adjacent[0], adjacent[1]] += xfer

        if center_ground >= adjacent[2]:
            max_water_xfer = center_water
            if delta >= max_water_xfer:  # Scenario 3
                scenario_3()
            else:
                scenario_1_2()  # Scenario 2
        else:
            scenario_1_2()  # Scenario 1

        # Add the adjacent cell to the list of water_cells if it has water.
        # This must be done at the very end, since it is possible for no water to be xfer'd under certain conditions.
        if self.water[adjacent[0], adjacent[1]] != 0:
            self.water_cells.add((adjacent[0], adjacent[1]))

        # Return XY's of effected cells
        return [pos, (adjacent[0], adjacent[1])]

if __name__ == "__main__":
    world = World((1024,1024))
