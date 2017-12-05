import math

import pytest

from magnolia.positioners import Positioner, AnglePositioner, RingPositioner


def test_new():
    """Check whether making a new bud works."""
    poser = Positioner()
    bud = poser.new()
    assert bud.radius == Positioner.BASE_RADIUS
    assert bud.height == 1
    assert bud.angle == 0
    assert bud.scale == 1


def test_next_pos():
    """Check whether the base positioner always returns the same positions."""
    poser = Positioner()
    for _ in range(10):
        assert poser._next_pos() == (0, 1, Positioner.BASE_RADIUS, 1)


@pytest.mark.parametrize('objects, item, expected', (
    ([1, 3, 4, 5, 6, 7], 3, [1, 4, 5, 6, 7]),
    ([1, 2, 3, 4], 4, [1, 2, 3]),
    ([1, 2, 3], 'asdasdas', [1, 2, 3]),
    ([], 123, []),
    # only the first item is removed
    ([1, 2, 2, 2, 3], 2, [1, 2, 2, 3])
))
def test_remove(objects, item, expected):
    """Check that removing items works."""
    poser = Positioner()
    poser.objects = objects
    poser.remove(item)

    assert poser.objects == expected


@pytest.mark.parametrize('objects, item, index, expected', (
    ([1, 2, 3], 2, 0, [2, 1, 3]),
    ([1, 2, 3], 2, 1, [1, 2, 3]),
    ([1, 2, 3], 2, 2, [1, 3, 2]),
    ([1, 2, 2, 2, 3], 2, 0, [2, 1, 2, 2, 3]),

    # negative indexes should also work
    ([1, 2, 3, 4, 5, 6], 2, -2, [1, 3, 4, 5, 2, 6]),
    ([1, 2, 3, 4, 5, 6], 5, -3, [1, 2, 3, 5, 4, 6]),

    # index out of bounds - the list remains the same
    ([1, 2, 3], 2, 1232, [1, 2, 3]),
    ([1, 2, 3, 4, 5, 6], 2, -1112, [1, 2, 3, 4, 5, 6]),

    # missing items - insert the item at the given position
    ([1, 2], 123, 1, [1, 123, 2]),
    ([1, 2], 123, -1, [1, 123, 2]),
))
def test_move(objects, item, index, expected):
    """Check whether moving an item works."""
    poser = Positioner()
    poser.objects = objects
    poser.move(item, index)

    assert poser.objects == expected


def test_reposition():
    """Check whether repositioning works."""
    poser = Positioner()
    for i in range(10):
        bud = poser.new()
        bud.radius = bud.height = bud.angle = i
        poser.add(bud)

    for i, bud in enumerate(poser.displayables):
        assert bud.radius == bud.height == bud.angle == i

    poser.recalculate()

    for bud in poser.displayables:
        assert bud.radius == Positioner.BASE_RADIUS
        assert bud.height == 1
        assert bud.angle == 0
        assert bud.scale == 1


@pytest.mark.parametrize('index', (1, 3, 5, 10))
def test_reposition_index(index):
    """Check whether repositioning works when an index is provided."""
    poser = Positioner()
    for i in range(10):
        bud = poser.new()
        bud.radius = bud.height = bud.angle = i
        poser.add(bud)

    poser.recalculate(index)

    for i, bud in enumerate(poser.displayables[:index]):
        assert bud.radius == bud.height == bud.angle == i

    for bud in poser.displayables[index:]:
        assert bud.radius == Positioner.BASE_RADIUS
        assert bud.height == 1
        assert bud.angle == 0
        assert bud.scale == 1


@pytest.mark.parametrize('angle, per_row, angle_step, lat_step', (
    (30, 2, 90, 180),
    (30, 6, 30, 60),
    (30, 36, 5, 10),

    (45, 12, 21.213203, 42.426406),
    (45, 8, 31.8198051, 63.639610),
))
def test_calc_steps_lateral(angle, per_row, angle_step, lat_step):
    """Check whether lateral angles are correctly calculated."""
    poser = AnglePositioner(math.radians(angle), per_row)
    assert math.degrees(poser.lat_step) == pytest.approx(lat_step)
    assert math.degrees(poser.angle_step) == pytest.approx(angle_step)


@pytest.mark.parametrize('angle, per_row, result_angles', (
    (30, 6, [
        1.0471975511965976, 2.0943951023931953, 3.141592653589793, 4.1887902047863905, 5.235987755982988,
        6.283185307179585, 0.5235987755982987, 1.5707963267948963, 2.617993877991494, 3.6651914291880914
    ]),
    (45, 8, [
        1.1107207345395915, 2.221441469079183, 3.3321622036187746, 4.442882938158366, 5.553603672697958,
        0.5553603672697958, 1.6660811018093873, 2.776801836348979, 3.8875225708885703, 4.998243305428161
    ])
))
def test_angle_next_pos(angle, per_row, result_angles):
    """Check whether correct angles are returned."""
    poser = AnglePositioner(math.radians(angle), per_row)
    assert [poser._next_pos()[0] for _ in range(10)] == result_angles


@pytest.mark.parametrize('angle, per_row, height, expected_angles', (
    (0, 3, 2*math.pi, (-120, -240, -360, 0, -120, -240, 0, -120, -240, 0, -120, -240)),
    (20, 3, 6.195304, (-120, -240, -360, 20, -100, -220, 40, -80, -200, 60, -60, -180)),
    (0, 6, math.pi, (
        -60, -120, -180, -240, -300, -360, 0, -60, -120, -180, -240, -300, 0, -60,
        -120, -180, -240, -300, 0, -60, -120, -180, -240, -300
    )),
    (20, 4, 4.59456, (
        -90, -180, -270, -360, 20, -70, -160, -250, 40, -50, -140, -230, 60, -30, -120, -210
    )),
))
def test_ring_angles(angle, per_row, height, expected_angles):
    """Check whether ring positioners return correct positions."""
    poser = RingPositioner(math.radians(angle), per_row)

    heights = [height * i for i in range(4) for row in range(per_row)]
    for angle, height in zip(expected_angles, heights):
        a, h, r, s = poser._next_pos()
        assert math.radians(angle) == pytest.approx(a)
        assert height == pytest.approx(h)
