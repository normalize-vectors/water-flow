import numpy as np
from perlin_noise import PerlinNoise
from random import seed, shuffle
import time
import multiprocessing
from multiprocessing import Pool
import pygame
seed(a=1)

def gen_row(x):
  row = []
  display_row = []
  for y in range(size[1]):
      z = 100*noise1((x/size[0], y/size[1])) + 40*noise2((x, y)) + 5*noise3((x, y)) + 50
      h = round(step_factor*z)/step_factor
      row.append(z)
      display_row.append(h)
  return row + display_row

cell_width = 2  # How many pixels wide each cell will appear
size = (1000,1000)  # Defines the shape of the board
chunk_size = 64

water = np.zeros(size, dtype=np.float16)
step_factor = 0.4

noise1 = PerlinNoise(octaves=1, seed=1)
noise2 = PerlinNoise(octaves=6, seed=1)
noise3 = PerlinNoise(octaves=16, seed=1)

start = time.time()
with Pool(processes=10) as pool:
    f = pool.map(gen_row, range(size[0]))
a = np.array(f, dtype=np.float16)
ground, ground_display = np.split(a, 2, axis=1)
stop = time.time()
del a
print(stop-start)

chunk_count = size[0]/chunk_size
print("chunk_count="+chunk_count)

def height(x, y):
  "Returns the height of the coordinate x,y. Height = height of ground + height of water"
  return ground[x][y] + water[x][y]

def adjacent_less_than(center, height):
  x, y = center
  adjacent_cells = []
  for i in range(-1, 2):
      for j in range(-1, 2):
          if i == 0 and j == 0:  # Skip the center cell
              continue
          if x + i < 0 or x + i >= size[0]: # Skip cells outside the board
              continue
          if y + j < 0 or y + j >= size[1]: # Skip cells outside the baord
              continue
          if ground[x + i][y + j] < height:
              adjacent_cells.append((x + i, y + j, ground[x + i][y + j]))
  return adjacent_cells

def water_movement(chunk):
  """Transfer water from pos to one adjacent cell. Assumes that water only 
  flows due to a difference in height. Returns the XY coordinates of cells
  that were modified."""

  # Information about the chunk that is doing the moving
  
  # get the positions for water in the chunk
  water_positions = np.where(water[chunk[0]:chunk[1]] > 0)
  # get the positions for height in the chunk
  height_positions = np.where(ground[chunk[0]:chunk[1]] > 0)
  # get the x and y positions for water in the chunk
  water_x = water_positions[0] + chunk[0]
  water_y = water_positions[1]
  # get the x and y positions for height in the chunk
  height_x = height_positions[0] + chunk[0]
  height_y = height_positions[1]
  # get the height of the water in the chunk
  center_water = height(water_x, water_y)
  # get the height of the ground in the chunk
  center_height = height(water_x, water_y)

def split_matrix(matrix, chunk_size):
    # Split the matrix into chunks of the specified size
    for i in range(0, matrix.shape[0], chunk_size):
        for j in range(0, matrix.shape[1], chunk_size):
            yield matrix[i:i+chunk_size, j:j+chunk_size]

def main():
  # Split the matrix into 64x64 chunks
  chunk_size = 64
  chunks = list(split_matrix(ground, chunk_size))

  # Create a Pool with 10 worker processes
  with multiprocessing.Pool(10) as p:
    # Apply the process_chunk function to each chunk in parallel
    processed_chunks = p.map(water_movement(), chunks)

  # make the sizes for chunks the same
  for i in range(len(processed_chunks)):
    processed_chunks[i] = np.pad(processed_chunks[i], ((0, chunk_size - processed_chunks[i].shape[0]), (0, chunk_size - processed_chunks[i].shape[1])), 'constant')

  # Concatenate the processed chunks back into a single matrix
  result = np.concatenate(processed_chunks)

  def draw_cell(coordinate):
    """Draw the cell at coordinate. Assigns a color based on presence of water and height."""

    x, y = coordinate

    # modulo color
    # make a more robust, performant, and easier to work with function to give color as a function of height

    C_GROUND = (188, 187, 171)
    C_WATER = (0, 82, 198)

    def f(h): return min((9*h/1100) + 0.02, 1)
    def g(z): return max(min((-9*z/100) + 1, 1), 0.1)

    if water[x][y] > 0:
        z = water[x][y]
        # mod = g(z)
        h = height(x, y)
        mod = 0.5*g(z) + 0.5*f(h)
        # mod = f(h)
        color = (int(C_WATER[0]*mod), int(C_WATER[1])*mod, int(C_WATER[2]*mod))
    else:
        h = ground_display[x][y]
        mod = f(h)
        color = (int(C_GROUND[0]*mod), int(C_GROUND[1]*mod), int(C_GROUND[2]*mod))

    cell_rect = (
        cell_width * x,
        cell_width * y,
        cell_width,
        cell_width
    )

    # return the rect that was drawn
    return pygame.draw.rect(screen, color, cell_rect)


  def draw_ground():
      """Draw every ground cell to the screen"""
      for x in range(size[0]):
          for y in range(size[1]):
              draw_cell((x, y))

  def update():
      """Calls water_movement and manages redrawing of water cells. Returns a list of cells that need to be redrawn."""

      def find_water():
          water_cells = []

          for x in range(size[0]):
              for y in range(size[1]):
                  z = water[x][y]
                  if z > 0:
                      water_cells.append((x, y, z))
          return water_cells

      water_cells = find_water()

      cells_to_redraw = []

      shuffle(water_cells)
      for cell in water_cells:
          cells_to_redraw += water_movement((cell[0], cell[1]))

      rects_to_update = []

      # set() returns the unique values in cells_to_redraw, so no cell should be redrawn twice
      for cell in set(cells_to_redraw):
          if cell == None:
              continue
          else:
              rects_to_update.append(draw_cell(cell))

      return rects_to_update

  def show_coordinate():
      """The mouse pointer's coordinate."""
      font = pygame.font.SysFont('Consolas', 20)
      mouse = pygame.mouse.get_pos()
      coord = (mouse[0]//cell_width, mouse[1]//cell_width)
      c = f"({coord[0]},{coord[1]})".ljust(9)
      ground = str(round(ground[coord[0]][coord[1]], 2)).ljust(6)
      water = str(round(water[coord[0]][coord[1]], 2)).ljust(6)
      height = str(round(height(coord[0], coord[1]), 2)).ljust(6)
      fps = str(round(clock.get_fps(), 1))
      string = f"{c} Gnd:{ground} Wtr:{water} Hgt:{height} Fps:{fps}"

      text = font.render(string, True, (0, 0, 0), (255, 255, 255))
      return screen.blit(text, (10, 10))

  def place_water():
      """Place down water at the mouse position"""
      mouse = pygame.mouse.get_pos()
      coord = (mouse[0]//cell_width, mouse[1]//cell_width)
      water[coord[0]][coord[1]] += 100

  # ===========================

  pygame.init()

  # Set the size of the display window
  screen = pygame.display.set_mode(
      (
          cell_width * size[0],
          cell_width * size[1]
      )
  )

  draw_ground()

  # Flip is used since it will need to update every pixel on the screen
  pygame.display.flip()

  running = True

  clock = pygame.time.Clock()

  # ===========================

  while running:
    # do stuff
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              running = False
          if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_ESCAPE:
                  running = False
          if event.type == pygame.MOUSEBUTTONDOWN:
              # if left mouse button pressed
              if event.button == 1:
                  place_water()

    #------------------------------------------------------------
      rects = update()
    #------------------------------------------------------------
      rects.append(show_coordinate())
    #------------------------------------------------------------
      clock.tick(60)
    #------------------------------------------------------------
      pygame.display.update(rects)
    #------------------------------------------------------------

if __name__ == '__main__':
  main()
  pygame.quit()