import math
from typing import List, Tuple, Iterable


class FrontError(ValueError):
    """Raised when a valid front can't be constructed."""


class Sphere(object):
    """Represent a sphere in cylindrical coords."""

    def __init__(self, angle=0, height=0, radius=1, scale=3, **kwargs):
        """
        Initialise the sphere.

        :param float angle: the angle by which the sphere is rotated around the cylinder
        :param float height: the height of the sphere on the cylinder
        :param float radius: the radius of the cylinder
        :param float scale: the radius of the sphere
        """
        self.angle = angle
        self.height = height
        self.radius = radius
        self.scale = scale
        super().__init__(**kwargs)

    @staticmethod
    def cyl_to_cart(angle, height, radius):
        """Convert the given cylinderic point to a cartesian one."""
        x = math.sin(angle) * radius
        z = math.cos(angle) * radius
        return (x, height, z)

    @property
    def offset(self):
        """Calculate the buds offset from the meristems origin.

        The bud is positioned on a simple circle on the XZ axis, so
        simple trigonometry does the trick.
        """
        return self.cyl_to_cart(self.angle, self.height, self.radius)

    @staticmethod
    def norm_angle(angle):
        """Normalize the given angle (wrapping around π)."""
        return norm_angle(angle)

    def angle2x(self, angle):
        """Return the given angle in pseudo 2D coordinates.

        In these coordinates, x is the bud's angle, while y is its height. To make calculations
        work, the angle has to be scaled by the radius. Otherwise 2 buds with the same angle would
        have the same x value, regardless of their radius. This would mean that there would be no way
        to e.g. check which is wider.
        """
        return self.norm_angle(angle) * self.radius

    def distance(self, bud):
        """Calculate the distance between this bud and the provided one."""
        return math.sqrt(self.angle2x(self.angle - bud.angle)**2 + (self.height - bud.height)**2)

    def opposite(self, b1, b2):
        """Check whether the given buds are on the opposite sides of this bud.

        This checks to a precision of 1% of the radius.
        """
        angles_diff = abs(self.angle2x(b1.angle - self.angle) + self.angle2x(b2.angle - self.angle))
        height_diff = abs(abs(b1.height + b2.height)/2 - abs(self.height))
        return angles_diff < self.radius / 100 and height_diff < self.radius / 100

    def bounds_test(self, angle, h, offset):
        """Check whether the provided point lies in this bud.

        This is a 2D test, for use when a meristem is rolled out.
        """
        dist = self.angle2x(angle / self.radius - offset[0] - self.angle)**2 + (h - self.height)**2
        if dist < self.scale**2:
            return math.sqrt(dist)
        return -1

    def __repr__(self):
        return '<Sphere (angle=%s, height=%s, radius=%s, scale=%s)' % (self.angle, self.height, self.radius, self.scale)


def by_height(circles: List[Sphere], reversed=True):
    """Return the given circles sorted by height."""
    return sorted(circles, key=lambda c: c.height, reverse=reversed)


def by_angle(circles: List[Sphere], reversed=True):
    """Return the given circles sorted by angle."""
    return sorted(circles, key=lambda c: c.angle, reverse=reversed)


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


def first_gap(circles: List[Sphere], radius: float) -> Tuple[float, float]:
    """
    Return the first available gap that will fit a circle of the given radius.

    This simply loops around the circles, sorted by x, and whenever the distance between
    2 circles is larger than 2*radius it deems that it's found a hole and returns the (x,y) that lies
    between the 2 circles.
    """
    circles = by_angle(circles)

    for c1, c2 in zip(circles, circles[1:] + [circles[0]]):
        dist = abs(norm_angle(c1.angle - c2.angle))
        if c1.scale + c2.scale + 2*radius < dist:
            return norm_angle(c1.angle - dist/2), 0


def flat_circle_overlap(
        b1: Tuple[float, float, float], b2: Tuple[float, float, float], r: float) -> Tuple[float, float]:
    """Return the higher overlap of 2 circles that are on the same height."""
    x1, y1, r1 = b1
    x2, y2, r2 = b2

    # there are 2 possible intersections, both with the same x, but with different ys
    x3 = -((r + r1)**2 - (r + r2)**2)/(2 * (x1 + x2))
    y3 = math.sqrt((r + r1)**2 - (x3 - x1))

    return norm_angle(x3), max(y1 + y3, y1 - y3)


def are_intersecting(c1: Sphere, c2: Sphere) -> bool:
    """Check whether the 2 provided circles intersect,"""
    return c1.distance(c2) < c1.scale + c2.scale - 0.0000001


def check_collisions(circle: Sphere, to_check: List[Sphere]) -> bool:
    """Check whether the given circle overlaps with any in the provided list."""
    return any(are_intersecting(circle, c) for c in to_check)


def closest_circle(b1: Sphere, b2: Sphere, radius: float) -> Sphere:
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
    x1, y1, r1 = b1.angle, b1.height, b1.scale
    x2, y2, r2 = b2.angle, b2.height, b2.scale

    n_b1 = r1 + radius
    n_b2 = r2 + radius

    # the dist between the 2 buds should be r1 + r2, but do it manually just in case
    b1_b2 = b1.distance(b2)

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
        return Sphere(norm_angle(x3_1), y3_1, scale=radius)
    return Sphere(norm_angle(x3_2), y3_2, scale=radius)


def highest_left(circles: List[Sphere], checked: Sphere) -> Sphere:
    for c in circles:
        if norm_angle(c.angle - checked.angle) > 0:
            return c
    raise FrontError


def touching(circle: Sphere, circles: Iterable[Sphere], precision: float=0.1) -> List[Sphere]:
    """Return all circles that are touching the provided one."""
    return [c for c in circles if circle.distance(c) < c.scale + circle.scale + precision and c != circle]


def front(circles: List[Sphere]) -> List[Sphere]:
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
    circles = by_height(circles)
    highest = circles[0]
    seen = set()

    def left(checked):
        neighbours = touching(checked, circles)
        c = highest_left(neighbours, checked)

        if c and c != highest and c not in seen:
            # sometimes a proper front can't be constructed coz a bud has no left neighbours
            # so to stop infinite recursions, stop when a bud is found more than once
            seen.add(c)
            return [checked] + left(c)
        return [checked]

    try:
        return left(highest)
    except FrontError:
        return None


def cycle_ring(ring: List[Sphere], n: int) -> List[Sphere]:
    """
    Rotate the given ring of circles by n circles.

    This function assumes that the ring is sorted by angle.
    """
    if n > 1:
        ring = cycle_ring(ring, n - 1)

    last = ring[-1]
    first = ring[0]

    if abs(last.angle - first.angle) > math.pi:
        first = Sphere(last.angle - 2 * math.pi, last.height, scale=last.scale)
    else:
        first = last
    return [first] + ring[:-1]
