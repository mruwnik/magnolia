from typing import List, Tuple, Iterable, Callable

from magnolia.meristem import Meristem, Bud
from magnolia.math.bud_geo import occlusion_cone, perendicular_plane_checker, on_helix_checker, helix


def by_height(buds: List[Bud]) -> List[Bud]:
    """Return the given buds sorted by height."""
    return sorted(buds, key=lambda b: b.height, reverse=True)


def get_reachable(selected, buds):  # noqa
    """Filter the given buds for all that can be accessed by the selected bud without collisions.

    :param Bud selected: The selected bud
    :param list buds: all available buds
    :returns: a list of accessible buds.
    """
    if not buds:
        return []

    tested, filtered = buds[0], []

    if tested == selected:
        return buds

    # Check whether the 2 bud circles are intersecting
    if selected.distance(tested) <= selected.scale + tested.scale + 0.0001:
        checker = perendicular_plane_checker(selected, tested)
        filtered = list(filter(checker, buds[1:]))
    else:
        # discard all buds that are in the occlusion cone for the selected and tested buds
        checker = occlusion_cone(selected, tested)
        filtered = [bud for bud in buds[1:] if not checker(bud)]

    return [tested] + get_reachable(selected, filtered)


class BudGraph(Meristem):
    """Represents a graph of all buds."""

    def __init__(self, *args, **kwargs):
        super(BudGraph, self).__init__(*args, **kwargs)
        self.nodes = {}

    def truncate(self, *args):
        super().truncate(*args)
        self.graph()

    def graph(self):
        self.nodes = {}
        for bud in self.displayables:
            self.add_node(bud)

    @property
    def size(self) -> int:
        """Get the amount of buds in the graph."""
        return len(self.drawables)

    def add_node(self, bud: Bud):
        """Add the given node to the graph, refreshing any previous connections that may get disrupted."""
        neighbours = get_reachable(bud, self.closest(bud))
        self.nodes[bud] = neighbours
        # For most cases it should suffice to simply append the new bud to the list of
        # neighbours of each of its neighbours. This will fail if the new node is between
        # 2 other nodes. In that case both of them won't see each other, but will see the
        # new node, so everything should be ok
        for neighbour in neighbours:
            self.nodes[neighbour] = get_reachable(neighbour, self.closest(neighbour))

    def neighbours(self, bud: Bud) -> List[Bud]:
        """Get a list of all buds that can be reached by the provided bud."""
        return self.nodes[bud]

    def axis_checkers(self, bud: Bud) -> Callable[[Bud], bool]:
        """Yield functions describing all possible axes through the given bud.

        A axis is defined as any line that goes through a bud and at least 2 of its neighbours.
        """
        for neighbour, checked in self._paired(bud):
            yield on_helix_checker(neighbour, checked)

    def axes(self, bud: Bud) -> Callable[[float], Tuple[float, float, float]]:
        """Yield functions describing all axes going through the given bud."""
        for neighbour, checked in self._paired(bud):
            yield helix(neighbour, checked)

    def _paired(self, bud: Bud) -> Tuple[Bud, Bud]:
        """Yield all possible axis pairs through the given bud.

        A axis is defined as any line that goes through a bud and at least 2 (the pair) of its neighbours.
        """
        paired = []
        neighbours = self.neighbours(bud)
        for i, neighbour in enumerate(neighbours):
            if neighbour in paired:
                continue
            for checked in neighbours[i + 1:]:
                if bud.opposite(neighbour, checked):
                    paired += [neighbour, checked]
                    yield neighbour, checked

    def on_line(self, line_checker: Callable[[Bud], bool]) -> Iterable[Bud]:
        """Get all buds that are on the given line."""
        return filter(line_checker, self.displayables)

    def touching(self, bud: Bud) -> List[Bud]:
        return [b for b in self.displayables if b != bud and b.distance(bud) < (b.scale + bud.scale)]

    def highest_left(self, bud: Bud) -> Bud:
        for b in by_height(self.displayables):
            if b != bud and b.distance(bud) < (b.scale + bud.scale) * 1.2 and bud.norm_angle(bud.angle - b.angle) > 0:
                return b

    @property
    def front(self) -> List[Bud]:
        """
        Return the current front.

        From https://doi.org/10.5586/asbp.3533: "a front is a zigzagging ring of
        primordia encircling the cylinder, each primordium being tangent to one on its left and
        one on its right. Moreover, any primordium above the front must be higher than any
        primordium of the front."

        :rtype: List[Bud]
        :returns: a list of buds, comprising the current front.
        """
        top = by_height(self.displayables)[0]

        def left(bud):
            b = self.highest_left(bud)
            if b and b != top:
                return [bud] + left(b)
            return [bud]

        return left(top)
