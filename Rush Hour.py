                                                                                #Rush Hour Puzzle Solver#
                                                                  # Group 15 | CS F401 Artificial intelligence | BITS Pilani 
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
# STATE CLASS 
# A State is one complete snapshot of the board
# It stores where every vehicle is sitting at that moment
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
                    for i in range (len(self.vehicles)))
# MAKE GRID
# Converts a State into a simple 2D grid of letters.
# Empty cells show a dot . Occupied cells show the vehicle name.
# We use this to check if a cell is free before moving a vehicle.
def make_grid(state):
    """Builds a 6x6 grid from the current state so we can check empty cells."""
    grid = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)] # start with a completely empty board
    for v in state.vehicles:        # place each vehicle onto the grid
        if v.orientation == 'H':
           for i in range(v.length):
               grid[v.y][v.x + i] = v.name      # fill cells going right
        else:
              for i in range(v.length):
                  grid[v.y + i][v.x] = v.name   # fill cells going down
    
     return grid
## COPY BOARD
# Makes a fresh copy of the vehicle list so we can modify it
# without changing the original state. This is important because each successor state must be completely independent.
def copy_vehicles(vehicles):
    """Returns a new list of Vehicle objects with the same values."""
    new_list = []
    for v in vehicles:
        new_list.append(Vehicle(v.x, v.y, v.length, v.orientation, v.name))
    return new_list
# SHOW BOARD (live window during search)
# only runs when SHOW_SEARCH =true
# Display the board as a colour image while the algorithm works.
def show_board(state):
   """Shows the current board in a matplotlib window during search."""
if not SHOW_SEARCH:
  return
try:
  grid=make_grid(state)
  #convert letters to numbers so matplotlib can colour them
  # 0=empty (grey), 1=normal car (blue), 2=red car(red)
  colour_grid = np.zeros((BOARD_SIZE, BOARD_SIZE))
  for row in range(BOARD_SIZE):
    for col in range(BOARD_SIZE):
      if grid[row][col]=='R':
        colour_grid[row][col] = 2 
      elif grid[row][col] ! = '.':
        colour_grid[row][col] = 1
  plt.imshow(colour_grid, cmap='coolwarm')
  plt.grid(true)                                
  for row in range(BOARD_SIZE): # write the vehicle letter inside each occupied cell
    for col in range(BOARD_SIZE):
      if grid[row][col] != '.':
         plt.text(col,row,grid[row][col], ha='center' , va='center')
  plt.xticks([])
  plt.yticks([])
  plt.title(f"moves so far:{state.moves}")
  plt.pause(0.2)
  plt.clf()
except:
    pass   #skip silently if no display is available
# REACHED EXIT
# The puzzle is solved when the red car touches the right wall.
# The exit is at column 5 on row 2.
# vehicles[0] is always the red car R.
def reached_exit(state):
    """Returns True when the red car has reached column 5."""
    red_car = state.vehicles[0]
    return red_car.x + red_car.length - 1 == BOARD_SIZE - 1 
# NEXT STATES (successor generation)
# Given a board state, finds every state reachable in one move.
# Each vehicle tries sliding one cell in both directions.
# Only moves to empty cells are allowed.

