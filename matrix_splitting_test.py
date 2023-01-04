import numpy as np
from perlin_noise import PerlinNoise
from random import seed, randrange
from multiprocessing import Pool

# values
sub_matrix_row = 4
sub_matrix_col = 4
original_matrix_row = 1024
original_matrix_col = 1024

# disable ommiting values
np.set_printoptions(threshold=np.inf)

# create a matrix of size 1024
matrix = np.zeros((original_matrix_row, original_matrix_col), dtype=np.float16)

def split(array, nrows, ncols):
    "Split a matrix into sub-matrices."
    r, h = array.shape
    # the int(h) will be 12, for example, because it returns the rows of the array (which is 12,12)
    # the int(r) will be 12, for example, because it returns the cols of the array (which is 12,12)
    x = array.reshape(h//nrows, nrows, -1, ncols)
    y = x.swapaxes(1, 2)
    z = y.reshape(-1, nrows, ncols)
    return z

# split() in reverse
def combine(array, nrows, ncols):
    "Combine sub-matrices into a matrix."
    # turn list into array
    array = np.array(array)
    chunk_count, chunk_rows, chunk_cols = array.shape
    # for example: if array is 12 and split into 4,4 chunks, there will be 9 chunks generated
    # chunk rows will be 12, because it returns the arrays (which is 12,12) rows.
    # chunk cols will be 12, because it returns the arrays (which is 12,12) cols.
    z = array
    y = z.reshape(original_matrix_row//chunk_rows, original_matrix_col//chunk_cols, nrows, ncols)
    x = y.swapaxes(1,2)
    to_return = x.reshape(original_matrix_row, original_matrix_col)
    return to_return

def do_something(matrix):
    return matrix

def main():
    Matrix = matrix
    # split the matrix into sub-matrices
    sub_matrices = split(np.array(Matrix), sub_matrix_row, sub_matrix_col)
    # give the matrixes their own processes
    with Pool() as p:
        # run the function on each matrix
        matrixes = p.map(do_something, sub_matrices)
    # combine the matrixes into the original shape of the matrix

    Matrix = combine(matrixes, sub_matrix_row, sub_matrix_col)
    print(Matrix)

if __name__ == "__main__":
    main()