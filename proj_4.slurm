#!/bin/bash
#
#SBATCH --job-name=proj4
#SBATCH --output=project4_out.txt
#SBATCH --ntasks-per-node=25  # Adjust to available cores
#SBATCH --nodes=1
#SBATCH --time=4:00:00
#SBATCH --partition=short-96core

module load gcc/12.1.0
module load mpi4py/3.0.3

mpirun -np 25 python /gpfs/home/bsbernstein/main.py
mpirun -np 25 python /gpfs/home/bsbernstein/main.py --load_balancing

