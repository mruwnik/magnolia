import math

from magnolia.meristem import Meristem


def length(vector):
    """Return the length of the provided vector."""
    return math.sqrt(sum(i**2 for i in vector))


def line_distance_check(b1, b2):
    """Return a function that calculates the distance from a line between the provided buds."""
    # the direction vector between the buds
    a, b, c = b1.norm_angle(b1.angle - b2.angle), b1.height - b2.height, b1.radius - b2.radius

    def checker(bud):
        # the diff between b1 and bud
        xd, yd, zd = bud.norm_angle(bud.angle - b1.angle), bud.height - b1.height, bud.radius - b1.radius

        # the cross product of the diff x dir_vector
        i = yd * c - zd * b
        j = xd * c - zd * a
        k = xd * b - yd * a

        return length((i, j, k))/length((a, b, c))

    return checker


def linear_function(b1, b2):
    """Get a linear function that goes through the given buds.

    This only works correctly when both are the same distance from the stella (i.e. they
    have the same radius).
    """
    if not b1.angle2x(b2.angle - b1.angle):
        # Handle invalid height linear functions.
        # As these functions are used to check if a bud is on a line, it suffices
        # to return the height of the given bud when the angle is the same, and in
        # other situations to return something that is totally off
        return lambda bud: bud.height if bud.angle == b1.angle else bud.height + 10000
    m = (b2.height - b1.height) / b1.angle2x(b2.angle - b1.angle)
    return lambda bud: m * bud.angle2x(bud.angle - b1.angle) + b1.height


def perendicular_line(b1, b2):
    """Get a line function that is perendicular to the line between the 2 buds.

    The resulting function goes through b2' center + an offset that moves the line behind
    b2 (away from b1).

    :param Bud b1: the first bud
    :param Bud b2: the second bud
    :rtype: function
    :return: the line function
    """
    if b1.angle2x(b2.angle - b1.angle) == 0:
        sign = (b1.height - b2.height)/abs(b1.height - b2.height)
        return lambda bud: b2.height + sign * b2.scale/2

    m = (b2.height - b1.height) / b1.angle2x(b2.angle - b1.angle)
    x = b1.height - b2.height
    # invalid linear function, as the perendicular line to these 2 buds would be
    # parallel to the Y-axis
    if not x:
        x = m = 10.0 ** 8

    offset = b2.scale * 4 * x/abs(x)
    return lambda b: -1 / m * b.angle2x(b.angle - b1.angle) + b1.height - offset


def inner_tangents(b1, b2):
    """Get the inner tangents between the given buds.

    :param Bud b1: the first bud
    :param Bud b2: the second bud
    :rtype: (function, function)
    returns: line functions representing the tangents
    """
    xp = (b1.angle2x(b2.angle - b1.angle) * b1.scale) / ((b1.scale + b2.scale) * b1.radius)
    yp = (b2.height * b1.scale + b1.height * b2.scale) / (b1.scale + b2.scale)

    worldxp, b, r = b1.angle2x(xp), b1.height, b1.scale
    try:
        sqrd = math.sqrt(worldxp**2 + (yp - b)**2 - r**2)
    except ValueError:
        sqrd = 0
    absd = abs(worldxp**2 + (yp - b)**2)
    x1 = ((r**2) * worldxp + r * (yp - b) * sqrd) / (absd * b1.radius)
    x2 = ((r**2) * worldxp - r * (yp - b) * sqrd) / (absd * b1.radius)

    y1 = ((r**2) * (yp - b) - r * worldxp * sqrd) / absd + b
    y2 = ((r**2) * (yp - b) + r * worldxp * sqrd) / absd + b

    def left(b):
        xdiff = b.angle2x(xp - x1)
        if xdiff == 0:
            xdiff = 0.00001
        return ((yp - y1) * b.angle2x(b.angle - b1.angle - x1)) / xdiff + y1

    def right(b):
        xdiff = b.angle2x(xp - x2)
        if xdiff == 0:
            xdiff = 0.00001
        return ((yp - y2) * b.angle2x(b.angle - b1.angle - x2)) / xdiff + y2

    return left, right


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
    if selected.distance(tested) <= selected.scale + tested.scale:
        # the circles are intersecting, so get a line perendicular to the tested bud. Any buds
        # behind the line are discarded. An offset it used to move the line a bit backwards, as
        # otherwise the check is a bit too strict
        left = perendicular_line(selected, tested)
        for bud in buds[1:]:
            if selected.height < tested.height:
                if left(bud) < bud.height:
                    continue
            elif left(bud) >= bud.height:
                continue
            filtered.append(bud)
    else:
        # The circles are disjoint - get the inner tangents of the 2 circles - any point that
        # lies behind the tested bud, but between the 2 tangents can be safely discarded.
        left, right = inner_tangents(selected, tested)

        # filter out any buds that cannot be accessed without any collisions. The `if` magic below
        # is because checking if a point lies above or below the `left` and 'right` lines is dependant
        # on where the tested point lies relative to the selected bud.
        # WARNING! Any modifications of the following code should be thoroughly tested!
        for bud in buds[1:]:
            if left(tested) >= tested.height:
                if right(tested) >= tested.height:
                    if left(bud) >= bud.height and right(bud) >= bud.height:
                        continue
                elif left(bud) >= bud.height and right(bud) < bud.height:
                    continue
            elif left(bud) < bud.height:
                if right(tested) >= tested.height:
                    if right(bud) >= bud.height:
                        continue
                elif right(bud) < bud.height:
                    continue
            filtered.append(bud)
    return [tested] + get_reachable(selected, filtered)


class BudGraph(Meristem):
    """Represents a graph of all buds."""

    def __init__(self, *args, **kwargs):
        super(BudGraph, self).__init__(*args, **kwargs)
        self.nodes = {}

    def add(self, *args):
        """Add the provided items."""
        super(BudGraph, self).add(*args)
        for bud in args:
            self.add_node(bud)

    def add_node(self, bud):
        """Add the given node to the graph, refreshing any previous connections that may get disrupted."""
        neighbours = get_reachable(bud, self.closest(bud))
        self.nodes[bud] = neighbours
        # For most cases it should suffice to simply append the new bud to the list of
        # neighbours of each of its neighbours. This will fail if the new node is between
        # 2 other nodes. In that case both of them won't see each other, but will see the
        # new node, so everything should be ok
        for neighbour in neighbours:
            self.nodes[neighbour] = get_reachable(neighbour, self.closest(neighbour))

    def neighbours(self, bud):
        """Get a list of all buds that can be reached by the provided bud."""
        return self.nodes[bud]

    def axes(self, bud):
        """Yield functions describing all possible axes through the given bud.

        A axis is defined as any line that goes through a bud and at least 2 of its neighbours.
        """
        paired = []
        neighbours = self.neighbours(bud)
        for i, neighbour in enumerate(neighbours):
            if neighbour in paired:
                continue
            for checked in neighbours[i + 1:]:
                if bud.opposite(neighbour, checked):
                    paired += [neighbour, checked]
                    yield linear_function(neighbour, checked)

    def on_line(self, line):
        """Get all buds that are on the given line."""
        return [b for b in self.objects if round(line(b) - b.height, 5) == 0]
