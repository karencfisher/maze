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

    def get_filled_cells(self):
        cells = np.argwhere(self.__matrix == 1)
        return [(int(cells[i, 1]), int(cells[i, 0])) 
                    for i in range(len(cells))]

    def get_start(self):
        return self.__start

    def set_start(self, start):
        self.__start = start

    def get_end(self):
        return self.__end

    def set_end(self, end):
        self.__end = end

    def DFS_search(self):
        path_found = []
        def recurse(node, path):
            nonlocal path_found
            path.append(node)
            if node == self.__end:
                path_found = path[:]
                return
            adjacent = self.__get_adjacent(node)
            for adj in adjacent:
                if adj in path:
                    continue
                recurse(adj, path)
                path.pop()
        recurse(self.__start, [])
        return path_found

    def BFS_search(self):
        path = []
        return path

    def __get_adjacent(self, cell):
        x, y = cell
        adjacent = []
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for offset in offsets:
            x_new, y_new = x + offset[0], y + offset[1]
            if ((x_new < 0 or x_new >= self.__matrix.shape[1]) or
                (y_new < 0 or y_new >= self.__matrix.shape[0])):
                    continue 
            value = self.__matrix[y_new, x_new]
            if value == 0:
                adjacent.append((x_new, y_new))
        return adjacent
        



    
