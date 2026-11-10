"""FTCS demonstration with the original boundary stencil and source timing."""

import numpy as np


def ftcs_step(u, u_new, alpha, dt, dx=1.0, dy=1.0):
    nx, ny = u.shape

    rx = alpha * dt / (dx * dx)
    ry = alpha * dt / (dy * dy)

    for i in range(nx):
        for j in range(ny):
            u_xx = 0.0
            u_yy = 0.0

            if i == 0:
                u_xx = u[i + 1, j] - u[i, j]
            elif i == nx - 1:
                u_xx = u[i - 1, j] - u[i, j]
            else:
                u_xx = u[i + 1, j] - 2 * u[i, j] + u[i - 1, j]

            if j == 0:
                u_yy = u[i, j + 1] - u[i, j]
            elif j == ny - 1:
                u_yy = u[i, j - 1] - u[i, j]
            else:
                u_yy = u[i, j + 1] - 2 * u[i, j] + u[i, j - 1]

            u_new[i, j] = u[i, j] + rx * u_xx + ry * u_yy

    return u_new


def apply_heat_source(u, source_temp, source_x, source_y, source_size):
    half_size = source_size // 2
    x_start = max(0, source_x - half_size)
    x_end = min(u.shape[0], source_x + half_size + 1)
    y_start = max(0, source_y - half_size)
    y_end = min(u.shape[1], source_y + half_size + 1)

    u[x_start:x_end, y_start:y_end] = source_temp


def simulate(
    initial,
    *,
    alpha,
    dt,
    num_steps,
    source_temp,
    source_x,
    source_y,
    source_size,
    sample_steps,
    include_initial=False
):
    u = initial.copy()
    u_new = np.zeros_like(u)
    snapshots = [u.copy()] if include_initial else []
    for step in range(num_steps):
        u_new = ftcs_step(u, u_new, alpha, dt)
        apply_heat_source(u_new, source_temp, source_x, source_y, source_size)
        u, u_new = u_new, u
        if step in sample_steps:
            snapshots.append(u.copy())
    return snapshots
