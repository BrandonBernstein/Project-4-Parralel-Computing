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
- `proj_4_run.slurm`: Seawulf batch script

## Run Commands
To run the code use ```mpirun -np 25 python /gpfs/home/bsbernstein/main.py --graph --load_balancing```. The ```--graph``` flag enables the graphing utils seen in this report and ```--load_balancing``` enables the load balance option. To turn either off simply remove the flag from the bash line.

## Algorithm Outline

#### **Step 0: Parameter Initialization**
- Declare general variables needed for broadcasting and generation

#### **Step 1: Particle Initialization**
- Generate particles within each sub-box.
- Assign $100$ particles to 12 randomly chosen sub-boxes and $1000$ particles to the remaining 13.
- Broadcast general parameters to processors.
- Scatter particles to processors corresponding to their sub-boxes.

#### **Step 2: Optional Load Balancing**
- Create new boxes by setting an initial column on the left side of the grid. Incrementally expanding that column east until the number of particles contained is within 4% $\pm$ 0.2%. Then set the next column's left boundary to the previous stopping stopping point and repeat. The balance achieved generally makes the maximum load on a single processor 4.2%.

#### **Step 2: All Gather Particles on Each Processor**
- Gather a complete list of all particles in the system (excluding local particles) for calculations against the local particles.

#### **Step 3: Lennard-Jones Potential Calculation**
- Each processor calculates the distance for its local particles
- Filters all particles outside the $r_c = 10$ cutoff.
- Calculates potential and aggregates values.

#### **Step 4: Profiling and MPI Communication**
- Collect timing information for computation and MPI communication.
- Profile the effects of load balancing on computation time.

## Results

| Sub-box            | (1,1) | (1,2) | (1,3) | (1,4) | (1,5) | (2,1) | (2,2) | (2,3) | (2,4) | (2,5) | (3,1) | (3,2) | (3,3) | (3,4) | (3,5) | (4,1) | (4,2) | (4,3) | (4,4) | (4,5) | (5,1) | (5,2) | (5,3) | (5,4) | (5,5) |
|--------------------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| # Particles: Case (1) | 100   | 100   | 100   | 1000  | 1000  | 100   | 1000  | 1000  | 100   | 100   | 1000  | 100   | 100   | 100   | 1000  | 1000  | 100   | 1000  | 100   | 1000  | 1000  | 1000  | 100  | 100  | 1000   |
| Time: Case (1)     | 0.07  | 0.05  | 0.06  | 0.51  | 0.62  | 0.06  | 0.51  | 0.51  | 0.06  | 0.06  | 0.64  | 0.06  | 0.06  | 0.07  | 0.5   | 0.52  | 0.06  | 0.51  | 0.53  | 0.63  | 0.51  | 0.51  | 0.06  | 0.06  | 0.51  |
| # Particles: Case (2) | 572   | 570   | 570   | 561   | 576   | 565   | 571   | 575   | 564   | 560   | 558   | 558   | 573   | 565   | 575   | 568   | 574   | 568   | 570   | 572   | 566   | 560   | 576   | 562   | 571   |
| Time: Case (2)     | 0.31  | 0.31  | 0.31  | 0.41  | 0.31  | 0.31  | 0.31  | 0.31  | 0.38  | 0.31  | 0.31  | 0.38  | 0.40  | 0.31  | 0.30  | 0.31  | 0.38  | 0.31  | 0.31  | 0.31  | 0.31  | 0.31  | 0.31  | 0.30  | 0.29  |

In general, we see a decrease in the time taken when load is balanced. When unbalanced the time taken to complete the leonard-jones potential is usually a magnitude higher for 1000 particles versus 100 particles in the sub-box. When balanced we see a 1.56x speed up in computation viewable in the table below.

| Case           | Time (Seconds) | Speed up |
|--------------------|----------|----------|
| Max Balanced      | 0.41     | 1.56   |
| Max Unbalanced    | 0.64     |


## Notes on Efficiency

### Communication
While not shown, broadcasting has a large (~0.3s) increase when load is balanced. As the number of particles in this simulation is quite low, we see any gains from the computational speedup lost from the communication costs associated.

### Adjacent Neighbor Calculations
Ideally, instead of an AllGather, we would like to limit which processors communicate with each other. This could be achieved by seeing which neighboring processors are within the most extreme cut-off distance of the $ith$ processor. Lowering how many distance calculations we need to compute and communication costs. From a geometric perspective, this would benefit the unbalanced case more than the balanced case which is partially why it was not implemented.

### LAMMPS
- LAMMPS or perhaps another library would likely be able to partition the 2d space for load balancing into parallelograms that are more suited for cylindrical optimization. Unfortunately, it would not properly load into my Anaconda env.

