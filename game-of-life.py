"""
Ari Hietanen
Convay's Game of Life  with Tkinter

This was by far the longest program I've written so far (April 15th 2020). I
have barely used libraries before, so creating this required a decent bit of
googling but I'm relatively happy with the "final" version.

Rules of the Game: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
    - Live cells are black and dead ones are white
"""

import tkinter as tk
from tkinter import ttk
from copy import deepcopy
from random import getrandbits
from timeit import default_timer as timer


class GUI:
    """
    A GUI that creates a Convay's game of life with a modular grid size, a
    manual and automatic way to simulate progression as well as possibility to
    add pregenerated patterns to the grid.
    """
    def __init__(self):

        """
        Actual window and Frames
        """
        self.__root = tk.Tk()
        self.__root.title("Convay's Game of Life")
        self.__setting_frame = tk.Frame(self.__root, bd=5, width=521,
                                        height=1005)
        self.__setting_frame.pack(side=tk.LEFT, fill="y", expand=False)
        self.__setting_frame.pack_propagate(0)
        self.__game_canvas = tk.Canvas(self.__root, bg="grey")
        self.__game_canvas.pack(side=tk.RIGHT, fill="both", expand=True)

        """
        Values required in the methods
        """
        self.__pattern_dict = {"living dot 1×1": [[1]],
                               "dead dot 1×1": [[0]],
                               "blinker 3×3": [[0, 1, 0], [0, 1, 0], [0, 1, 0]],
                               "block 2×2": [[1, 1], [1, 1]],
                               "glider 3×3": [[0, 1, 0], [0, 0, 1], [1, 1, 1]],
                               "10-line 3×10": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}
        self.__grid_list = []
        self.__sq_width = 0
        self.__sq_height = 0
        self.__continue_loop = False
        self.__counter = 0
        self.__dict_material_var = tk.StringVar()
        self.__rand_y_n = tk.IntVar()
        self.__play_speed = tk.IntVar()
        self.__play_speed_text_var = tk.StringVar()

        """
        Defining the widgets of the Settings-frame
        """
        self.__width_info = tk.Label(self.__setting_frame,
                                     text="Width in squares (Integer)")
        self.__width_entry_val = tk.Entry(self.__setting_frame)
        self.__width_entry_val.insert(tk.END, "60")
        self.__height_info = tk.Label(self.__setting_frame,
                                      text="Height in squares (Integer)")
        self.__height_entry_val = tk.Entry(self.__setting_frame)
        self.__height_entry_val.insert(tk.END, "40")
        self.__entry_info = tk.Label(self.__setting_frame,
                                     text="Update the grid for information")
        self.__sq_side_length_info = tk.Label(self.__setting_frame,
                                              text="Side lenght of a square "
                                                   "(Int, in pixels)")
        self.__sq_side_length_val = tk.Entry(self.__setting_frame)
        self.__sq_side_length_val.insert(tk.END, "24")
        self.__update_grid_btn = tk.Button(self.__setting_frame,
                                           text="New Grid",
                                           command=self.generate_grid)

        self.__radiobtn1 = tk.Radiobutton(self.__setting_frame,
                                          text="Random fill",
                                          variable=self.__rand_y_n, value=1)

        self.__radiobtn2 = tk.Radiobutton(self.__setting_frame,
                                          text="Blank fill",
                                          variable=self.__rand_y_n, value=0)

        self.__next_simulation_step_btn = \
            tk.Button(self.__setting_frame,
                      text="Simulate one step",
                      command=self.next_simulation_step)
        self.__play_pause_btn = \
            tk.Button(self.__setting_frame,
                      text="Play / Pause",
                      command=self.play_pause)
        self.__play_speed_slider = tk.Scale(self.__setting_frame,
                                            orient=tk.HORIZONTAL,
                                            from_=10, to=1000,
                                            variable=self.__play_speed)
        self.__play_speed_info = \
            tk.Label(self.__setting_frame,
                     textvariable=self.__play_speed_text_var)

        self.__pattern_selector = \
            ttk.Combobox(self.__setting_frame,
                         values=list(self.__pattern_dict.keys()),
                         textvariable=self.__dict_material_var)
        self.__insert_pattern_btn = \
            tk.Button(self.__setting_frame, text="Insert a predefined pattern",
                      command=self.insert_predefined_ptrn)
        self.__insert_pattern_x_info = tk.Label(self.__setting_frame,
                                                text="y-val")
        self.__insert_pattern_y_info = tk.Label(self.__setting_frame,
                                                text="x-val")
        self.__insert_pattern_x_val = tk.Entry(self.__setting_frame)
        self.__insert_pattern_x_val.insert(tk.END, 0)
        self.__insert_pattern_y_val = tk.Entry(self.__setting_frame)
        self.__insert_pattern_y_val.insert(tk.END, 0)

        self.__insert_pattern_info = tk.Label(self.__setting_frame,
                                              text="Insert a pattern for info")

        self.__close_btn = tk.Button(self.__setting_frame, text="End program",
                                     command=self.close, bg="#FF8686",
                                     activebackground="#FF4040")

        """
        Specifying the locations of the before mentioned widgets
        """
        self.__setting_frame.grid_columnconfigure(0, weight=3)
        self.__setting_frame.grid_columnconfigure(1, weight=1)
        self.__setting_frame.grid_columnconfigure(2, weight=1)

        self.__width_info.grid(row=0, column=0, sticky=tk.EW)
        self.__width_entry_val.grid(row=0, column=1, sticky=tk.EW,
                                    columnspan=2)
        self.__height_info.grid(row=1, column=0, sticky=tk.EW)
        self.__height_entry_val.grid(row=1, column=1, sticky=tk.EW,
                                     columnspan=2)
        self.__sq_side_length_info.grid(row=2, column=0, sticky=tk.EW)
        self.__sq_side_length_val.grid(row=2, column=1, sticky=tk.EW,
                                       columnspan=2)

        self.__update_grid_btn.grid(row=3, column=0, sticky=tk.EW)
        self.__radiobtn1.grid(row=3, column=1)
        self.__radiobtn2.grid(row=3, column=2)
        self.__entry_info.grid(row=4, column=0, sticky=tk.W)
        self.__next_simulation_step_btn.grid(row=4, column=1, sticky=tk.EW,
                                             columnspan=2)

        self.__play_pause_btn.grid(row=5, column=0, sticky=tk.EW,
                                   columnspan=1)
        self.__play_speed_slider.grid(row=5, column=1, sticky=tk.EW,
                                      columnspan=2)
        self.__play_speed_info.grid(row=7, column=0, columnspan=3)

        tk.Label(self.__setting_frame).grid(row=8, column=0, columnspan=3)

        self.__pattern_selector.grid(row=11, column=0, sticky=tk.EW)
        self.__insert_pattern_btn.grid(row=10, column=0, sticky=tk.EW)
        self.__insert_pattern_x_info.grid(row=10, column=1, sticky=tk.EW)
        self.__insert_pattern_y_info.grid(row=10, column=2, sticky=tk.EW)
        self.__insert_pattern_x_val.grid(row=11, column=1, sticky=tk.EW)
        self.__insert_pattern_y_val.grid(row=11, column=2, sticky=tk.EW)
        self.__insert_pattern_info.grid(row=12, column=0, sticky=tk.W,
                                        columnspan=3)

        tk.Label(self.__setting_frame).grid(row=15, column=0, columnspan=3)

        self.__close_btn.grid(row=25, column=0, columnspan=3, sticky=tk.SE)

        self.__root.mainloop()

    def close(self):
        """
        Closes the window using the red button
        :return: None
        """
        self.__root.destroy()

    def generate_grid(self):
        """
        1) Changes the self.__grid_list according to the input values given in
        the Entry boxes for width, height and side length.
        2) Constructs the new grid on the canvas.
        :return: None
        """

        __negative = False
        __nonintegers = False

        # Saves the Entry values while evaluating their applicability
        try:
            self.__sq_width = int(self.__width_entry_val.get())
            self.__sq_height = int(self.__height_entry_val.get())
            s_length = int(self.__sq_side_length_val.get())

            if self.__sq_width < 1 or self.__sq_height < 1 or s_length < 1:
                __negative = True
                raise ValueError

        except ValueError:
            __nonintegers = True
        except KeyError:
            self.__entry_info[
                "text"] = "Select a key from above, first."

        if __negative:
            self.__entry_info[
                "text"] = "All of the values must be positive."
            return
        elif __nonintegers:
            self.__entry_info[
                "text"] = "All of the values must be integers."
            return
        elif self.__sq_width * self.__sq_height > 5000:
            self.__entry_info["text"] = "Keep the amount of squares " \
                                        "below 5000."
            return
        elif self.__sq_width * s_length>1440 or self.__sq_height*s_length>1000:
            self.__entry_info[
                "text"] = "The maximum size of the grid is " \
                          "1440×1000 pixels"
            return
        else:
            self.__entry_info[
                "text"] = f"Grid updated, {self.__sq_width * self.__sq_height}"\
                          f" squaress."

        # Cleans the canvas from old marks and draws the new grid
        self.__grid_list = 0
        self.__grid_list = []

        for i in range(self.__sq_width):
            self.__grid_list.append(i)
            self.__grid_list[i] = []
            for ii in range(self.__sq_height):
                if self.__rand_y_n.get() == 1:
                    __sq_val = getrandbits(1)
                else:
                    __sq_val = 0
                self.__grid_list[i].append(__sq_val)

        self.draw_on_canvas()

    def find_neighbors(self, x, y):
        """
        Helper function for managing the data and checking the rules
        Finds the neighbors to a square in position (x,y) in the current grid.
        :param x: The ordinal number of the square from left to right
        :type x: int
        :param y: The ordinal number of the square from top to bottom
        :type y: int
        :return: Neighbor squares of the square as a (1d) list
        :rtype: list
        """

        neighbors = []
        for i in [-1, 0, 1]:
            for ii in [-1, 0, 1]:
                try:
                    if not (y + i == y and x + ii == x) and \
                            (x + ii in list(
                                range(0, len(self.__grid_list[y]) + 1))) \
                            and (
                            y + i in list(range(0, len(self.__grid_list)))):
                        neighbors.append(self.__grid_list[y + i][x + ii])
                except IndexError:
                    pass
        return neighbors

    def count_active_neighbors(self):
        """
        Helper function for managing the data and checking the rules
        Counts the amount of '1's in the given list.
        :return: Matrix (2d-array)
        :rtype: list
        """
        __count_grid_list = deepcopy(self.__grid_list)
        for i in range(len(__count_grid_list)):
            for ii in range(len(__count_grid_list[i])):
                current_neighbors = self.find_neighbors(ii, i)
                __count_grid_list[i][ii] = str(current_neighbors).count("1")
        return __count_grid_list

    def next_simulation_step(self):
        """
        Simulates one step/iteration of the game. This method checks the state
        (activeness and amount of neighbors) of each square one by one and then
        applies the changes according to the rules (mentioned below)
        :return: None
        """
        __start = timer()
        # If ran before generate_grid, runs it and continues if the entry was ok
        if not self.__grid_list:
            self.generate_grid()
            if not self.__grid_list:
                return

        # If the side length is modified to 0 during automated loop
        try:
            __s_len = int(self.__sq_side_length_val.get())
            if __s_len*self.__sq_height > 1000 or \
                    __s_len * self.__sq_width > 1440:
                raise ValueError

        except ValueError:
            self.__continue_loop = False
            self.__play_speed_text_var.set("Side length was Illegal."
                                           "The game was paused.")
            self.__game_canvas.delete("all")
            self.__root.after(4000, lambda: self.__play_speed_text_var.set(
                ""))
            return

        __neighbors_for = self.count_active_neighbors()

        for i in range(len(self.__grid_list)):
            for ii in range(len(self.__grid_list[i])):

                # The actual Rules of the Game
                if self.__grid_list[i][ii] == 1:
                    if __neighbors_for[i][ii] < 2:
                        self.__grid_list[i][ii] = 0
                    elif 2 <= __neighbors_for[i][ii] <= 3:
                        self.__grid_list[i][ii] = 1
                    elif __neighbors_for[i][ii] > 3:
                        self.__grid_list[i][ii] = 0
                elif self.__grid_list[i][ii] == 0 \
                        and __neighbors_for[i][ii] == 3:
                    self.__grid_list[i][ii] = 1

        self.draw_on_canvas()
        __end = timer()

        self.monitor_playback_speed(__start, __end)

    def draw_on_canvas(self):
        """
        Draws the current self.__grid_list to the game_canvas
        :return: None
        """
        self.__game_canvas.delete("all")
        s_length = int(self.__sq_side_length_val.get())
        for y in range(len(self.__grid_list)):
            for x in range(len(self.__grid_list[y])):
                self.__game_canvas.create_rectangle(
                    (y * s_length, x * s_length, y * s_length + s_length,
                     x * s_length + s_length),
                    fill="white" if self.__grid_list[y][x] == 0 else "black",
                    outline="", state=tk.DISABLED, activefill="grey")

    def insert_predefined_ptrn(self):
        """
        Inserts a predefined pattern to the canvas with the top left corner of
        the pattern assigned by the entry values x and y.
        :return: None
        """

        __negative = False
        __nonintegers = False
        __doesnt_fit = False

        # Checks if there is space for the pattern / the entry can be used
        try:
            __pattern_name = self.__pattern_selector.get()
            __pattern = self.__pattern_dict[__pattern_name]

            x = int(self.__insert_pattern_x_val.get())
            y = int(self.__insert_pattern_y_val.get())

            if x < 0 or y < 0:
                __negative = True

            elif x + len(__pattern[0]) > len(self.__grid_list[0]) or \
                    y + len(__pattern) > len(self.__grid_list):
                __doesnt_fit = True

        except ValueError:
            __nonintegers = True

        except KeyError:
            self.__insert_pattern_info[
                "text"] = "Select a pattern from above, first."
            return

        # Given if a grid isn't defined. -> attempts to create it
        except IndexError:
            if not self.__grid_list:
                self.__insert_pattern_info["text"] = "Create a grid, first"
                return

        # Updates the info according to the taken data
        if __negative:
            self.__insert_pattern_info[
                "text"] = "Given coordinate doesn't exist in the grid."

        elif __nonintegers:
            self.__insert_pattern_info[
                "text"] = "The coordinates must be given as integers."

        elif __doesnt_fit:
            self.__insert_pattern_info[
                "text"] = "The pattern doesn't fit if it starts from the " \
                          "given grid."
        else:
            self.__insert_pattern_info["text"] = "Pattern added succesfully!"

        if __negative or __doesnt_fit or __nonintegers:
            return

        # Replaces an area of grid_list starting at  spot defined by the entries
        for i in range(len(__pattern)):
            for ii in range(len(__pattern[0])):
                self.__grid_list[y + i][x + ii] = __pattern[i][ii]
        self.draw_on_canvas()

    def play_pause(self):
        """
        Pauses / Unpauses the simulation step.
        :return: None
        """
        if self.__continue_loop:
            self.__continue_loop = False
        else:
            self.__continue_loop = True
        self.run_loop()

    def run_loop(self):
        """
        Loops self.next_simulation_step as long as self.__continue_loop is not
        changed to False.
        The scale and its variable self.__play_speed determine the pace.
        :return: None
        """
        if self.__continue_loop:
            self.__root.after(self.__play_speed.get(),
                              lambda: [self.next_simulation_step(),
                                       self.run_loop()])

    def monitor_playback_speed(self, start, end):
        """
        Slows the play_speed if the program/next_simulation_step
        can't keep up with it.
        :param start: Starting time of a iteration measured by timeit
        :param end: Ending time of an iteration measured by timeit
        :return: None
        """
        if self.__continue_loop:
            __laptime = 1000*(end-start)
            if __laptime + __laptime*0.10 > self.__play_speed.get():
                self.__play_speed.set(self.__play_speed.get()+25)
                self.__play_speed_text_var.set("Play-speed was slowed down!")
                self.__root.after(4000, lambda: self.__play_speed_text_var.set(
                    ""
                ))
        else:
            pass


def main():
    window = GUI()


if __name__ == '__main__':
    main()
