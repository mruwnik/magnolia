import math
import pytest

from magnolia.math.geometry import (
    length, dot_product, cross_product, vect_diff, vect_mul, approx_equal,
    norm_angle, are_intersecting, cycle_ring,
)


@pytest.mark.parametrize('v1, v2, dot', (
    ([1, 3, -5], [4, -2, -1], 3),
    ([1, 2, 3], [1, 5, 7], 32),
    ([0, 0, 0, 0, 0], [1, 1, 1], 0),
    ([1] * 23, [1, 1, 1], 3),
))
def test_dot_product(v1, v2, dot):
    """Check whether dot products are correctly calculated."""
    assert dot_product(v1, v2) == pytest.approx(dot)


@pytest.mark.parametrize('v1, v2, cross', (
    ((2, 3, 4), (5, 6, 7), (-3, 6, -3)),
    ((1, 2, 3), (1, 5, 7), (-1, -4, 3)),
    ((-1, -2, 3), (4, 0, -8), (16, 4, 8)),
))
def test_cross_product(v1, v2, cross):
    """Test whether cross products are correctly calculated."""
    a, b, c = cross_product(v1, v2)
    assert cross[0] == pytest.approx(a)
    assert cross[1] == pytest.approx(b)
    assert cross[2] == pytest.approx(c)


@pytest.mark.parametrize('v1, v2, out', (
    ((1, 1, 1), (1, 1, 1), [0, 0, 0]),
    ((2, 1, -1), (1, 1, 1), [1, 0, -2]),
    ((2, 1, -1, 1233), (1, 1, 1), [1, 0, -2]),
))
def test_vect_diff(v1, v2, out):
    """Check whether subtracting vectors works."""
    assert vect_diff(v1, v2) == out


@pytest.mark.parametrize('v1, scalar, out', (
    ((1, 1, 1), 2, [2, 2, 2]),
    ((2, 1, -1), 3, [6, 3, -3]),
    ((2, 1, -1, 2, 3.1), 3, [6, 3, -3, 6, 9.3]),
    ((2, 1, -1), 0, [0, 0, 0]),
))
def test_vect_mul(v1, scalar, out):
    """Check whether multiplying a vector by a scalar works."""
    assert vect_mul(v1, scalar) == out


@pytest.mark.parametrize('vector, leng', (
    ((1,), 1),
    ((1, 1), math.sqrt(2)),
    ((5, 3), math.sqrt(25 + 9)),
    ((4, 3), 5),
    ((1, 1, 1), 1.73205),
    ((2, 1, 2), 3),
    ((2, -14, 5), 15),
))
def test_length(vector, leng):
    """Check whether calculating vector lengths works."""
    assert length(vector) == pytest.approx(leng)


@pytest.mark.parametrize('a, b, diff', (
    (1, 1.00000001, 0.001),
    (1, 1, 0.00000001),
    (2, 3, 1.1),
))
def test_approx_equal(a, b, diff):
    """Check that appropriately equal numbers are deemed so."""
    assert approx_equal(a, b, diff)


@pytest.mark.parametrize('a, b, diff', (
    (1, 1.1, 0.001),
    (1.0000001, 1, 0.00000001),
    (2, 3, 1),
))
def test_approx_equal_not(a, b, diff):
    """Check that appropriately unequal numbers are deemed so."""
    assert not approx_equal(a, b, diff)


@pytest.mark.parametrize('angle, normed', (
    (0, 0), (math.pi - 0.0001, math.pi - 0.0001), (-math.pi + 0.0001, -math.pi + 0.0001),
    (math.pi + 0.0001, -math.pi - 0.0001), (-math.pi - 0.0001, math.pi + 0.0001),
    (21*math.pi, -math.pi), (22*math.pi, 0), (19*math.pi, -math.pi), (-19*math.pi, -math.pi),
    (123, -2.6637)
))
def test_norm_angle(angle, normed):
    """Check whether normalizing angles works."""
    assert approx_equal(norm_angle(angle), normed)


@pytest.mark.parametrize('c1, c2', (
    ((1, 1, 0.5), (1, 2, 0.6)),
    ((0, 0, 1), (1, 1, 1)),
    ((math.pi, 0, 0.5), (-math.pi, 0, 0.5)),
))
def test_are_intersecting(c1, c2):
    """Check whether the 2 provided circles intersect,"""
    assert are_intersecting(c1, c2)


@pytest.mark.parametrize('c1, c2', (
    ((1, 1, 0.5), (1, 20, 0.6)),
    ((0, 0, 1), (2, 2, 1)),
))
def test_are_intersecting_not(c1, c2):
    """Check whether the 2 provided circles don't intersect,"""
    assert not are_intersecting(c1, c2)


@pytest.mark.parametrize('ring, n, expected', (
    ([(0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1)], 1, [[3, 0, 1], (0, 0, 1), (1, 0, 1), (2, 0, 1)]),
    ([(0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1)], 2, [[2, 0, 1], [3, 0, 1], (0, 0, 1), (1, 0, 1)]),
    ([(0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1)], 5, [[3, 0, 1], [0, 0, 1], [1, 0, 1], [2, 0, 1]]),

    # check what happens with pi values
    ([(0, 0, 1), (1, 0, 1), (2, 0, 1), (math.pi, 0, 1)], 1, [[math.pi, 0, 1], (0, 0, 1), (1, 0, 1), (2, 0, 1)]),
    ([(0, 0, 1), (1, 0, 1), (2, 0, 1), (math.pi + 1, 0, 1)], 1,
     [[-math.pi + 1, 0, 1], (0, 0, 1), (1, 0, 1), (2, 0, 1)]),
))
def test_cycle_ring(ring, n, expected):
    """Test whether cycling rings works correctly."""
    assert cycle_ring(ring, n) == expected
