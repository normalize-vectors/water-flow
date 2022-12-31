# https://dr0id.bitbucket.io/legacy/pygame_tutorial00.html

from terrain_2 import terrain, terrain_shape
import pygame
import numpy as np
from random import choice, randint


class World:
    def __init__(self):
        self.cell_width = 3
        self.size = terrain_shape
        self.terrain = terrain

        # generate 2d matrices representing the heights of ground, and water
        self.ground = np.empty(
            (self.size[0], self.size[1]), dtype=int)
        self.water = np.empty(
            (self.size[0], self.size[1]), dtype=int)

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.ground[x][y] = list(terrain[x][y]).count("1")
                self.water[x][y] = list(terrain[x][y]).count("2")


def noise():
    x = randint(0, world.size[0]-1)
    y = randint(0, world.size[1]-1)
    z = world.ground[x][y]

    Z = z + choice([1, -1])

    if Z < 10 and Z > 0:
        world.ground[x][y] = Z

    return (x, y, Z)


def main():

    def draw_cell(coordinate):
        x, y, z = coordinate

        color = (int(26*(1-0.08*z)),
                 int(114*(1-0.08*z)), int(52*(1-0.08*z)))

        cell_rect = (
            world.cell_width * x,
            world.cell_width * y,
            world.cell_width,
            world.cell_width
        )

        return pygame.draw.rect(screen, color, cell_rect)

    pygame.init()

    screen = pygame.display.set_mode(
        (
            world.cell_width * world.size[0],
            world.cell_width * world.size[1]
        )
    )

    # draw terrain
    for x in range(world.size[0]):
        for y in range(world.size[1]):
            z = world.ground[x][y]

            draw_cell((x, y, z))

    pygame.display.flip()

    running = True

    clock = pygame.time.Clock()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        cells_to_update = []

        # for i in range(2000):
        #     cells_to_update.append(noise())

        rects_to_update = []

        for cell in cells_to_update:
            rects_to_update.append(draw_cell(cell))

        print(f"{clock.get_fps()}")
        clock.tick(240)

        if len(rects_to_update) == 0:
            rects_to_update = None

        pygame.display.update(rects_to_update)


if __name__ == "__main__":
    world = World()
    main()
    pygame.quit()
