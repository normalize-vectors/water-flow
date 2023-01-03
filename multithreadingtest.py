import numpy as np
from perlin_noise import PerlinNoise
from random import seed, shuffle
import time
import multiprocessing
from multiprocessing import Pool
import pygame
from multithreadingtest_2 import World
seed(a=1)

def main():
  #region TERRAIN GENERATION - STEP 0
  #------------------------------------------------------------
  ground, ground_display = world.terrain_generation()
  #------------------------------------------------------------
  #endregion

  #region CHUNK SPLITTING - STEP 1
  #------------------------------------------------------------
  "SPLITTING THE MATRIX INTO CHUNKS"
  def split_matrix(matrix, chunk_size):
    chunks = []
    for x in range(0, matrix.shape[0], chunk_size):
        for y in range(0, matrix.shape[1], chunk_size):
            chunks.append(matrix[x:x+chunk_size, y:y+chunk_size])
    return chunks
  #------------------------------------------------------------
  #endregion
  chunks = split_matrix(ground, world.chunk_size)
  print(chunks)

if __name__ == '__main__':
  world = World()
  main()
  pygame.quit()