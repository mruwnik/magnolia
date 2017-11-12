import math

from magnolia.meristem import Meristem


def dot_product(v1, v2):
    """Calculate the dot products of the provided vectors.

    If the vectors have different lengths, the extra values will be discarded from the longer one.
    """
    return sum(i*j for i, j in zip(v1, v2))


def vect_diff(v1, v2):
    """Subtract the provided vectors from each other.

    If the vectors have different lengths, the extra values will be discarded from the longer one.
    """
    return [i - j for i, j in zip(v1, v2)]


def vect_mul(v, scalar):
    """Multiply the vector by the scalar."""
    return [i * scalar for i in v]


def cross_product(v1, v2):
    """Return the cross product of the provided 3D vectors."""
    ax, ay, az = v1
    bx, by, bz = v2

    i = ay * bz - az * by
    j = az * bx - ax * bz
    k = ax * by - ay * bx

    return (i, j, k)


def length(vector):
    """Return the length of the provided vector."""
    return math.sqrt(sum(i**2 for i in vector))


def line_distance_check(b1, b2):
    """Return a function that calculates the distance from a line between the provided buds."""
    # the direction vector between the buds
    dir_vector = (b1.norm_angle(b1.angle - b2.angle), b1.height - b2.height, b1.radius - b2.radius)

    def checker(bud):
        # the diff between b1 and bud
        diff = (bud.norm_angle(bud.angle - b1.angle), bud.height - b1.height, bud.radius - b1.radius)

        return length(cross_product(diff, dir_vector)) / length(dir_vector)

    return checker


def in_cone_checker(tip, dir_vec, r, h):
    """
    Return a function that checks whether a bud is in the provided cone.

    The `r` and `h` params describe a sample base - in reality the cone is assumed to be
    infinite. For use in occlusion checks, `tip` should be where the inner tangents of the
    checked bud meet, `dir_vec` should be the vector between them, while `r` and `h` should
    be the scale and height (respectably) of the occluding bud.

    :param tuple tip: the tip of the cone
    :param tuple dir_vec: the direction vector of the cone
    :param float r: a radius at h that describes the cone
    :param float h: a height along the axis which along with `r` describes the cone
    """
    tx, ty, tz = tip

    def in_cone(bud):
        """Return whether the given bud totally fits in the cone."""
        diff = (bud.norm_angle(bud.angle - tx), bud.height - ty, bud.radius - tz)

        cone_dist = dot_product(diff, dir_vec)
        if cone_dist < 0:
            return False

        radius = r * cone_dist / h
        orth_dist = length(vect_diff(diff, vect_mul(dir_vec, cone_dist)))
        return orth_dist < radius

    return in_cone


def middle_point(b1, b2):
    """Find the approximate cutting point of the inner tangents of the provided buds."""
    dir_vector = (b1.norm_angle(b2.angle - b1.angle), b2.height - b1.height, b2.radius - b1.radius)
    line_len = length(dir_vector)

    normed_dir = vect_mul(dir_vector, 1/line_len)

    d1 = (b1.scale * line_len) / (b1.scale + b2.scale)

    return (
        b1.norm_angle(b1.angle + d1 * normed_dir[0]),
        b1.height + d1 * normed_dir[1],
        b1.radius + d1 * normed_dir[2],
    )


def occlusion_cone(b1, b2):
    """Return a function that tests whether a given bud lies in the occlusion cone behind b2 from b1."""
    dir_vector = (b1.norm_angle(b2.angle - b1.angle), b2.height - b1.height, b2.radius - b1.radius)
    apex = middle_point(b1, b2)

    # because of the overwrapping of angles, there is a degenerative case when the cone lies on the angle axis
    if dir_vector[1] == 0 and dir_vector[2] == 0:
        h = length((b1.norm_angle(b2.angle - apex[0]), b2.height - apex[1], b2.radius - apex[2]))
    else:
        h = length(vect_diff((b2.angle, b2.height, b2.radius), apex))
    return in_cone_checker(apex, dir_vector, b2.radius, h)


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
        # discard all buds that are in the occlusion cone for the selected and tested buds
        checker = occlusion_cone(selected, tested)
        filtered = [bud for bud in buds[1:] if not checker(bud)]
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
