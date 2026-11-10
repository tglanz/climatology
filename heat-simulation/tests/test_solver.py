import numpy as np

from heat_simulation.solver import ftcs_step, apply_heat_source, simulate


def test_impulse_on_rectangular_grid():
    field = np.zeros((3, 4))
    field[1, 2] = 1.0
    expected = np.array(
        [[0.0, 0.0, 0.1, 0.0], [0.0, 0.1, 0.6, 0.1], [0.0, 0.0, 0.1, 0.0]]
    )
    result = ftcs_step(field, np.zeros_like(field), 1.0, 0.1)
    np.testing.assert_allclose(result, expected, rtol=0, atol=1e-15)
    np.testing.assert_array_equal(field[1], [0.0, 0.0, 1.0, 0.0])


def test_uniform_field_and_boundary_flux():
    uniform = np.full((3, 5), 7.0)
    np.testing.assert_array_equal(
        ftcs_step(uniform, np.zeros_like(uniform), 0.1, 0.2), uniform
    )
    corner = np.zeros((3, 5))
    corner[0, 0] = 1.0
    result = ftcs_step(corner, np.zeros_like(corner), 1.0, 0.1)
    assert result[0, 0] == 0.8
    assert result[1, 0] == 0.1
    assert result[0, 1] == 0.1
    assert result.sum() == 1.0


def test_source_clipping_and_update_timing():
    initial = np.zeros((3, 5))
    clipped = initial.copy()
    apply_heat_source(clipped, 5.0, 0, 0, 3)
    expected = initial.copy()
    expected[:2, :2] = 5.0
    np.testing.assert_array_equal(clipped, expected)
    samples = simulate(
        initial,
        alpha=1.0,
        dt=0.1,
        num_steps=2,
        source_temp=5.0,
        source_x=0,
        source_y=0,
        source_size=1,
        sample_steps=[0, 1],
        include_initial=True,
    )
    np.testing.assert_array_equal(samples[0], initial)
    assert samples[1][0, 0] == 5.0
    assert samples[1].sum() == 5.0
    assert samples[2][0, 0] == 5.0
    assert samples[2][1, 0] == 0.5
    assert samples[2][0, 1] == 0.5
    np.testing.assert_array_equal(initial, np.zeros((3, 5)))
