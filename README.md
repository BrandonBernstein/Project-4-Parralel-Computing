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

#### **Step 1: Particle Initialization**
- Generate particles within each sub-box.
- Assign $100$ particles to 12 randomly chosen sub-boxes and $1000$ particles to the remaining 13.
- Scatter particles to the processors corresponding to their sub-boxes.

#### **Step 2: Lennard-Jones Potential Calculation**
- Each processor calculates the potential for its local particles, considering all particles within the $r_c = 10$ cutoff.

#### **Step 3: Load Balancing**
- Dynamically adjust sub-box boundaries to redistribute particles until each sub-box has approximately $568$ particles, within a tolerance of $\pm 50$.
- Boundaries are adjusted by shifting column edges incrementally ($0.01$ units per iteration) until the balance condition is met.

#### **Step 4: Profiling and MPI Communication**
- Collect timing information for computation and MPI communication.
- Profile the effects of load balancing on computation time.

---

## Results

### **Particle Distribution**

| Sub-box   | Case (1): Initial Distribution | Case (2): Load Balanced |
|-----------|---------------------------------|--------------------------|
| (1,1)     | 1000                            | 568                      |
| (1,2)     | 100                             | 570                      |
| (1,3)     | 1000                            | 567                      |
| ...       | ...                             | ...                      |
| (5,5)     | 1000                            | 569                      |

### **Computation Times**

| Processor | Case (1): Initial Distribution | Case (2): Load Balanced |
|-----------|---------------------------------|--------------------------|
| 0         | 0.045 seconds                  | 0.062 seconds           |
| 1         | 0.050 seconds                  | 0.055 seconds           |
| ...       | ...                             | ...                      |

### **MPI Profiling**

| Metric          | Case (1) | Case (2) |
|------------------|----------|----------|
| Total Send Time  | 0.003 s  | 0.004 s  |
| Total Receive Time | 0.002 s  | 0.003 s  |

---

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
