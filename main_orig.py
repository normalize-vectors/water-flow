# https://dr0id.bitbucket.io/legacy/pygame_tutorial00.html

# from terrain_generator_cython import World
from world import World
import pygame
from random import shuffle, seed

seed(a=1)
# TODO list
# better coloration
# GUI panel at top/bottom/side
# display mode that shows JUST height
# only start physics on button press
# water needs to prefer going downhill
# -- when picking which direction to go down, ideally it would pick the lowest side
# water neeeds to prefer being in groups
# investigate multithreading
# momentum
# -- complex: water could build momentum going down a hill only to splash against a wall and climb up it
# -- simple: mechanic where if a water successfully does a scenario 3, then if the next cell is shorter, then it simply
# -- teleports to that one, this would be scenario 4, ty auri :)
# better terrain generator - Specify top/bottom heights desired
# try adding diagonals to coordinates in adjacent_less_than


def main():

    def draw_cell(coordinate):

        x, y = coordinate

        # modulo color
        # make a more robust, performant, and easier to work with function to give color as a function of height

        C_GROUND = (188, 187, 171)
        C_WATER = (0, 82, 198)

        def f(h): return min((9*h/1100) + 0.02, 1)
        def g(z): return max(min((-3*z/100) + 1, 1), 0.4)

        if world.water[x][y] > 0:
            z = world.water[x][y]
            h = world.height(x, y)
            # mod = 0.5*g(z) + 0.5*f(h)
            mod = f(h)
            color = (int(C_WATER[0]*mod), int(C_WATER[1])*mod, int(C_WATER[2]*mod))
        else:
            h = world.ground_display[x][y]
            mod = f(h)
            color = (int(C_GROUND[0]*mod), int(C_GROUND[1]*mod), int(C_GROUND[2]*mod))

        cell_rect = (
            world.cell_width * x,
            world.cell_width * y,
            world.cell_width,
            world.cell_width
        )

        # return the rect that was drawn
        return pygame.draw.rect(screen, color, cell_rect)

    pygame.init()

    screen = pygame.display.set_mode(
        (
            world.cell_width * world.size[0],
            world.cell_width * world.size[1]
        )
    )

    # Draw every ground cell to the screen
    for x in range(world.size[0]):
        for y in range(world.size[1]):
            z = world.ground[x][y]

            draw_cell((x, y))

    # Flip is used since it will need to update every pixel on the screen
    pygame.display.flip()

    running = True

    clock = pygame.time.Clock()

    def show_coordinate():
        # The mouse pointer's coordinate
        font = pygame.font.Font('freesansbold.ttf', 20)
        mouse = pygame.mouse.get_pos()
        coord = (mouse[0]//world.cell_width, mouse[1]//world.cell_width)
        text = font.render(
            f"({coord[0]},{coord[1]}) Ground:{round(world.ground[coord[0]][coord[1]],2)} Water:{round(world.water[coord[0]][coord[1]],2)}",
            True,
            (0, 0, 0),
            (255, 255, 255))
        return screen.blit(text, (10, 10))

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # if left mouse button pressed
                if event.button == 1:
                    mouse = pygame.mouse.get_pos()
                    coord = (mouse[0]//world.cell_width, mouse[1]//world.cell_width)
                    world.water[coord[0]][coord[1]] += 1

        cells_to_redraw = []

        # Put code here that would change cells
        water_cells = []

        for x in range(world.size[0]):
            for y in range(world.size[1]):
                z = world.water[x][y]
                if z > 0:
                    water_cells.append((x, y, z))

        shuffle(water_cells)
        for cell in water_cells:
            cells_to_redraw += world.water_movement((cell[0], cell[1]))

        rects_to_update = []

        # Using set() means that no cell should be redrawn twice
        for cell in set(cells_to_redraw):
            if cell == None:
                continue
            else:
                rects_to_update.append(draw_cell(cell))

        print(f"{round(clock.get_fps(),1)} fps")
        clock.tick(60)

        rects_to_update.append(show_coordinate())

        # # TODO - Test what effect, if any, this has on performance
        # if len(rects_to_update) == 0:
        #     rects_to_update = None

        # Update is used since not every pixel needs to be updated,
        # only those which we have tracked
        # TODO - Test whether this is what was improving performance
        pygame.display.update(rects_to_update)


if __name__ == "__main__":
    world = World()
    main()
    pygame.quit()
