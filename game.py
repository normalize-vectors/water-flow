"""
TODO list
1. Water should be able to move diagonally
2. Water should flow to the shortest of the adjacent cells
3. Erosion
4. Improve performance

1 & 2 can be implemented together. Could be done by replacing world.adjacent_less_than() with a
Numba vectorized ufunc that is given the 3x3 slice of the world.water array centered around

3 would likely be just as costly to performance as world.water_movement is, optimization necessary

4 is tricky. Potential options:
    - Multiprocessing
    - Only process half of water cells every frame (lame)
    - Rewrite parts of code to utilize Numba
    - Rewrite parts of code to utilize Cython
    - Rewrite world.water_movement() in C++, import using Pybind11 or Boost.Python
    - Rewrite entirely in C++
"""
from world import World
import arcade
from interpolate import Interpolate


GRID_WIDTH = 120
GRID_HEIGHT = 120
CELL_WIDTH = 5
CELL_HEIGHT = 5
CELL_MARGIN = 0

TOP_MARGIN = 30
SCREEN_WIDTH = (CELL_WIDTH + CELL_MARGIN) * GRID_WIDTH
SCREEN_HEIGHT = (CELL_HEIGHT + CELL_MARGIN) * GRID_HEIGHT + TOP_MARGIN
SCREEN_TITLE = "Water Flow"


class Color_Mapper():
    """
    Holds functions for calculating color of a cell as a function of height.
    Records each color calculated in a dictionary so that it will not need to be calculated again.
    """

    def __init__(self):
        # Find the min and max height of the world for color interpolation.
        self.height_min = world.ground_display.min()
        self.height_max = world.ground_display.max()

        # RGB value of highest (max) and lowest (min) ground point on the map
        self.ground_color_max = (239, 215, 203)  # (255, 255, 255)
        self.ground_color_min = (61, 55, 52)  # (40, 40, 40)

        # RGB value of highest (max) and lowest (min) water point on the map
        self.water_color_max = (18, 100, 158)
        self.water_color_min = (63, 172, 255)

        # Greycale colors for height display mode
        self.height_color_max = 255
        self.height_color_min = 0

        # Enable or disable height display mode
        self.height_display = False

        # Interpolation objects that will be used to interpolate the ground and water colors
        self.__ground_R__ = Interpolate(
            x2=self.height_max,
            x1=self.height_min,
            y2=self.ground_color_max[0],
            y1=self.ground_color_min[0]
        )

        self.__ground_G__ = Interpolate(
            x2=self.height_max,
            x1=self.height_min,
            y2=self.ground_color_max[1],
            y1=self.ground_color_min[1]
        )

        self.__ground_B__ = Interpolate(
            x2=self.height_max,
            x1=self.height_min,
            y2=self.ground_color_max[2],
            y1=self.ground_color_min[2]
        )

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

        self.__height__ = Interpolate(
            x2=30,
            x1=0,
            y2=self.height_color_max,
            y1=self.height_color_min
        )

        # Dictionaries of color values as a function of height
        self.ground_dict = dict()
        self.water_dict = dict()
        self.height_dict = dict()

    def ground(self, h):
        """Returns the RGB value for a ground cell with height h."""

        if h in self.ground_dict.keys():
            return self.ground_dict[h]
        else:
            r = int(self.__ground_R__(h))
            g = int(self.__ground_G__(h))
            b = int(self.__ground_B__(h))
            self.ground_dict[h] = (r, g, b)
            return (r, g, b)

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

    def height(self, z):
        """Returns the greyscale color value for any cell with height h."""
        h = int(z)
        if h in self.height_dict.keys():
            return self.height_dict[h]
        else:
            r = int(self.__height__(h))
            self.height_dict[h] = (r, r, r)
            return (r, r, r)


class Cell(arcade.SpriteSolidColor):
    """
    Object used to represent each grid cell. Extended from arcade.SpriteSolidColor.

    """

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
        # Heightmap display mode
        if color_mapper.height_display:
            z = world.height(self.grid_x, self.grid_y)
            self.color = color_mapper.height(z)

        # Regular display mode
        else:
            z = world.water[self.grid_x, self.grid_y]
            if z == 0:
                # This cell has no water.
                self.color = self.ground_color
            else:
                # This cell has water on it.
                self.color = color_mapper.water(z)


class Game(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Control variables
        self.left_click = False
        self.mouse_x = 0
        self.mouse_y = 0

    arcade.enable_timings()

    def setup(self):
        """
        Set up the game variables. Call to re-start the game.
        """

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
            font_size=14,
            font_name='Consolas'
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

        for cell in world.water_cells.copy():
            xy_to_update += world.water_movement((cell[0], cell[1]))

        for pos in xy_to_update:
            if pos == None:
                continue
            else:
                sprite = self.grid_sprites[pos[0]][pos[1]]
                sprite.update()

        """UI Stuff"""

        c = str((self.mouse_x, self.mouse_y)).ljust(10)
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
                world.__init__((GRID_WIDTH, GRID_HEIGHT))  # Regenerate the world
                color_mapper.__init__()  # Reset the colors
                self.setup()  # Reset the game
            case 65307:  # Escape
                arcade.close_window()  # Close the game
            case 65507:  # left control
                # Toggle the height_display mode
                color_mapper.height_display = not color_mapper.height_display
                self.grid_sprite_list.update()  # Update color of all sprites

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
    color_mapper = Color_Mapper()
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()
    arcade.close_window()
