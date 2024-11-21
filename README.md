# Project Report: Lennard-Jones Potential Computation with Load Balancing

## Problem Description

You are tasked with placing $N = 12 × 100 + 13 × 1000 = 14,200$ particles in a 2D box of dimensions $50 × 50$. The box is divided into $5 × 5$ sub-boxes. Each sub-box contains either $1000$ particles (13 sub-boxes) or $100$ particles (12 sub-boxes), generated randomly within each sub-box.

The particles interact through the Lennard-Jones potential truncated at a cutoff radius $r_c = 10$. The potential between two particles $i$ and $j$ is given by:

$$
V_{ij} =
\begin{cases}
\frac{1}{r_{ij}^{12}} - \frac{2}{r_{ij}^6}, & \text{if } r_{ij} \leq r_c, \\
0, & \text{if } r_{ij} > r_c.
\end{cases}
$$

Where $r_{ij} = \| \mathbf{x}_i - \mathbf{x}_j \|$ is the distance between particles $i$ and $j$. The total energy for particle $i$ is:

$$
V_i = \frac{1}{2} \sum_{j \neq i} V_{ij}.
$$

You are required to:

1. Design algorithms to compute the potential for every particle using 25 processors, assigning one processor per sub-box.
2. Adjust the vertices of the sub-boxes to redistribute particles and achieve approximate load balance, ensuring each sub-box has around $568$ particles.

---

## Program Structure

### File Organization

- `main.py`: Main script for particle initialization, MPI setup, and computation of Lennard-Jones potential.
- `utils.py`: Contains utility functions such as plotting particles and calculating the Lennard-Jones potential.
- `load_balance.py`: Implements the dynamic adjustment of sub-box boundaries to achieve load balance.

### Algorithm Outline

#### **Step 0: Parameter Initialization**
- Declare general variables needed for broadcasting and generation

#### **Step 1: Particle Initialization**
- Generate particles within each sub-box.
- Assign $100$ particles to 12 randomly chosen sub-boxes and $1000$ particles to the remaining 13.
- Broadcast general parameters to processors.
- Scatter particles to processors corresponding to their sub-boxes.

#### **Step 2: Optional Load Balancing**
- Create new boxes by setting an initial column on the left side of the grid. Incrementally expanding that column east until the number of particles contained is within $4\% \pm 0.2\%$. Then set the next column's left boundary to the previous stopping stopping point and repeat. The balance achieved generally makes the maximum load on a single processor 4.2%.

#### **Step 2: All Gather Particles on Each Processor**
- Gather a complete list of all particles in the system (excluding local particles) for calculations against the local particles.

#### **Step 3: Lennard-Jones Potential Calculation**
- Each processor calculates the potential for its local particles, considering all particles within the $r_c = 10$ cutoff.

#### **Step 4: Profiling and MPI Communication**
- Collect timing information for computation and MPI communication.
- Profile the effects of load balancing on computation time.

## Results

### **Particle Distribution**

| Sub-box            | (1,1) | (1,2) | (1,3) | (1,4) | (1,5) | (2,1) | (2,2) | (2,3) | (2,4) | (2,5) | (3,1) | (3,2) | (3,3) | (3,4) | (3,5) | (4,1) | (4,2) | (4,3) | (4,4) | (4,5) | (5,1) | (5,2) | (5,3) | (5,4) | (5,5) |
|--------------------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| # Particles: Case (1) | 100   | 100   | 100   | 1000  | 1000  | 100   | 1000  | 1000  | 100   | 100   | 1000  | 100   | 100   | 100   | 1000  | 1000  | 100   | 1000  | 100   | 1000  | 1000  | 1000  | 100  | 100  | 1000   |
| Time: Case (1)     | 0.07  | 0.05  | 0.06  | 0.51  | 0.62  | 0.06  | 0.51  | 0.51  | 0.06  | 0.06  | 0.64  | 0.06  | 0.06  | 0.07  | 0.5   | 0.52  | 0.06  | 0.51  | 0.53  | 0.63  | 0.51  | 0.51  | 0.06  | 0.06  | 0.51  |
| # Particles: Case (2) | 572   | 570   | 570   | 561   | 576   | 565   | 571   | 575   | 564   | 560   | 558   | 558   | 573   | 565   | 575   | 568   | 574   | 568   | 570   | 572   | 566   | 560   | 576   | 562   | 571   |
| Time: Case (2)     | 0.31  | 0.31  | 0.31  | 0.41  | 0.31  | 0.31  | 0.31  | 0.31  | 0.38  | 0.31  | 0.31  | 0.38  | 0.40  | 0.31  | 0.30  | 0.31  | 0.38  | 0.31  | 0.31  | 0.31  | 0.31  | 0.31  | 0.31  | 0.30  | 0.29  |



## Analysis of Results

1. **Initial vs. Balanced Distribution**: 
    - In the initial case, heavily populated sub-boxes resulted in computational bottlenecks for the corresponding processors.
    - Load balancing reduced these disparities, leading to a more even distribution of particles across processors.

2. **Impact on Computation Time**:
    - While load balancing improved particle distribution, communication overhead increased due to the dynamic adjustment of boundaries.
    - The total computation time showed a slight increase in the balanced case due to higher boundary synchronization costs.

3. **Potential Optimization**:
    - Reducing the number of load-balancing iterations.
    - Optimizing the boundary adjustment algorithm to minimize communication overhead.

---

## Instructions for Execution

### Requirements
- **MPI**: Install `mpi4py` using `pip install mpi4py`.
- **Python Dependencies**: Install `numpy` and `matplotlib`.

### Execution
1. Run the program using `mpirun` or `mpiexec` with 25 processors:
   ```bash
   mpirun -n 25 python main.py
