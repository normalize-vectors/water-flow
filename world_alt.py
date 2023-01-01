import numpy as np
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt
from random import seed, shuffle

seed(a=1)


class World:

    def __init__(self):
        self.cell_width = 6  # How many pixels wide each cell will appear
        self.size = (150, 150)  # Defines the shape of the board

        self.ground = np.empty(self.size, dtype=np.float16)
        self.ground_display = np.empty(self.size, dtype=np.float16)
        self.water = np.zeros(self.size, dtype=np.float16)

        noise1 = PerlinNoise(octaves=2, seed=69)
        noise2 = PerlinNoise(octaves=8, seed=420)
        noise3 = PerlinNoise(octaves=16, seed=46)
        noise4 = PerlinNoise(octaves=32, seed=62)

        step_factor = 0.4

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                noise_coordinate = [x/self.size[0], y/self.size[1]]

                self.ground[x][y] = 100*noise1(noise_coordinate)
                self.ground[x][y] += 20*noise2(noise_coordinate)
                self.ground[x][y] += 5*noise3(noise_coordinate)
                self.ground[x][y] += 2*noise4(noise_coordinate)
                # self.ground[x][y] = round(step_factor*self.ground[x][y])/step_factor
                self.ground_display[x][y] = round(step_factor*self.ground[x][y])/step_factor

        # Assure that there are only positive values in self.ground
        self.ground += abs(self.ground.min())*1.5
        # TODO this is inefficient, redo after color stuff is better
        self.ground_display += abs(self.ground_display.min())*1.5

    def height(self, x, y):
        """Returns the height of the coordinate x,y. Height = height of ground + height of water"""
        return self.ground[x][y] + self.water[x][y]

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
        """Returns a list of every water pixel on the map. Very slow."""

        return np.argwhere(world.water)

    def water_movement(self, pos):
        """Transfer water from pos to one adjacent cell. Assumes that water only 
        flows due to a difference in height. Returns the XY coordinates of cells
        that were modified."""

        # TODO water selects adjacent to flow into by which has lowest height

        # Information about the cell of water that is doing the moving
        x, y = pos
        center_height = self.height(x, y)
        center_ground = self.ground[x][y]
        center_water = self.water[x][y]

        self.i += 1  # Debug

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

        # If the amount of water that would be left behind is smaller than this, then all water will be moved
        cohesion_constant = 0.01

        def cohesive_xfer(xfer):
            self.water[x][y] = 0
            self.water[adjacent[0]][adjacent[1]] += xfer

        def scenario_1_2():
            # Handles resolution of scenarios 1 and 2

            average_height = (center_height+adjacent[2])/2

            # This is the amount of water that will be necessary to give the two cells the same height
            xfer_to_balance = average_height - adjacent[2]

            self.water[x][y] -= xfer_to_balance
            self.water[adjacent[0]][adjacent[1]] += xfer_to_balance

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
                self.water[x][y] -= xfer
                self.water[adjacent[0]][adjacent[1]] += xfer

        if center_ground >= adjacent[2]:
            max_water_xfer = center_water
            if delta >= max_water_xfer:  # Scenario 3
                scenario_3()
            else:
                scenario_1_2()  # Scenario 2
        else:
            scenario_1_2()  # Scenario 1

        # Return XY's of effected cells
        return [pos, (adjacent[0], adjacent[1])]


if __name__ == "__main__":
    world = World()
