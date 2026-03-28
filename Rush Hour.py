                                                                                #Rush Hour Puzzle Solver#
                                                                  # Group 15 | CS F401 Artificial intelligence | BITS Pilani 
#   We solve the Rush Hour puzzle using four search algorithms:
#   1. BFS    - searches level by level
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
     """x           : column number, 0 is the left edge
        y           : row number, 0 is the top edge
        length      : how many cells it takes up (2 or 3)
        orientation : H means horizontal, V means vertical
        name        : one letter label, R is always the red car"""
   self.x = x
   self.y = y  
   self.length = length
   self.orientation = orientation
   self.name = name
# STATE CLASS 
# A State is one complete snapshot of the board
# It stores where every vehicle is sitting at that moment
class State:
    """Represents one board configuration at a specific moment."""
    def __init__(self, vehicles, moves=0):
     """vehicles : list of all Vehicle objects on the board
        moves    : number of moves taken to reach this state"""
        self.vehicles = vehicles
        self.moves = moves
    def __hash__(self):
        """Needed so Python can store States in a set to track visited ones."""
        return hash(tuple((v.x, v.y) for v in self.vehicles))
    def __eq__(self, other):
        """Two states are the same if every vehicle is at the same position."""
        return all(
            self.vehicles[i].x == other.vehicles[i].x and self.vehicles[i].y == other.vehicles[i].y
            for i in range(len(self.vehicles)))
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
# COPY BOARD
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
        grid = make_grid(state)
        # convert letters to numbers so matplotlib can colour them
        # 0 = empty (grey), 1 = normal car (blue), 2 = red car (red)
        colour_grid = np.zeros((BOARD_SIZE, BOARD_SIZE))
        for row in range(BOARD_SIZE): 
            for col in range(BOARD_SIZE):
                if grid[row][col] == 'R':
                    colour_grid[row][col] = 2 
                elif grid[row][col] != '.':  
                    colour_grid[row][col] = 1
        plt.imshow(colour_grid, cmap='coolwarm')
        plt.grid(True) 
        for row in range(BOARD_SIZE): # write the vehicle letter inside each occupied cell
            for col in range(BOARD_SIZE):
                if grid[row][col] != '.':
                    plt.text(col, row, grid[row][col], ha='center', va='center')
        plt.xticks([])
        plt.yticks([])
        plt.title(f"moves so far: {state.moves}")
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
def next_states(state):
    """Returns a list of all board states reachable in exactly one move."""
    possible_moves = []
    grid = make_grid(state)
    for idx, v in enumerate(state.vehicles):
        if v.orientation == 'H':
            # try sliding this vehicle one step to the right
            right_cell = v.x + v.length
           if right_cell < BOARD_SIZE and grid[v.y][right_cell] == '.':
              new_vehicles = copy_vehicles(state.vehicles)
              new_vehicles[idx].x += 1
              possible_moves.append(State(new_vehicles, state.moves + 1))
            # try sliding this vehicle one step to the left
            left_cell = v.x - 1
            if left_cell >= 0 and grid[v.y][left_cell] == '.':
                new_vehicles = copy_vehicles(state.vehicles)
                new_vehicles[idx].x -= 1
                possible_moves.append(State(new_vehicles, state.moves + 1))
       else:
            # try sliding this vehicle one step downward
            one_down = v.y + v.length
            if one_down < BOARD_SIZE and grid[one_down][v.x] == '.':
                new_vehicles = copy_vehicles(state.vehicles)
                new_vehicles[idx].y += 1
                possible_moves.append(State(new_vehicles, state.moves + 1))
            # try sliding this vehicle one step upward
            one_up = v.y - 1
            if one_up >= 0 and grid[one_up][v.x] == '.':
                new_vehicles = copy_vehicles(state.vehicles)
                new_vehicles[idx].y -= 1
                possible_moves.append(State(new_vehicles, state.moves + 1))

    return possible_moves
#HEURISTIC 1 — Blocking Vehicle Count (H1)
# Counts how many cars are sitting between the red car and the exit on row 2. 
# Each one needs at least one move to clear, so this is always a safe lower bound — admissible.
def h1_blocking_count(state):
    """H1: counts vehicles directly blocking the red car's path to exit."""
    grid = make_grid(state)
    red_car = state.vehicles[0]
    blockers = 0
    for col in range(red_car.x + red_car.length, BOARD_SIZE): # scan every column between the red car and the exit
        if grid[red_car.y][col] != '.':
            blockers += 1
    return blockers
# HEURISTIC 2 — Blocking Count + Distance (H2)
# H1 plus how many cells the red car still needs to travel.
# This is a tighter estimate and still never overestimates.
# H2 is a always >= H1 so it is said to dominate H1.
# A* with H2 explores fewer states than A* with H1.
def h2_blocking_plus_distance(state):
    """H2: H1 + the remaining distance the red car must travel."""
    red_car = state.vehicles[0]
    blockers = h1_blocking_count(state)
    distance_left = (BOARD_SIZE - 1) - (red_car.x + red_car.length - 1)
    return blockers + distance_left
# TRACE BACK (path reconstruction)
# After the goal is found, walk backwards through parent
# pointers to rebuild the full solution path from start to goal.
def trace_back(parents, id_to_state, goal_state):
    """Rebuilds the solution path by following parent pointers backwards."""
    path = []
    current_id = id(goal_state)
    while current_id is not None:
        path.append(id_to_state[current_id])
        current_id = parents.get(current_id)
    path.reverse()   # flip so it reads from start to goal
    return path

def bfs(start):
  # breadth first search- optimal, uninformed
  frontier = deque([start])
  visited = set([start])
  parents = {id(start):None}
  states = {id(start:start}
  nodes = 0
  while frontier:
    current = frontier.popleft()
    nodes += 1
    show_board(current)
    if reached_exit(current):
      print("BFS solved in", current.moves, "moves | states explored:", nodes)
return current, trace_back(parents, states, current), nodes
for neighbour in next_states(current):
  if neghbour not in visited:
    visited.add(neighbour)
parents[id(neighbour)] = id(current)
states[id(neighbour)] = neighbour
frontier.append(neighbour)
return None, [], nodes

# BFS — Breadth First Search
# Explores all states reachable in 1 move, then 2, then 3...
# Guaranteed to find the shortest solution.
# Does not use any heuristic — purely uninformed.
# Explores many states because it has no guidance.
def bfs(start):
    """BFS: explores level by level, guaranteed optimal, no heuristic."""
    queue   = deque([start])      # states waiting to be explored
    visited = set([start])        # states already seen
    parents = {id(start): None}   # tracks how we reached each state
    states  = {id(start): start}
    nodes   = 0
    while queue:
      current = queue.popleft()
      nodes += 1
      show_board(current)
      if reached_exit(current)
      print("BFS solved in", current.moves, "moves | states explored:", nodes)
      return current, trace_back(parentss, states, current), nodes
      for neighbour in next_states(current):
        if neighbour not in visited:
          visited.add(neighbour)
                parents[id(neighbour)] = id(current)
                states[id(neighbour)]  = neighbour
                queue.append(neighbour)
    return None, [], nodes
# IDDFS — Iterative Deepening Depth First Search
# Tries depth 0, then depth 1, then depth 2, and so on.
# At each attempt it does a depth-limited DFS.
# Uses far less memory than BFS because it only keeps
# the current path in memory, not the whole frontier.
# Still finds the optimal solution like BFS.
def limited_dfs(state, depth_Left, visited, parents, states):
  "Helper for IDDFS - Does DFS but stops at the given depth limit"
show_board(state)
if reached_exit(state):
  return state          # found the goal
if depth_Left == 0:
  return None           # hit the depth limit, stop here
visited.add(state)
for neighbour in next_states(state):
  if neighbour not in visited:
    parents[id(neighbour)] = id(state)
    states[id(neighbour)] = neighbour
    result = limited_dfs(neighbour, depth_Left - 1, visited, parents, states)
if result:
  return result    # pass the goal back up the call stack
return None
def iddfs(start, max_depth=50):
  """IDDFS: repeats DFS with increasing depth limits until goal is found."""
total_nodes = 0
for depth in range(max_depth):
  parents = {id(start): None}
  states  = {id(start): start}
  result  = limited_dfs(start, depth, set(), parents, states)
  total_nodes += depth * 10   # each extra depth re-expands earlier levels
   if result:
     print("IDDFS solved at depth", depth, "| states explored:", total_nodes)
     return result, trace_back(parents, states, result), total_nodes
return None, [], total_nodes
# GREEDY SEARCH
# Always picks the state that looks closest to the goal
# based on the heuristic. Very fast but NOT guaranteed to
# find the shortest solution because it ignores move cost.
# f(n) = h(n) only
def greedy(start, heuristic):
  "Greedy: always picks the state with the lowest heuristic value"
heap = []      # priority queue, lowest h(n) goes first
visited = set([start])
parents = {id(start): None}
states = (id(start): start}
nodes = 0
heapq.heappush(heap, (heuristic(start), next(tie_breaker), start))
while heap:
  current = heapq.heappop(heap)
  nodes +=1
  show_board(current)
  if reached_exit(current):
    print("Greedy solved in", current.moves, "moves | states explored:", nodes)
    return current, track_back(parents, states, current), nodes
    for neighbour in next_states(current):
      if neighbour not in visited:
        visited.add(neighbour)
        parents[id(neighbour)] = id(current)
        states[id(neighbour)] = neighbour
        heapq.heappush(heap, (heuristic(neighbour), next(tie_breaker), neighbour))
        return None, [], nodes

# A* SEARCH
# Combines actual move cost g(n) with heurestic estimate h(n).
#f(n) = g(n) + h(n)
# Guaranteed to find the shortest solution when the heurestic is admissible. Explores far fewer states than BFS.

def astar(start, heurestic):
  """A*: picks states with lowest f(n) = g(n) + h(n), optimal and informal."""
  heap = []             #priority queue, lowest f(n) goes first
  visited = set([start])
  parents = {id(start): None}
  states = {id(start): start}
  nodes = 0

heapq.heappush(heap, (heurestic(start) + start.moves, next(tie_breaker), start))

while heap:
  _, _, current = heapq.heappop(heap)
  nodes += 1
  show_board(current)
  
if reached_exit(current):
  print("A* solved in", current.moves, "moves | states explored:", nodes)
  return current, trace_back(parents, states, current), nodes

