from mpi4py import MPI
import numpy as np
from utils import plot_particles, lennard_jones_potential
from load_balance import adjust_column_slices
import time
import argparse
import csv

parser = argparse.ArgumentParser(description="Run MPI simulation with graph and load balancing options.")
parser.add_argument('--graph', action='store_true', help="Enable particle graph plotting.")
parser.add_argument('--load_balancing', action='store_true', help="Enable load balancing for particles.")

args = parser.parse_args()
graph = args.graph
load_balancing = args.load_balancing

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

BOX_SIZE = 50
SUB_BOX_DIM = 5
N_SUB_BOXES = SUB_BOX_DIM ** 2
PARTICLES_SMALL = 100
PARTICLES_LARGE = 1000
LJ_CUTOFF = 10.0
LJ_CUTOFF_SQUARED = LJ_CUTOFF ** 2

scatter_time = 0.0
gather_time = 0.0
bcast_time = 0.0
computation_time = 0.0

if rank == 0:
    np.random.seed(42)
    small_boxes = np.random.choice(N_SUB_BOXES, 12, replace=False)
    large_boxes = [i for i in range(N_SUB_BOXES) if i not in small_boxes]

    sub_box_particles = {i: [] for i in range(N_SUB_BOXES)}
    particle_counts = np.zeros(N_SUB_BOXES, dtype=int)

    for box in range(N_SUB_BOXES):
        x_start = (box % SUB_BOX_DIM) * (BOX_SIZE / SUB_BOX_DIM)
        y_start = (box // SUB_BOX_DIM) * (BOX_SIZE / SUB_BOX_DIM)
        x_end = x_start + (BOX_SIZE / SUB_BOX_DIM)
        y_end = y_start + (BOX_SIZE / SUB_BOX_DIM)

        num_particles = PARTICLES_SMALL if box in small_boxes else PARTICLES_LARGE
        particle_counts[box] = num_particles

        x_coords = np.random.uniform(x_start, x_end, num_particles)
        y_coords = np.random.uniform(y_start, y_end, num_particles)

        sub_box_particles[box] = np.column_stack((x_coords, y_coords))

    if graph:
        plot_particles(sub_box_particles)


    if load_balancing:
        all_particles = np.vstack(list(sub_box_particles.values()))

        print("Balancing particles across column slices...")
        column_boundaries, column_indices = adjust_column_slices(all_particles, N_SUB_BOXES)

        sub_box_particles = {i: all_particles[indices] for i, indices in enumerate(column_indices)}

        if graph:
            print("Particle distribution after load balancing:")
            plot_particles(sub_box_particles)


    # Prepare the data for scattering: each processor gets particles from its assigned sub-box
    partitioned_particles = [sub_box_particles[i] for i in range(size)]
    # Prepare the data for scattering: each processor gets particles from its assigned sub-box
    partitioned_particles = [sub_box_particles[i] for i in range(size)]
else:
    partitioned_particles = None
    particle_counts = np.empty(N_SUB_BOXES, dtype=int)


start_bcast = MPI.Wtime()
comm.Bcast(particle_counts, root=0)
end_bcast = MPI.Wtime()
bcast_time = end_bcast - start_bcast

start_scatter = MPI.Wtime()
local_particles = comm.scatter(partitioned_particles, root=0)
end_scatter = MPI.Wtime()
scatter_time = end_scatter - start_scatter

local_array = np.array(local_particles).reshape((len(local_particles), 2))

local_particle_count = len(local_particles)

start_gather = MPI.Wtime()
all_particles_list = comm.allgather(local_particles)
end_gather = MPI.Wtime()
gather_time = end_gather - start_gather

all_particles = np.vstack([particles for i, particles in enumerate(all_particles_list) if i != rank])

comm.Barrier()
start_time = time.time()

total_potential = lennard_jones_potential(local_particles, all_particles, LJ_CUTOFF)

end_time = time.time()
computation_time = end_time - start_time

# print(f"Rank {rank}: Computed Lennard-Jones potential = {total_potential}")

all_scatter_times = comm.gather(scatter_time, root=0)
all_gather_times = comm.gather(gather_time, root=0)
all_bcast_times = comm.gather(bcast_time, root=0)
all_computation_times = comm.gather(computation_time, root=0)

all_times = comm.gather(computation_time, root=0)
if rank == 0:
    file_name = 'mpi_profiling_results.csv'

    if load_balancing:
        file_name = 'mpi_profiling_results_balanced.csv'

    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = ['Processor', 'Scatter Time (s)', 'Gather Time (s)', 'Bcast Time (s)', 'Computation Time (s)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for i in range(size):
            writer.writerow({
                'Processor': i,
                'Scatter Time (s)': all_scatter_times[i],
                'Gather Time (s)': all_gather_times[i],
                'Bcast Time (s)': all_bcast_times[i],
                'Computation Time (s)': all_computation_times[i]
            })

    print(f"MPI Profiling results have been saved to {file_name}.")

MPI.Finalize()
