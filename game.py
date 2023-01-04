"""
TODO list
display mode that shows JUST height
only start physics on button press
water needs to prefer going downhill
-- when picking which direction to go down, ideally it would pick the lowest side
momentum
-- complex: water could build momentum going down a hill only to splash against a wall and climb up it
-- simple: mechanic where if a water successfully does a scenario 3, then if the next cell is shorter, then it simply
-- teleports to that one, this would be scenario 4, ty auri :)
better terrain generator - Specify top/bottom heights desired
try adding diagonals to coordinates in adjacent_less_than
in world.py, try moving scenario functions outside of water_movement
---- Each time it runs, it has to remind itself that those functions exist, surely that's a (minor) performance loss?
is there a numpy way to make adjacent_less_than faster? optimize it in general?
potential cheat to improve performance: update 1/2 of water cells per frame
xfer coefficient dependent on delta? Water would slow faster down a larger slope...?
Is there a more efficient array type than numpy? Accesing them seems to be taking a lot of time
Colors seem off
If a water cell couldn't move this frame, add it to a list so that it won't try to mvoe next frame, either
"""
from world import World
from chunk import Chunking
import arcade
from interpolate import Interpolate
from multiprocessing import Pool
import numpy as np

# Constants ----------------------------------------------------------

# Cells:
GRID_WIDTH = 64
GRID_HEIGHT = 64
CELL_WIDTH = 5
CELL_HEIGHT = 5
CELL_MARGIN = 0

# Screen:
TOP_MARGIN = 40
SCREEN_WIDTH = (CELL_WIDTH + CELL_MARGIN) * GRID_WIDTH
SCREEN_HEIGHT = (CELL_HEIGHT + CELL_MARGIN) * GRID_HEIGHT + TOP_MARGIN
SCREEN_TITLE = "Water Flow"

#---------------------------------------------------------------------
class Color_Mapper():
    """
    Holds functions for calculating color of a cell as a function of height.
    Records each color calculated in a dictionary so that it will not need to be calculated again.
    """

    def __init__(self):
        # Find the min and max height of the world for color interpolation.
        self.height_min = world.ground_display.min()*0.8
        self.height_max = world.ground_display.max()*1.2

        # Value for RGB of highest/lowest ground point on the map
        # Only built for greyscale ground.
        self.ground_color_max = (255, 255, 255)
        self.ground_color_min = (40, 40, 40)

        self.__ground__ = Interpolate(
            x2=self.height_max,
            x1=self.height_min,
            y2=self.ground_color_max[0],
            y1=self.ground_color_min[0]
        )

        self.water_color_max = (18, 100, 158)
        self.water_color_min = (63, 172, 255)

        self.__water_R__ = Interpolate(
            x2=30,
            x1=0,
            y2=self.water_color_max[0],
            y1=self.water_color_min[0]
        )

        self.__water_G__ = Interpolate(
            x2=30,
            x1=0,
            y2=self.water_color_max[1],
            y1=self.water_color_min[1]
        )

        self.__water_B__ = Interpolate(
            x2=30,
            x1=0,
            y2=self.water_color_max[2],
            y1=self.water_color_min[2]
        )

        # Dictionaries of color values as a function of heights
        self.ground_dict = dict()
        self.water_dict = dict()

    def ground(self, h):
        """Returns the RGB value for a ground cell with height h."""

        if h in self.ground_dict.keys():
            return self.ground_dict[h]
        else:
            r = int(self.__ground__(h))
            self.ground_dict[h] = (r, r, r)
            return (r, r, r)

    def water(self, z):
        """Returns the RGB value for a water cell with height h."""
        h = int(z)
        if h in self.water_dict.keys():
            return self.water_dict[h]
        else:
            r = int(self.__water_R__(h))
            g = int(self.__water_G__(h))
            b = int(self.__water_B__(h))
            self.water_dict[h] = (r, g, b)
            return (r, g, b)
class Cell(arcade.SpriteSolidColor):
    "Object used to represent each grid cell. Extended from arcade.SpriteSolidColor."
    # Attributes:
    def __init__(self, width: int, height: int, color: arcade.Color, grid_x: int, grid_y: int):
        super().__init__(width, height, color)

        # Position of the cell within the grid.
        self.grid_x = grid_x
        self.grid_y = grid_y

        # The color the cell should revert to when water is not present.
        # Should be a value from world.ground_display
        self.ground_color = color

    def update(self):
        """
        Update the color of the sprite based on the world matrices.
        """
        z = world.water[self.grid_x, self.grid_y]
        if z == 0:
            # This cell has no water.
            self.color = self.ground_color
        else:
            # This cell has water on it.
            self.color = color_mapper.water(z)
class Game(arcade.Window):
    "Main application class."
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Controls stuff
        self.left_click = False
        self.mouse_x = 0
        self.mouse_y = 0

    arcade.enable_timings()

    def setup(self):
        "Set up the game variables. Call to re-start the game."

        # split the world matrix into chunks using chunk.py
        Matrix = world.water

        self.sub_matrices = chunking.split(np.array(Matrix), chunking.sub_matrix_row, chunking.sub_matrix_col)

        # Create your sprites and sprite lists here

        # One dimensional list of all sprites in the two-dimensional sprite list
        self.grid_sprite_list = arcade.SpriteList()

        # This will be a two-dimensional grid of sprites to mirror the two
        # dimensional grid of numbers. This points to the SAME sprites that are
        # in grid_sprite_list, just in a 2d manner.
        self.grid_sprites = []

        # Create a list of solid-color sprites to represent each grid location
        for grid_x in range(GRID_WIDTH):
            self.grid_sprites.append([])
            for grid_y in range(GRID_HEIGHT):
                z = world.ground_display[grid_x, grid_y]
                init_color = color_mapper.ground(z)
                sprite = Cell(
                    CELL_WIDTH,
                    CELL_HEIGHT,
                    init_color,
                    grid_x,
                    grid_y
                )
                sprite.center_x = grid_x * (CELL_WIDTH + CELL_MARGIN) + (CELL_WIDTH / 2 + CELL_MARGIN)
                sprite.center_y = grid_y * (CELL_HEIGHT + CELL_MARGIN) + (CELL_HEIGHT / 2 + CELL_MARGIN)
                self.grid_sprite_list.append(sprite)
                self.grid_sprites[grid_x].append(sprite)

        self.grid_sprite_list.update()

        self.hud_text = arcade.Text(
            text="",
            start_x=5,
            start_y=SCREEN_HEIGHT - TOP_MARGIN + 10,
            color=color_mapper.ground_color_max,
            font_size=20
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # Always start by clearing the window pixels
        self.clear()

        self.grid_sprite_list.draw()

        # Draw hud text displaying information
        self.hud_text.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        xy_to_update = []

        """Player input stuff"""
        if self.left_click:
            world.water[self.mouse_x, self.mouse_y] += 20
            world.water_cells.add((self.mouse_x, self.mouse_y))
            xy_to_update.append((self.mouse_x, self.mouse_y))

        """Water update stuff"""

        """for cell in world.water_cells.copy():
            xy_to_update += world.water_movement((cell[0], cell[1]))"""

        # call water_movement() for all water, multiprocess for every chunk
        with Pool() as p:
            # for every chunk, run water_movement() for every cell
            for x in range(len(self.sub_matrices)):
                for y in range(len(self.sub_matrices[x])):
                    for cell in self.sub_matrices[x][y]:
                        # run water_movement() for every chunk
                        matrixes = p.apply_async(world.water_movement(cell[x]),(cell[y]))

        Matrix = chunking.combine(matrixes, chunking.sub_matrix_row, chunking.sub_matrix_col)

        xy_to_update += Matrix

        for pos in xy_to_update:
            if pos == None:
                continue
            else:
                sprite = self.grid_sprites[pos[0]][pos[1]]
                sprite.update()

        """UI Stuff"""

        # HUD
        c = (self.mouse_x, self.mouse_y)
        ground = str(round(world.ground[self.mouse_x, self.mouse_y], 2)).ljust(6)
        water = str(round(world.water[self.mouse_x, self.mouse_y], 2)).ljust(6)
        height = str(round(world.height(self.mouse_x, self.mouse_y), 2)).ljust(6)
        fps = str(round(arcade.get_fps(), 1))
        self.hud_text.text = f"{c} Gnd:{ground} Wtr:{water} Hgt:{height} Fps:{fps}"

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        match key:
            case 32:  # Spacebar
                world.__init__((GRID_WIDTH, GRID_HEIGHT))
                self.setup()  # Reset the game
            case 65307:  # Escape
                arcade.close_window()  # Close the game

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        self.mouse_x = min(max(x//CELL_WIDTH, 0), GRID_WIDTH-1)
        self.mouse_y = min(max(y//CELL_HEIGHT, 0), GRID_WIDTH-1)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        if button == 1:
            self.left_click = True

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        if button == 1:
            self.left_click = False

if __name__ == "__main__":
    world = World((GRID_WIDTH, GRID_HEIGHT))
    chunking = Chunking(world,(world.size[0],world.size[1]),(16,16))
    color_mapper = Color_Mapper()
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()
    arcade.close_window()
