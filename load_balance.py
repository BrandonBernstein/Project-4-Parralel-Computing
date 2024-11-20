import numpy as np


def adjust_column_slices(particles, n_columns):
    """
    Adjust column slices dynamically with fixed boundary shifts until each slice has particles
    within tolerance of the target count (4% ± 0.2% of total particles).
    Includes a fail-safe to stop when the particle percentage exceeds the upper limit
    and ensures the last column extends to the end of the grid.

    Parameters:
    particles (numpy.ndarray): Array of particle coordinates (x, y).
    n_columns (int): Number of column slices (25 in this case).
    tolerance (float): Allowable margin of error (0.2% MOE).

    Returns:
    tuple: Updated column boundaries and indices of particles in each slice.
    """
    total_particles = len(particles)

    target_percentage = 1/n_columns
    target_count = total_particles * target_percentage

    # Allowable margin of error (0.2% MOE)
    margin_of_error = target_count * 0.002
    upper_threshold = target_count + margin_of_error

    column_boundaries = []
    particle_indices = []

    left_boundary = 0.0
    right_boundary = 0.0 + 0.0001

    for col in range(n_columns):
        iteration = 0

        if col == n_columns - 1:
            right_boundary = 50.0
            slice_particles = particles[(particles[:, 0] >= left_boundary) & (particles[:, 0] < right_boundary)]
            slice_count = len(slice_particles)
            percentage = (slice_count / total_particles) * 100
            print(f"Last Column {col + 1}: Final Boundary - "
                  f"Left Boundary: {left_boundary:.2f}, Right Boundary: {right_boundary:.2f}, "
                  f"Percentage of Particles: {percentage:.2f}%")
            column_boundaries.append((left_boundary, right_boundary))
            particle_indices.append(
                np.where((particles[:, 0] >= left_boundary) & (particles[:, 0] < right_boundary))[0])
            break

        while True:

            slice_particles = particles[(particles[:, 0] >= left_boundary) & (particles[:, 0] < right_boundary)]
            slice_count = len(slice_particles)
            percentage = (slice_count / total_particles) * 100

            if abs(slice_count - target_count) <= margin_of_error:
                break

            if slice_count > upper_threshold:
                print(f"Fail-safe triggered! Column {col + 1}: Iteration {iteration} - "
                      f"Left Boundary: {left_boundary:.2f}, Right Boundary: {right_boundary:.2f}, "
                      f"Percentage of Particles: {percentage:.2f}% (Exceeds threshold)")
                break

            right_boundary += 0.01
            iteration += 1

            # Print status at every 250th iteration
            # if iteration % 250 == 0:
            #     print(f"Column {col + 1}: Iteration {iteration} - "
            #           f"Left Boundary: {left_boundary:.2f}, Right Boundary: {right_boundary:.2f}, "
            #           f"Percentage of Particles: {percentage:.2f}%")

        column_boundaries.append((left_boundary, right_boundary))
        particle_indices.append(np.where((particles[:, 0] >= left_boundary) & (particles[:, 0] < right_boundary))[0])

        left_boundary = right_boundary

    return column_boundaries, particle_indices
