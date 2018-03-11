import math
from typing import List, Tuple, Iterable


class FrontError(ValueError):
    """Raised when a valid front can't be constructed."""


def approx_equal(a: float, b: float, diff=0.001) -> bool:
    """Check whether the 2 values are appropriately equal."""
    return abs(a - b) < diff


def norm_angle(angle):
    """Normalize the given angle (wrapping around π)."""
    return ((angle + math.pi) % (2 * math.pi) - math.pi)


def dot_product(v1: Iterable, v2: Iterable) -> float:
    """Calculate the dot products of the provided vectors.

    If the vectors have different lengths, the extra values will be discarded from the longer one.
    """
    return sum(i*j for i, j in zip(v1, v2))


def vect_diff(v1: Iterable, v2: Iterable) -> List[float]:
    """Subtract the provided vectors from each other.

    If the vectors have different lengths, the extra values will be discarded from the longer one.
    """
    return [i - j for i, j in zip(v1, v2)]


def vect_mul(v: Iterable, scalar: float) -> List[float]:
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


def length(vector: Iterable) -> float:
    """Return the length of the provided vector."""
    return math.sqrt(sum(i**2 for i in vector))


def cylin_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate the distance between the given points, in cylinder coords."""
    return length((norm_angle(p1[0] - p2[0]), p1[1] - p2[1]))


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
        diff = (norm_angle(bud.angle - tx), bud.height - ty, bud.radius - tz)

        cone_dist = dot_product(diff, dir_vec)
        if cone_dist < 0:
            return False

        radius = r * cone_dist / h
        orth_dist = length(vect_diff(diff, vect_mul(dir_vec, cone_dist)))
        return orth_dist < radius

    return in_cone


def first_gap(circles: List[Tuple[float, float, float]], radius: float) -> Tuple[float, float]:
    """
    Return the first available gap that will fit a circle of the given radius.

    This simply loops around the circles, sorted by x, and whenever the distance between
    2 circles is larger than 2*radius it deems that it's found a hole and returns the (x,y) that lies
    between the 2 circles.
    """
    circles = sorted(circles, key=lambda x: x[0], reverse=True)

    for c1, c2 in zip(circles, circles[1:] + [circles[0]]):
        dist = abs(norm_angle(c1[0] - c2[0]))
        if c1[2] + c2[2] + 2*radius < dist:
            return norm_angle(c1[0] - dist/2), 0


def flat_circle_overlap(
        b1: Tuple[float, float, float], b2: Tuple[float, float, float], r: float) -> Tuple[float, float]:
    """Return the higher overlap of 2 circles that are on the same height."""
    x1, y1, r1 = b1
    x2, y2, r2 = b2

    # there are 2 possible intersections, both with the same x, but with different ys
    x3 = -((r + r1)**2 - (r + r2)**2)/(2 * (x1 + x2))
    y3 = math.sqrt((r + r1)**2 - (x3 - x1))

    return norm_angle(x3), max(y1 + y3, y1 - y3)


def are_intersecting(c1: Tuple, c2: Tuple) -> bool:
    """Check whether the 2 provided circles intersect,"""
    return cylin_distance(c1, c2) < c1[2] + c2[2] - 0.0000001


def check_collisions(circle: Tuple[float, float, float], to_check: List[Tuple]) -> bool:
    """Check whether the given circle overlaps with any in the provided list."""
    return any(are_intersecting(circle, c) for c in to_check)


def closest_circle(
        b1: Tuple[float, float, float], b2: Tuple[float, float, float], radius: float) -> Tuple[float, float]:
    """
    Return the angle and height of a bud with the given radius as close a possible to the given buds.

                     n *
                      /   \
                    / phi   \
        n_b1   /             \  n_b2
                /                  \
              /                       \
       b1  * -------------------------* b2
                        b1_b2

    This can be reduced to the intersection of 2 circles at b1 and b2, with radiuses of
    b1,radius + radius and b2.radius + radius
    """
    x1, y1, r1 = b1
    x2, y2, r2 = b2

    n_b1 = r1 + radius
    n_b2 = r2 + radius

    # the dist between the 2 buds should be r1 + r2, but do it manually just in case
    b1_b2 = cylin_distance(b1, b2)

    # check if the circles are in the same place
    if approx_equal(b1_b2, 0):
        return None

    a = (n_b1**2 - n_b2**2 + b1_b2**2) / (2 * b1_b2)
    if n_b1 < abs(a):
        h = 0
    else:
        h = math.sqrt(n_b1**2 - a**2)

    midx = x1 + a * norm_angle(x2 - x1)/b1_b2
    midy = y1 + a * (y2 - y1)/b1_b2

    x3_1 = midx + h*(y2 - y1)/b1_b2
    y3_1 = midy - h*norm_angle(x2 - x1)/b1_b2

    x3_2 = midx - h*(y2 - y1)/b1_b2
    y3_2 = midy + h*norm_angle(x2 - x1)/b1_b2

    if y3_1 > y3_2:
        return norm_angle(x3_1), y3_1, radius
    return norm_angle(x3_2), y3_2, radius


def highest_left(circles, checked: Tuple[float, float, float]) -> Tuple[float, float, float]:
    for c in circles:
        if norm_angle(c[0] - checked[0]) > 0:
            return c
    raise FrontError


def touching(circle: Tuple[float, float, float], circles: Iterable[Tuple]) -> List[Tuple]:
    """Return all circles that are touching the provided one."""
    return [c for c in circles if cylin_distance(c, circle) < c[2] + circle[2] + 0.1 and c != circle]


def front(circles: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
    """
    Given a list of circles, return their current front.

    From https://doi.org/10.5586/asbp.3533: "a front is a zigzagging ring of
    primordia encircling the cylinder, each primordium being tangent to one on its left and
    one on its right. Moreover, any primordium above the front must be higher than any
    primordium of the front."

    :param list circles: the collection of circles to be checked
    :returns: the front
    """
    if not circles:
        return []

    # sort the circles by height
    circles = sorted(circles, key=lambda c: c[1], reverse=True)

    highest = circles[0]

    def left(checked):
        neighbours = touching(checked, circles)
        c = highest_left(neighbours, checked)

        if c and c != highest:
            return [checked] + left(c)
        return [checked]

    try:
        return left(highest)
    except FrontError:
        return None


def cycle_ring(ring: List[Tuple], n: int) -> List[Tuple]:
    """
    Rotate the given ring of circles by n circles.

    This function assumes that the ring is sorted by angle.
    """
    if n > 1:
        ring = cycle_ring(ring, n - 1)

    lastx, lasty, lastr = ring[-1]
    first = ring[0]

    if abs(lastx - first[0]) > math.pi:
        first = [lastx - 2 * math.pi, lasty, lastr]
    else:
        first = [lastx, lasty, lastr]
    return [first] + ring[:-1]
