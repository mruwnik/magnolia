import math
from typing import List, Tuple, Iterable


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
    circles = sorted(circles, key=lambda x: x[0])
    prev_x, _, prev_rad = circles[0]

    for current_x, __, current_rad in circles[1:] + [circles[0]]:
        dist = abs(norm_angle(prev_x + current_x))
        if prev_rad + current_rad + 2*radius < dist:
            return norm_angle(prev_x + dist/2), 0
        prev_x, prev_rad = current_x, current_rad


def flat_circle_overlap(
        b1: Tuple[float, float, float], b2: Tuple[float, float, float], r: float) -> Tuple[float, float]:
    """Return the higher overlap of 2 circles that are on the same height."""
    x1, y1, r1 = b1
    x2, y2, r2 = b2

    # there are 2 possible intersections, both with the same x, but with different ys
    x3 = -((r + r1)**2 - (r + r2)**2)/(2 * (x1 + x2))
    y3 = math.sqrt((r + r1)**2 - (x3 - x1))

    return norm_angle(x3), max(y1 + y3, y1 - y3)


def closest_bud(b1: Tuple[float, float, float], b2: Tuple[float, float, float], radius: float) -> Tuple[float, float]:
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
    n_b1 = b1[2] + radius
    n_b2 = b2[2] + radius
    b1_b2 = b1[2] + b2[2]

    x1, y1, r1 = b1
    x2, y2, r2 = b2

    # check that the given circles are actually touching
    if n_b1 + n_b2 < cylin_distance(b1, b2):
        return norm_angle((b1[0] + b2[0]) / 2), (b1[1] + b2[1]) / 2

    a = (n_b1**2 - n_b2**2 + b1_b2**2) / (2 * b1_b2)
    h = math.sqrt(n_b1**2 - a**2)

    midx = x1 + a * (x2 - x1)/b1_b2
    midy = y1 + a * (y2 - y1)/b1_b2

    x3_1 = midx + h*(y2 - y1)/b1_b2
    y3_1 = midy - h*(x2 - x1)/b1_b2

    x3_2 = midx - h*(y2 - y1)/b1_b2
    y3_2 = midy + h*(x2 - x1)/b1_b2

    if y3_1 > y3_2:
        return norm_angle(x3_1), y3_1
    return norm_angle(x3_2), y3_2
