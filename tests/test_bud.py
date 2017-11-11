import math
import pytest

from magnolia.meristem import Bud, solve_quadratic, MathError


def make_bud(angle=0.123, height=1, radius=3):
    return Bud(angle=angle, radius=radius, height=height)


@pytest.mark.parametrize('a, b, c', (
    (0, 0, 0),
    (0, 0, 1),
    (0, 1, 0),
    (0, 1, 1),
))
def test_solve_quatratic_errors(a, b, c):
    """Check whether `a` is required."""
    with pytest.raises(MathError):
        solve_quadratic(a, b, c)


@pytest.mark.parametrize('a, b, c, result', (
    (1, 0, 1, (None, None)),  # ∆ < 0
    (1, 1, 1, (None, None)),  # ∆ < 0

    # ∆ == 0
    (1, 2, 1, (-1, -1)),
    (1, 0, 0, (0, 0)),

    # ∆ > 0
    (1, 3, -4, (1, -4)),
    (1, 0, -0.0625, (0.25, -0.25)),
    (6, 11, -35, (5/3, -7/2)),
    (5, 6, 1, (-0.2, -1)),
))
def test_solve_quatratic(a, b, c, result):
    """Check whether quatratics are correctly solved."""
    assert solve_quadratic(a, b, c) == result


@pytest.mark.parametrize('angle, radius, height, offset', (
    (30, 2, 4, (1, 4, math.sqrt(3))),
    (45, 2, 4, (math.sqrt(2), 4, math.sqrt(2))),
    (60, 2, 4, (math.sqrt(3), 4, 1)),
))
def test_bud_offset(angle, radius, height, offset):
    """Check whether calculating the offset works correctly."""
    x, y, z = Bud(angle=math.radians(angle), radius=radius, height=height).offset
    assert x == pytest.approx(offset[0])
    assert y == offset[1]
    assert z == pytest.approx(offset[2])


@pytest.mark.parametrize('radius, angle, angle2x', (
    (1, 1, 1),
    (1, 0, 0),
    (1, 45, 45),
    (2, 45, 45*2),
    (5, 45, 45*5),
    (5, 60, 60*5),

    # check that they get wrapped around 180 degrees
    (1, 181, -179),
    (6, 181, -179*6),
    (1, 359, -1),
    (5, 359, -5),

    # check that they get wrapped
    (5, 360, 0),
    (4, 366, 6*4),
    (4, 400, 40*4),
    (7, 620, -100*7),
    (7, 980, -100*7),
))
def test_bud_angle2x(angle, radius, angle2x):
    """Check whether getting the angle in 2D space works."""
    bud = make_bud(radius=radius)
    assert bud.angle2x(math.radians(angle)) == pytest.approx(math.radians(angle2x))


@pytest.mark.parametrize('angle, height, dist', (
    (1, 0, 3),
    (math.radians(90), 0, 3 * math.pi / 2),
    (math.pi, 0, 3 * math.pi),
    (0.123, 0, 3 * 0.123),
    (0, 1, 1),
    (0.123, 1, math.sqrt((3 * 0.123)**2 + 1)),
    (0.123, 5, math.sqrt((3 * 0.123)**2 + 5**2)),

    (-math.pi, 0, 3 * math.pi),
    (-21 * math.pi, 0, 3 * math.pi),
))
def test_bud_distance(angle, height, dist):
    """Test whether calculating distances works."""
    b1 = Bud(angle=0, height=0, radius=3)
    b2 = Bud(angle=angle, height=height, radius=3)

    assert b1.distance(b2) == pytest.approx(dist)


@pytest.mark.parametrize('b1, b2, b3', (
    (make_bud(0, 0), make_bud(1, 0), make_bud(-1, 0)),
    (make_bud(0, 0), make_bud(0, 1), make_bud(0, -1)),

    (make_bud(math.pi/2, 1), make_bud(0, 1), make_bud(math.pi, 1)),
    (make_bud(-math.pi/2, 1), make_bud(0, 1), make_bud(math.pi*21, 1)),

    (make_bud(math.pi, 1), make_bud(math.pi/2, 0), make_bud(3*math.pi/2, 2)),
))
def test_opposite(b1, b2, b3):
    """Check that testing whether 2 buds are opposite the tested one works."""
    assert b1.opposite(b2, b3)


@pytest.mark.parametrize('b1, b2, b3', (
    (make_bud(0, 0), make_bud(1, 0), make_bud(2, 0)),
    (make_bud(0, 0), make_bud(0, 1), make_bud(0, 2)),

    (make_bud(math.pi/2, 1), make_bud(0, 1), make_bud(math.pi/3, 1)),
    (make_bud(-math.pi/2, 1), make_bud(0, 1), make_bud(2*math.pi/3, 1)),
))
def test_opposite_not(b1, b2, b3):
    """Check that testing whether 2 buds not are opposite the tested one works."""
    assert not b1.opposite(b2, b3)
