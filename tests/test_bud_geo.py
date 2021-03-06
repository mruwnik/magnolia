import math
import pytest

from magnolia.math.geometry import in_cone_checker
from magnolia.math.bud_geo import (
    linear_function, line_distance_check, perendicular_plane_checker, middle_point
)
from magnolia.meristem import Bud


def make_bud(angle=0.123, height=1, radius=3, scale=1):
    return Bud(angle=angle, radius=radius, height=height, scale=scale)


@pytest.mark.parametrize('b1, b2, b3, dist', (
    # along the X axis
    (make_bud(0, 0, 0), make_bud(0, 1, 0), make_bud(0, 2, 0), 0),
    (make_bud(0, 0, 0), make_bud(0, 1, 0), make_bud(0, -12, 0), 0),
    (make_bud(0, 0, 0), make_bud(0, 1, 0), make_bud(1, 0, 0), 1),
    (make_bud(0, 0, 0), make_bud(0, 1, 0), make_bud(1, 2, 0), 1),

    # along the Y axis
    (make_bud(0, 0, 0), make_bud(1, 0, 0), make_bud(2, 0, 0), 0),
    (make_bud(0, 0, 0), make_bud(1, 0, 0), make_bud(-12, 0, 0), 0),
    (make_bud(0, 0, 0), make_bud(1, 0, 0), make_bud(0, 1, 0), 1),
    (make_bud(0, 0, 0), make_bud(1, 0, 0), make_bud(2, 1, 0), 1),

    # along the Z axis
    (make_bud(0, 0, 0), make_bud(0, 0, 12), make_bud(0, 0, -312), 0),
    (make_bud(0, 0, 0), make_bud(0, 0, 1), make_bud(0, 0, 0), 0),
    (make_bud(0, 0, 0), make_bud(0, 0, 1), make_bud(0, -1, 0), 1),

    # proper functions
    (make_bud(1, 1, 1), make_bud(-1, -1, -1), make_bud(0, 1, 0), math.sqrt(2/3)),
    (make_bud(3, 1, -1), make_bud(5, 2, 1), make_bud(0, 2, 3), 5),
))
def test_line_distance_check(b1, b2, b3, dist):
    """Check whether calculating the distance from a point works."""
    assert line_distance_check(b1, b2)(b3) == pytest.approx(dist)


@pytest.mark.parametrize('bud, is_in', (
    (make_bud(2, 0, 0), True),  # along the axis

    (make_bud(2, 1.99999, 0, scale=1), True),  # just under the cone
    (make_bud(2, 3, 0, scale=1), False),  # on the cone

    # angle wrapping
    (make_bud(math.pi - 0.0001, 2.5, 0), True),
    (make_bud(math.pi, 1, 0), False),

    # outside the cone
    (make_bud(-2, 0, 0), False),  # the opposite direction
    (make_bud(1, 2, 0), False),  # orthogonal
))
def test_in_cone_checker(bud, is_in):
    """Check whether the cone checker works."""
    checker = in_cone_checker((0, 0, 0), (1, 0, 0), 1, 1)
    assert checker(bud) == is_in


@pytest.mark.parametrize('tip, dir_vec, r, h', (
    # cones pointing directly up at it
    ((math.pi/2, 0, 3), (0, 1, 0), 3/2.0, 0.5),
    ((math.pi/2, -1, 3), (0, 2, 0), 2, 1),
    ((math.pi/2, -1, 3), (0, 1, 0), 0.1, 1),  # a really thin cone

    # cones pointing from various directions
    ((0, 0, 0), (1, 1, 1), 2, 1),
    ((10, 10, 10), (-1, -1, -1), 2, 1),
))
def test_in_cone_checker_static_bud(tip, dir_vec, r, h):
    """Check whether various cones find the specified bud."""
    bud = make_bud(angle=math.pi/2, height=1, radius=3, scale=1)
    checker = in_cone_checker(tip, dir_vec, r, h)
    assert checker(bud) is True


@pytest.mark.parametrize('b1, b2, point', (
    # same size - the point should be half way between them
    (make_bud(0, 0, 0), make_bud(2, 0, 0), (1, 0, 0)),
    (make_bud(0, 0, 0), make_bud(-2, 0, 0), (-1, 0, 0)),
    (make_bud(1, 2, 0), make_bud(2, 2, 0), (1.5, 2, 0)),
    (make_bud(0, 10, 10), make_bud(0, 0, 0), (0, 5, 5)),
    (make_bud(1, 1, 1), make_bud(0, 0, 0), (0.5, 0.5, 0.5)),

    # different sizes
    (make_bud(1, 0, 0, scale=1), make_bud(2, 0, 0, scale=2), (4/3., 0, 0)),
    (make_bud(0, 0, 0, scale=1), make_bud(2, 0, 0, scale=2), (2/3., 0, 0)),
    (make_bud(0, 0, 0, scale=1), make_bud(2, 0, 0, scale=9), (2/10., 0, 0)),
    (make_bud(1, 1, 1, scale=9), make_bud(-1, -1, -1, scale=1), (-0.8, -0.8, -0.8)),
))
def test_middle_point(b1, b2, point):
    """Check whether finding the approximate inner tangents crossing works."""
    for i, j in zip(middle_point(b1, b2), point):
        assert i == pytest.approx(j)


Xs = [-361, -270, -180, -120, -90, -60, -15, 0, 15, 30, 45, 60, 90, 120, 180, 270, 360]


@pytest.mark.parametrize('b1, b2, ys', (
    (make_bud(0, 0), make_bud(math.pi, 0), [0] * 18),  # along the X axis
    (make_bud(0, 12), make_bud(math.pi, 12), [12] * 18),  # along the X axis

    # not a valid function
    (make_bud(0, 0), make_bud(0, 1), [10001] * 7 + [1] + [10001] * 10),

    # more interesting functions
    (
        make_bud(0, 0), make_bud(math.radians(1), 1),
        [-1, 90, -180, -120, -90, -60, -15, 0, 15, 30, 45, 60, 90, 120, -180, -90, 0]
    ), (
        make_bud(0, 0), make_bud(math.radians(2), 1),
        [-1/2, 45, -90, -60, -45, -30, -15/2, 0, 15/2, 15, 45/2, 30, 45, 60, -90, -45, 0]
    ), (
        make_bud(0, 0), make_bud(math.radians(1), 2),
        [-2, 180, -360, -240, -180, -120, -30, 0, 30, 60, 90, 120, 180, 240, -360, -180, 0]
    ), (
        make_bud(math.radians(90), 2), make_bud(math.radians(60), 5),
        [11.1, 2.0, -7, -13.0, 20.0, 17.0, 12.5, 11.0, 9.5, 8.0, 6.5, 5.0, 2.0, -1.0, -7.0, 20.0, 11.0]
    ),
))
def test_linear_function(b1, b2, ys):
    """Check whether linear functions are correctly generated."""
    func = linear_function(b1, b2)
    test_bud = make_bud()

    for x, y in zip(Xs, ys):
        test_bud.angle = math.radians(x)
        assert func(test_bud) == pytest.approx(y)


@pytest.mark.parametrize('b1, b2, on_plane', (
    # invalid functions (parallel to the Y-axis)
    (
        make_bud(0, 0), make_bud(math.pi, 0),
        [False, True, True, False, False, False, False, True, True, True, True, True, True, True, True, False, True]
    ),
    (
        make_bud(0, 12), make_bud(math.pi, 12),
        [False, True, True, False, False, False, False, True, True, True, True, True, True, True, True, False, True]
    ),

    # along the X axis
    (make_bud(0, 0), make_bud(0, 1), [True] * 18),
    (make_bud(math.pi/2, 3), make_bud(math.pi/2, 4), [True] * 18),
    (make_bud(math.pi/2, 4), make_bud(math.pi/2, 3), [False] * 18),
    (make_bud(-math.pi/2, 3), make_bud(-math.pi/2, 4), [True] * 18),

    # actual functions
    (
        make_bud(0, 0), make_bud(math.radians(90), 1),
        # actual values:
        # [4.246740, -18.20660, 48.413219, 33.60881, 26.20660, 18.804406, 7.701101, 4.0, 0.29889834,
        # -3.4022033, -7.103304, -10.80440, -18.20660, -25.60881, 48.413219, 26.20660, 4.0]
        [True, True, False, False, True, True, True, True, True, True, True, True, True, False, False, True, True]
    ),
))
def test_perendicular_plane_checker(b1, b2, on_plane):
    """Check whether perendicular planes are correctly checked."""
    func = perendicular_plane_checker(b1, b2)
    test_bud = make_bud()

    for x, is_on in zip(Xs, on_plane):
        test_bud.angle = math.radians(x)
        assert func(test_bud) == is_on
