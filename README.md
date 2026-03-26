# Rush Hour Puzzle Solver  
**Group 15 | CSF401 Artificial Intelligence | BITS Pilani** <br>
**Semester 2, 2025-26 | Complexity Level: L2**  <br>
**Members : Shivansh Saxena, Navya Jain, Aditya Kumar Panda** 

## How To Run

Install dependencies:
 pip install matplotlib numpy pillow

Run the solver:
 python rush_hour.py

Outfit GIFs will be saved in the output/folder.
Set SHOW_SEARCH = False to save gifs of the final output.

## Algorithm Used

**BFS(Breadth First Search)**
Explore all states level by level. Guaranteed to find the shortest solution. Does not use any heurestic.

**IDDFS(Iterative Deepening DFS)**
Runs DFS with increasing depth limits. Uses much less memory than BFS while still finding the optimal solution.

**Greedy Best First Search**
Always picks the state that looks closest to the goal using the heurestic. Fast but not guaranteed to be optimal.

**A*Search**

Combines actual move cost g(n) and heurestic h(n) using
f(n) = g(n) + h(n)
Optimal and efficient. 
