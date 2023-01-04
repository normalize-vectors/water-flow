import numpy as np
from perlin_noise import PerlinNoise
from random import seed, randrange
from multiprocessing import Pool

class Chunking():
    def __init__(self, matrix, matrix_size, sub_matrix_size):
        self.matrix = matrix
        self.sub_matrix_row = sub_matrix_size[0]
        self.sub_matrix_col = sub_matrix_size[1]
        self.original_matrix_row = matrix_size[0]
        self.original_matrix_col = matrix_size[1]

    def split(self, array, nrows, ncols):
        "Split a matrix into sub-matrices."
        r, h = array.shape
        # the int(h) will be 12, for example, because it returns the rows of the array (which is 12,12)
        # the int(r) will be 12, for example, because it returns the cols of the array (which is 12,12)
        x = array.reshape(h//nrows, nrows, -1, ncols)
        y = x.swapaxes(1, 2)
        z = y.reshape(-1, nrows, ncols)
        return z

    def combine(self, array, nrows, ncols):
        "Combine sub-matrices into a matrix."
        # turn list into array
        array = np.array(array)
        chunk_count, chunk_rows, chunk_cols = array.shape
        # for example: if array is 12 and split into 4,4 chunks, there will be 9 chunks generated
        # chunk rows will be 12, because it returns the arrays (which is 12,12) rows.
        # chunk cols will be 12, because it returns the arrays (which is 12,12) cols.
        z = array
        y = z.reshape(self.original_matrix_row//chunk_rows, self.original_matrix_col//chunk_cols, nrows, ncols)
        x = y.swapaxes(1,2)
        to_return = x.reshape(self.original_matrix_row, self.original_matrix_col)
        return to_return

    def do_something(self, matrix):
        # do something to the matrix
        return matrix

    def main(self):
        Matrix = self.matrix
        # split the matrix into sub-matrices
        sub_matrices = self.split(np.array(Matrix), self.sub_matrix_row, self.sub_matrix_col)
        # give the matrixes their own processes
        with Pool() as p:
            # run the function on each matrix
            matrixes = p.map(self.do_something, sub_matrices)
        # combine the matrixes into the original shape of the matrix
        Matrix = self.combine(matrixes, self.sub_matrix_row, self.sub_matrix_col)

if __name__ == "__main__":
    # create a matrix of random numbers
    Matrix = np.random.randint(0, 255, (1024,1024))
    # create a chunk object
    chunk = Chunking(Matrix, (12,12), (4,4))
    # run the main function
    chunk.main()