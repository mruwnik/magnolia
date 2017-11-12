import math
import pytest

from magnolia.graph import linear_function, perendicular_line, length, line_distance_check
from magnolia.meristem import Bud


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


@pytest.mark.parametrize('b1, b2, ys', (
    # invalid functions (parallel to the Y-axis)
    (make_bud(0, 0), make_bud(math.pi, 0), [-4] * 18),
    (make_bud(0, 12), make_bud(math.pi, 12), [12 - 4] * 18),

    # along the X axis
    (make_bud(0, 0), make_bud(0, 1), [0.5] * 18),
    (make_bud(math.pi/2, 3), make_bud(math.pi/2, 4), [4 - 0.5] * 18),
    (make_bud(math.pi/2, 4), make_bud(math.pi/2, 3), [3 + 0.5] * 18),
    (make_bud(-math.pi/2, 3), make_bud(-math.pi/2, 4), [4 - 0.5] * 18),

    # actual functions
    (
        make_bud(0, 0), make_bud(math.radians(90), 1),
        [4.246740, -18.20660, 48.413219, 33.60881, 26.20660, 18.804406, 7.701101, 4.0, 0.29889834,
         -3.4022033, -7.103304, -10.80440, -18.20660, -25.60881, 48.413219, 26.20660, 4.0]
    ),
))
def test_perendicular_line(b1, b2, ys):
    """Check whether perendicular lines get correctly created."""
    func = perendicular_line(b1, b2)
    test_bud = make_bud()

    for x, y in zip(Xs, ys):
        test_bud.angle = math.radians(x)
        assert func(test_bud) == pytest.approx(y)
