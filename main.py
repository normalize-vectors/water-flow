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
# --- multithreading with NumPy: page 1880 https://numpy.org/doc/1.23/numpy-ref.pdf
# momentum
# -- complex: water could build momentum going down a hill only to splash against a wall and climb up it
# -- simple: mechanic where if a water successfully does a scenario 3, then if the next cell is shorter, then it simply
# -- teleports to that one, this would be scenario 4, ty auri :)
# better terrain generator - Specify top/bottom heights desired
# try adding diagonals to coordinates in adjacent_less_than
# in world.py, try moving scenario functions outside of water_movement
# ---- Each time it runs, it has to remind itself that those functions exist, surely that's a (minor) performance loss?
# is there a numpy way to make adjacent_less_than faster? optimize it in general?


def main():

    def draw_cell(coordinate):
        """Draw the cell at coordinate. Assigns a color based on presence of water and height."""

        x, y = coordinate

        # modulo color
        # make a more robust, performant, and easier to work with function to give color as a function of height

        C_GROUND = (188, 187, 171)
        C_WATER = (0, 82, 198)

        def f(h): return min((9*h/1100) + 0.02, 1)
        def g(z): return max(min((-9*z/100) + 1, 1), 0.1)

        if world.water[x][y] > 0:
            z = world.water[x][y]
            # mod = g(z)
            h = world.height(x, y)
            mod = 0.5*g(z) + 0.5*f(h)
            # mod = f(h)
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

    def draw_ground():
        """Draw every ground cell to the screen"""
        for x in range(world.size[0]):
            for y in range(world.size[1]):

                draw_cell((x, y))

    def update():
        """Calls water_movement and manages redrawing of water cells. Returns a list of cells that need to be redrawn."""

        cells_to_redraw = []

        for cell in world.water_cells.copy():
            cells_to_redraw += world.water_movement((cell[0], cell[1]))

        rects_to_update = []

        for cell in cells_to_redraw:
            if cell == None:
                continue
            else:
                rects_to_update.append(draw_cell(cell))

        return rects_to_update

    def show_coordinate():
        """The mouse pointer's coordinate."""
        font = pygame.font.SysFont('Consolas', 20)
        mouse = pygame.mouse.get_pos()
        coord = (mouse[0]//world.cell_width, mouse[1]//world.cell_width)
        c = f"({coord[0]},{coord[1]})".ljust(9)
        ground = str(round(world.ground[coord[0]][coord[1]], 2)).ljust(6)
        water = str(round(world.water[coord[0]][coord[1]], 2)).ljust(6)
        height = str(round(world.height(coord[0], coord[1]), 2)).ljust(6)
        fps = str(round(clock.get_fps(), 1))
        string = f"{c} Gnd:{ground} Wtr:{water} Hgt:{height} Fps:{fps}"

        text = font.render(string, True, (0, 0, 0), (255, 255, 255))
        return screen.blit(text, (10, 10))

    def place_water():
        """Place down water at the mouse position"""
        mouse = pygame.mouse.get_pos()
        coord = (mouse[0]//world.cell_width, mouse[1]//world.cell_width)
        world.water[coord[0]][coord[1]] += 1
        if coord not in world.water_cells:
            world.water_cells.add(coord)

    # ===========================

    pygame.init()

    # Set the size of the display window
    screen = pygame.display.set_mode(
        (
            world.cell_width * world.size[0],
            world.cell_width * world.size[1]
        )
    )

    draw_ground()

    # Flip is used since it will need to update every pixel on the screen
    pygame.display.flip()

    running = True

    clock = pygame.time.Clock()

    frame_count = 0

    # ===========================

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LCTRL:
                    breakpoint()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # if left mouse button pressed
                if event.button == 1:
                    place_water()

        rects = update()

        # if set(world.find_water()) != world.water_cells:
        #     breakpoint()

        rects.append(show_coordinate())

        clock.tick(60)

        # # TODO - Test what effect, if any, this has on performance
        # if len(rects_to_update) == 0:
        #     rects_to_update = None

        # Update is used since not every pixel needs to be updated,
        # only those which we have tracked
        # TODO - Test whether this is what was improving performance
        pygame.display.update(rects)

        frame_count += 1


if __name__ == "__main__":
    world = World()
    main()
    pygame.quit()
