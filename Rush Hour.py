                                         #Rush Hour Puzzle Solver
                          #Group 15 | CS F401 Artificial intelligence | BITS Pilani 

#We solve the Rush Hour puzzle using four search algorithms:
#   1. BFS    - searches level by level, no hints used
#   2. IDDFS  - like BFS but uses much less memory
#   3. Greedy - uses a smart guess to search faster
#   4. A*     - combines actual cost + smart guess, best overall

#   Two heuristics are implemented:
#   H1 - count how many cars are blocking the red car
#   H2 - H1 + how far the red car still needs to travel

import heapq                            # used for priority queue in Greedy and A*
from collections import deque           # used for BFS queue
import copy                             # used to copy the board without changing original
import matplotlib.pyplot as plt         # used to draw the board
import numpy as np                      # used to create the colour grid for display
import os                               # used to create the output folder
BOARD_SIZE = 6
SHOW_SEARCH = False                     # the Rush Hour board is always 6 rows x 6 columns
from itertools import count
tie_breaker = count()                   # counter helps the priority queue break ties safely
os.makedirs("output" , exist_ok=True)   # create the output folder if it does not already exist
# VEHICLE CLASS 
# Stores the position , size , direction , and name of one vehicle
class Vehicle:
def __init__(self, x, y, Length, orientation, name):
  """   x           : column number, 0 is the left edge
        y           : row number, 0 is the top edge
        length      : how many cells it takes up (2 or 3)
        orientation : H means horizontal, V means vertical
        name        : one letter label, R is always the red car  """
  self.x = x
  self.y = y  
  self.length = length
  self.orientation = orientation
  self.name = name
#STATE CLASS 
#A State is one complete snapshot of the board
#It stores where every vehicle is sitting at that moment
class State:
     def __init__(self, vehicles, moves=0):
         """  vehicles : list of all vehicle object on the board
                 moves : number of moves taken to reach this state """
      self.vehicles = vehicles
      self.moves = moves
      def__hash__(self):
         """needed so python can store states in  a set to track visited ones """
         return hash (tuple((v.x,v.y) for v in self.vehicles))
      def__eq__(self,other):
         """Two states are the same if every vehicles is at the same position """
         return all(self.vehicles[i].x==other.vehicles[i].x and self.vehicles[i].y==other.vehicles[i].y 
                    for i in range (len(self.vehicles))
         )
# MAKE GRID
# Converts a State into a simple 2D grid of letters.
# Empty cells show a dot . Occupied cells show the vehicle name.
# We use this to check if a cell is free before moving a vehicle.
def make_grid(state):
    """Builds a 6x6 grid from the current state so we can check empty cells."""
    # start with a completely empty board
    grid = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # place each vehicle onto the grid
    for v in state.vehicles:
        if v.orientation == 'H':
            for i in range(v.length):
                grid[v.y][v.x + i] = v.name   # fill cells going right
        else:
            for i in range(v.length):
                grid[v.y + i][v.x] = v.name   # fill cells going down

    return grid
