import pytest

from magnolia.positioners import Positioner


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
