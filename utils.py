import matplotlib.pyplot as plt
import numpy as np


def plot_particles(sub_box_particles, sub_box_dim=5, box_size=50):
    """
    Plot the particles in a 50x50 grid with sub-boxes highlighted, using two colorblind-friendly colors.

    Parameters:
    - sub_box_particles: dict, keys are sub-box indices (0 to 24), values are np.ndarray with shape (N, 2).
    - sub_box_dim: Dimension of the sub-box grid (default is 5 for a 5x5 grid).
    - box_size: Size of the entire box (default is 50).
    """
    plt.figure(figsize=(8, 8))

    colors = ['#0072B2', '#D55E00']  # Blue and orange

    for box, particles in sub_box_particles.items():
        if len(particles) > 0:
            plt.scatter(
                particles[:, 0], particles[:, 1],
                s=5, alpha=0.7, color=colors[box % 2], label=f'Sub-box {box + 1}' if box < 2 else None
            )

    sub_box_size = box_size / sub_box_dim
    for i in range(1, sub_box_dim):

        plt.axvline(i * sub_box_size, color='black', linestyle='--', linewidth=0.5)
        plt.axhline(i * sub_box_size, color='black', linestyle='--', linewidth=0.5)

    plt.xlim(0, box_size)
    plt.ylim(0, box_size)

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(f'Particle Distribution in a {box_size}x{box_size} Grid')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.show()


def lennard_jones_potential(local_particles, all_particles, LJ_CUTOFF):
    """
    Calculate the Lennard-Jones potential between local_particles and all_particles without using cdist.

    Parameters:
    local_particles (numpy.ndarray): Array of shape (M, 2) with (x, y) positions of local particles.
    all_particles (numpy.ndarray): Array of shape (N-M, 2) with (x, y) positions of all particles.
    LJ_CUTOFF (float): Cutoff distance for Lennard-Jones potential.

    Returns:
    float: Total Lennard-Jones potential.
    """
    potential = 0.0

    for local in local_particles:

        delta1 = all_particles - local
        delta2 = local_particles - local
        
        squared_distances1 = np.sum(delta1**2, axis=1)
        squared_distances2 = np.sum(delta2**2, axis=1)

        within_cutoff1 = np.sqrt(squared_distances1) < LJ_CUTOFF
        within_cutoff2 = np.sqrt(squared_distances2) > 0 # Removes ii point
        
        valid_distances1 = squared_distances1[within_cutoff1]
        valid_distances2 = squared_distances2[within_cutoff2]
        
        inv_dist21 = 1.0 / valid_distances1
        inv_dist22 = 1.0 / valid_distances2
        
        inv_dist61 = inv_dist21 ** 3
        inv_dist62 = inv_dist22 ** 3

        potential += np.sum((inv_dist61 ** 2) - 2 * inv_dist61) + np.sum((inv_dist62 ** 2) - 2 * inv_dist62)


    return 0.5 * potential
