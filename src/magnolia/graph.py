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


def dir_vector(b1, b2):
    """Return a direction vector for the provided buds."""
    return (b1.norm_angle(b1.angle - b2.angle), b1.height - b2.height, b1.radius - b2.radius)


def line_distance_check(b1, b2):
    """Return a function that calculates the distance from a line between the provided buds."""
    # the direction vector between the buds
    dir_vec = dir_vector(b1, b2)

    def checker(bud):
        # the diff between b1 and bud
        diff = (bud.norm_angle(bud.angle - b1.angle), bud.height - b1.height, bud.radius - b1.radius)

        return length(cross_product(diff, dir_vec)) / length(dir_vec)

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
    dir_vec = dir_vector(b1, b2)
    line_len = length(dir_vec)

    normed_dir = vect_mul(dir_vec, 1/line_len)

    d1 = (b1.scale * line_len) / (b1.scale + b2.scale)

    return (
        b1.norm_angle(b1.angle + d1 * normed_dir[0]),
        b1.height + d1 * normed_dir[1],
        b1.radius + d1 * normed_dir[2],
    )


def occlusion_cone(b1, b2):
    """Return a function that tests whether a given bud lies in the occlusion cone behind b2 from b1."""
    dir_vec = dir_vector(b1, b2)
    apex = middle_point(b1, b2)

    # because of the overwrapping of angles, there is a degenerative case when the cone lies on the angle axis
    if dir_vec[1] == 0 and dir_vec[2] == 0:
        h = length((b1.norm_angle(b2.angle - apex[0]), b2.height - apex[1], b2.radius - apex[2]))
    else:
        h = length(vect_diff((b2.angle, b2.height, b2.radius), apex))
    return in_cone_checker(apex, dir_vec, b2.radius, h)


def on_helix_checker(b1, b2):
    """Return a function that checks if a bud lies on the helix going through the provided buds."""
    hdiff = b2.height - b1.height
    adiff = b2.angle - b1.angle

    if b2.height < b1.height:
        hdiff = -hdiff
        adiff = -adiff

    # the buds are on the same height - a circle, not a helix
    if abs(hdiff) < 0.001:
        return lambda b: abs(b.height - b1.height) < 0.001

    # the buds have the same angle - a vertical line, not a helix
    if abs(adiff) < 0.001:
        return lambda b: abs(b.norm_angle(b.angle - b1.angle)) < 0.001

    slope = math.atan(adiff/hdiff)

    def on_helix(b):
        """Check if the provided bud is on the given helix.

        The helix is created as (bud.radius, t - bud.angle, slope*t - bud.height). This
        make things easier, as it's really just the unit helix moved up by the selected
        buds height, moved sideways by the selected buds angle and then streched so that
        it goes through the second bud. The slope is calculated from the tangent of how
        much the helix was moved laterly and vertically.
        """
        angle_diff = b.norm_angle(b.angle - b1.angle)
        height_diff = b.norm_angle(slope * (b.height - b1.height))
        return abs(angle_diff - height_diff) < min(1, abs(slope)) * b.scale

    return on_helix


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


def perendicular_plane_checker(b1, b2):
    """Return a function that checks if a bud is behind the plane perendicular to b2."""
    a, b, c = dir_vector(b1, b2)

    def checker(bud):
        """Return whether this bud is occluded by b2."""
        pl = a * bud.norm_angle(bud.angle - b2.angle) + b * (bud.height - b2.height) + c * (bud.radius - b2.radius)
        return pl >= 0

    return checker


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
# skip the check for now, as it's really slow
#        for neighbour in neighbours:
#            self.nodes[neighbour] = get_reachable(neighbour, self.closest(neighbour))

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
                    yield on_helix_checker(neighbour, checked)

    def on_line(self, line_checker):
        """Get all buds that are on the given line."""
        return filter(line_checker, self.displayables)
