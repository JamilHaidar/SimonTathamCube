# SimonTathamCube
Implementation of the Cube game from Simon Tatham's Puzzles with an optimal solution search in Python. A standalone executable can be downloaded and run to try out the game.

Controls:
Arrow keys to move cube
N to start new game
S to solve puzzle

The game being explored can be found [here](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/cube.html).
I have been able to find strategies and algorithms for all puzzles in this game (even NP hard ones, I just iterate through possible states in a greedy/pruning way). 
I decided to start implementing solutions for these games, and I will start with Cube.

## Objective and Approach
The objective of Cube is simple:
Roll the cube around the grid, picking up the blue squares on its faces. Try to get all the blue squares on to the object at the same time, in as few moves as possible.

### Game Implementation
I recreate the game in Python using PyGame. It does not support 3D objects, therefore, I coded the grid as a 2D object and the cube as a 3D object, which I used a projection matrix to get it down to 2D.
Projecting to 2D from above, only the cube's top shows. Therefore, I applied a shear operation on the cube in the negative x and y directions to show the other faces.

I kept the empty faces undrawn on purpose to allow to see behind the facing 3 sides of the cube (to know the full state of the cube).

### Game solution
I based the solution on a very interesting discussion with [Michał Stachurski](https://cs.stackexchange.com/users/156430/micha%c5%82-stachurski) on a question I posted on stackexchange [(link)](https://cs.stackexchange.com/questions/156414/).
I had already found a manual solution using an algorithm I devised which uses cube nets. The approach I posted can be found [here](https://math.stackexchange.com/questions/4605240). When I decided to code a solution, I knew a BFS solution would make sense, but the number of states made it seem to be too large.
However, Michał told me about the Burnside lemma, and after some learning on group theory, the math shows that the number of symmetrically unique states is actually much lower than expected!

The way we approach this is to realize that the number of possible states is not too large, which allows for a simple BFS search algorithm. This will be discussed in the next section.
In terms of possible initial states we have: $16 \cdot {16 \choose 6} = 128128$
This value can be reduced by a factor of 16, since starting with an uncolored cube, it does not matter where the cube is.
Second, we aren't interested in positions that are symmetric (through reflections and rotations). 
So let's eliminate them, and enumerate positions using the [Burnside lemma](https://en.wikipedia.org/wiki/Burnside%27s_lemma). The final count equals $1051$ unique states.

As a conclusion, we can use this fact and precompute solutions for all possible game states and it won't hurt our memory.

## Algorithm

Let's construct directed graph of this game. Each node will be representing some state of the game (including current coloring of grid, position of cube and colors on the cube itself). Each directed edge from one state to another will represent possibility of moving between this states (each state has at most $4$ neighbors, so graph isn't dense).

Then using BFS on so build graph, we can calculate (for example) distance to each state from initial one. That's even better, because now we can find optimal solution! And this is description of above approach:

 1. Create queue containing starting state
 2. Repeat while solved state aren't found
 3. Take first state from queue and mark as visited
 4. For each achievable next state, push it on queue (if next state is unvisited already)

### Implementation
An example solution may look like this one:

<img src="https://raw.githubusercontent.com/michal-stachurski/rolling-cube/main/example/solution.gif" width="250" height="250">

My approach for the optimal solution looks like:

<img src="https://user-images.githubusercontent.com/60647115/210168448-c440d7ea-a00f-4313-b7dd-317cb10fdd0f.gif" width="300" height="300">
