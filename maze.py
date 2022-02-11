import json
import time
from collections import defaultdict
from threading import Thread, Event

from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.simpledialog import askstring
from tkinter.messagebox import showerror, showinfo

from matrix import Matrix


# grid dimensions
WIDTH = 1000
HEIGHT = 500
CELL_SIZE = 50
TIME_OUT = 3


class MazeApplication(Frame):
    def __init__(self, matrix, master=None, width=1000, height=500, cell_size=20):
        Frame.__init__(self, master)
        self.__master = master 
        self.__canvas = Canvas(master, width=width, height=height)
        self.__width = width
        self.__height = height
        self.__cell_size = cell_size
        self.__rects = defaultdict(list)
        self.__matrix = matrix

    def init_window(self):
        self.__master.title("Maze")
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.__master)
        self.__master.config(menu=menu)

        file = Menu(menu)
        file.add_command(label='Open Maze...', command=self.__load)
        file.add_command(label='Save Maze...', command=self.__store)
        file.add_command(label='Clear Maze', command=self.__clear)
        file.add_command(label='Exit', command=self.__client_exit)
        menu.add_cascade(label='File', menu=file)

        file = Menu(menu)
        file.add_command(label='Breadth First Search', 
                         command=lambda: self.__search(self.__matrix.BFS_search))
        file.add_command(label='Depth First Search', 
                         command=lambda: self.__search(self.__matrix.DFS_search))
        file.add_command(label='Clear Breadcrumbs', command = self.__clear_path)
        menu.add_cascade(label='Solve Maze', menu=file)

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

    def __fill_cell(self, x, y, color, scaling=1):
        cell_size = int(CELL_SIZE * scaling)
        padding = (CELL_SIZE - cell_size) // 2 if scaling < 1 else 0
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        rect = self.__canvas.create_rectangle(left, top, left + cell_size, 
                                              top + cell_size, fill=color)
        self.__rects[(x, y)].append(rect)

    def __fill_maze(self):
        # Fill maze from internal array
        cells = self.__matrix.get_filled_cells()
        for x, y in cells:
            self.__fill_cell(x, y, 'black')
        x, y = self.__matrix.get_start()
        self.__fill_cell(x, y, 'green')
        x, y = self.__matrix.get_end()
        self.__fill_cell(x, y, 'red')

    def __leftclick(self, event):
        # add/remove walls or obstacles
        x = event.x // self.__cell_size
        y = event.y // self.__cell_size
        if (self.__matrix.get_start() == (x, y) or 
            self.__matrix.get_end() == (x, y)):
                showerror('Error', 'Reset start or end before setting barrier.')
                return
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
        x = event.x // self.__cell_size
        y = event.y // self.__cell_size
        if self.__matrix.get_cell(x, y) == 1:
            showerror('Error', 'Cannot set start on a barrier.')
            return
        # get current start point
        start = self.__matrix.get_start()
        if start is not None:
            # remove previous start point
            x_prev, y_prev = start
            rect = self.__rects[(x_prev, y_prev)]
            self.__canvas.delete(rect)
            del self.__rects[(x_prev, y_prev)]
        # set new start point
        self.__matrix.set_start((x, y))
        self.__fill_cell(x, y, 'green')

    def __rightclick(self, event):
        x = event.x // self.__cell_size
        y = event.y // self.__cell_size
        if self.__matrix.get_cell(x, y) == 1:
            showerror('Error', 'Cannot set end on a barrier.')
            return
        # get previous end point
        end = self.__matrix.get_end()
        if end is not None:
            # remove previous end point
            x_prev, y_prev = end
            rect = self.__rects[(x_prev, y_prev)]
            self.__canvas.delete(rect)
            del self.__rects[(x_prev, y_prev)]
        # set new end point
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
            x, y = data['walls'][i]
            self.__matrix.set_cell(x, y, 1)
        self.__matrix.set_start(tuple(data['start']))
        self.__matrix.set_end(tuple(data['end']))
        self.__fill_maze()

    def __store(self):
        filename = asksaveasfilename(filetypes=[('JSON files', '*.json')])
        if filename == '':
            return
        data = {'start': self.__matrix.get_start(),
                'end': self.__matrix.get_end(),
                'walls': self.__matrix.get_filled_cells()}
        with open(filename, 'w') as fp:
            json.dump(data, fp)

    def __clear(self):
        # Clear the grid and matrix
        self.__matrix.clear()
        self.__matrix.set_start(None)
        self.__matrix.set_end(None)
        self.__matrix.found_path = []
        for key in self.__rects.keys():
            while len(self.__rects[key]) > 0:
                rect = self.__rects[key].pop()
                self.__canvas.delete(rect)
        self.__rects.clear()

    def __clear_path(self):
        if len(self.__matrix.found_path) > 0:
            for x, y in self.__matrix.found_path:
                rect = self.__rects[(x, y)].pop()
                self.__canvas.delete(rect)
            self.__matrix.found_path = []

    def __search(self, method):
        if self.__matrix.get_start() is None:
            showerror('Error', 'Start point not set. Set with middle mouse button.')
        elif self.__matrix.get_end() is None:
            showerror('Error', 'End point not set.  Set with right mouse button.')
        else:
            self.__clear_path()
            # setup time out for search thread
            self.__matrix.stop_flag = False
            search_thread = Thread(target=method)
            search_thread.start()
            # wait for search thread to naturally complete
            search_thread.join(TIME_OUT)
            if search_thread.is_alive():
                # tell it to exit
                self.__matrix.stop_flag = True
                search_thread.join()
                self.__matrix.found_path = []
                showinfo('Info', 'Search timed out.')
            elif len(self.__matrix.found_path) == 0:
                showinfo('Info', 'No path was found.')
            else:
                for x, y in self.__matrix.found_path:
                    self.__fill_cell(x, y, color='yellow', scaling=0.25)

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