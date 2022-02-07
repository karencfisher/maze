import numpy as np


class Matrix:
    def __init__(self, width, height, cell_size):
        self.__height = height // cell_size
        self.__width = width // cell_size
        self.__matrix = np.zeros((self.__height, self.__width), dtype='int')
        self.__start = None
        self.__end = None

    def clear(self):
        # clear all cells to 0
        for i in range(self.__matrix.shape[0]):
            for j in range(self.__matrix.shape[1]):
                self.__matrix[i, j] = 0

    def get_cell(self, x, y):
        return self.__matrix[y, x]

    def set_cell(self, x, y, value):
        self.__matrix[y, x] = value

    def get_start(self):
        return self.__start

    def set_start(self, x, y):
        self.__start = (x, y)

    def get_end(self):
        return self.__end

    def set_end(self, x, y):
        self.__end = (x, y)

    def DFS_search(self):
        pass

    def BFS_search(self):
        pass



    
