import json

from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.simpledialog import askstring

from matrix import Matrix


# grid dimensions
WIDTH = 1000
HEIGHT = 500
CELL_SIZE = 50


class MazeApplication(Frame):
    def __init__(self, matrix, master=None, width=1000, height=500, cell_size=20):
        Frame.__init__(self, master)
        self.__master = master 
        self.__canvas = Canvas(master, width=width, height=height)
        self.__width = width
        self.__height = height
        self.__cell_size = cell_size
        self.__rects = {}
        self.__matrix = matrix

    def init_window(self):
        self.__master.title("Maze")
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.__master)
        self.__master.config(menu=menu)

        file = Menu(menu)
        file.add_command(label='Open...', command=self.__load)
        file.add_command(label='Save...', command=self.__store)
        file.add_command(label='Clear', command=self.__clear)
        file.add_command(label='Exit', command=self.__client_exit)
        menu.add_cascade(label='File', menu=file)

        file = Menu(menu)
        file.add_command(label='DFS', command=self.__matrix.DFS_search)
        file.add_command(label='BFS', command=self.__matrix.BFS_search)
        menu.add_cascade(label='Solve', menu=file)

    def draw_maze(self):
        # Draw grid
        for i in range(0, self.__width, self.__cell_size):
            self.__canvas.create_line(i, 0, i, 500, fill="gray", dash=(3,5))
        for i in range(0, self.__height, self.__cell_size):
            self.__canvas.create_line(0, i, 1000, i, fill="gray", dash=(3,5))

        # binf mouse buttons
        self.__canvas.bind("<Button-1>", self.__leftclick)
        self.__canvas.bind("<Button-2>", self.__middleclick)
        self.__canvas.bind("<Button-3>", self.__rightclick)
        self.__canvas.pack()

    def __fill_cell(self, x, y, color):
        left = x * CELL_SIZE
        top = y * CELL_SIZE
        rect = self.__canvas.create_rectangle(left, top, left + CELL_SIZE, 
                                              top + CELL_SIZE, fill=color)
        self.__rects[(x, y)] = rect

    def __fill_maze(self):
        walls = self.__matrix.get_filled_cells()
        for y, x in walls:
            self.__fill_cell(x, y, 'black')
        x, y = self.__matrix.get_start()
        self.__fill_cell(x, y, 'green')
        x, y = self.__matrix.get_end()
        self.__fill_cell(x, y, 'red')   

    def __leftclick(self, event):
        # add/remove walls or obstacles
        x = event.x // self.__cell_size
        y = event.y // self.__cell_size
        value = self.__matrix.get_cell(x, y)
        if value == 1:
            # remove wall/obstacle
            self.__matrix.set_cell(x, y, 0)
            rect = self.__rects[(x, y)]
            self.__canvas.delete(rect)
            del self.__rects[(x, y)]
        else:
            # add wall/obstacle
            self.__matrix.set_cell(x, y, 1)
            self.__fill_cell(x, y, 'black')

    def __middleclick(self, event):
        # get current start point
        start = self.__matrix.get_start()
        if start is not None:
            # remove previous start point
            x, y = start
            rect = self.__rects[(x, y)]
            self.__canvas.delete(rect)
            del self.__rects[(x, y)]
        # set new start point
        x = event.x // self.__cell_size
        y = event.y // self.__cell_size
        self.__matrix.set_start((x, y))
        self.__fill_cell(x, y, 'green')

    def __rightclick(self, event):
        # get previous end point
        end = self.__matrix.get_end()
        if end is not None:
            # remove previous end point
            x, y = end
            rect = self.__rects[(x, y)]
            self.__canvas.delete(rect)
            del self.__rects[(x, y)]
        # set new end point
        x = event.x // self.__cell_size
        y = event.y // self.__cell_size
        self.__matrix.set_end((x, y))
        self.__fill_cell(x, y, 'red')

    def __load(self):
        filename = askopenfilename(filetypes=[('JSON files', '*.json')])
        if filename == '':
            return
        with open(filename, 'r') as fp:
            data = json.load(fp)
        self.__clear()
        for i in range(len(data['walls'])):
            y, x = data['walls'][i]
            self.__matrix.set_cell(x, y, 1)
        self.__matrix.set_start(data['start'])
        self.__matrix.set_end(data['end'])
        self.__fill_maze()

    def __store(self):
        filename = asksaveasfilename(filetypes=[('JSON files', '*.json')])
        if filename == '':
            return
        data = {'start': self.__matrix.get_start(),
                'end': self.__matrix.get_end(),
                'walls': self.__matrix.get_filled_cells().tolist()}
        with open(filename, 'w') as fp:
            json.dump(data, fp)

    def __clear(self):
        # Clear the grid and matrix
        self.__matrix.clear()
        self.__matrix.set_start(None)
        self.__matrix.set_end(None)
        for key in self.__rects.keys():
            self.__canvas.delete(self.__rects[key])
        self.__rects.clear()

    def __client_exit(self):       
        self.master.destroy()


def main():
    matrix = Matrix(WIDTH, HEIGHT, CELL_SIZE)
    master = Tk() 
    maze_app = MazeApplication(matrix, master, WIDTH, HEIGHT, CELL_SIZE)
    maze_app.init_window()
    maze_app.draw_maze()
    mainloop()


if __name__ == '__main__':
    main()