import math

from PyQt5.QtGui import QVector3D

from ui import MultiDrawable, MeshDrawable, OBJReader


def perendicular_line(b1, b2):
    """Get a line function that is perendicular to the line between the 2 buds.

    The resulting function goes through b2' center. An offset that moves the line behind
    b2 (away from b1) is also returned.

    :param Bud b1: the first bud
    :param Bud b2: the second bud
    :rtype: (function, float)
    :return: the line function and an offset
    """
    m = (b2.height - b1.height) / b1.angle2x(b2.angle - b1.angle)
    x = b1.angle2x(b2.angle - b1.angle)
    line = lambda b: -1 / m * b.angle2x(b.angle - b1.angle) + b1.height
    offset = (b2.scale + abs(x)) * x/abs(x)
    return line, offset


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
    sqrd = math.sqrt(worldxp**2 + (yp - b)**2 - r**2)
    absd = abs(worldxp**2 + (yp - b)**2)
    x1 = ((r**2) * worldxp + r * (yp - b) * sqrd) / (absd * b1.radius)
    x2 = ((r**2) * worldxp - r * (yp - b) * sqrd) / (absd * b1.radius)

    y1 = ((r**2) * (yp - b) - r * worldxp * sqrd) / absd + b
    y2 = ((r**2) * (yp - b) + r * worldxp * sqrd) / absd + b

    left = lambda b: ((yp - y1) * b.angle2x(b.angle - b1.angle - x1)) / b.angle2x(xp - x1) + y1
    right = lambda b: ((yp - y2) * b.angle2x(b.angle - b1.angle - x2)) / b.angle2x(xp - x2) + y2
    return left, right


def get_reachable(selected, buds):
    """Filter the given buds for all that can be accessed by the selected bud without collisions.

    :param Bud selected: The selected bud
    :param list buds: all available buds
    :returns: a list of accessible buds.
    """
    if not buds:
        return []

    tested, offset = buds[0], 0

    # Check whether the 2 bud circles are intersecting
    if selected.distance(tested) <= selected.scale + tested.scale:
        # the circles are intersecting, so get a line perendicular to the tested bud. Any buds
        # behind the line are discarded. An offset it used to move the line a bit backwards, as
        # otherwise the check is a bit too strict
        (left, offset), right = perendicular_line(selected, tested), lambda b: b.height
    else:
        # The circles are disjoint - get the inner tangents of the 2 circles - any point that
        # lies behind the tested bud, but between the 2 tangents can be safely discarded.
        left, right = inner_tangents(selected, tested)

    # filter out any buds that cannot be accessed without any collisions. The `if` magic below
    # is because checking if a point lies above or below the `left` and 'right` lines is dependant
    # on where the tested point lies relative to the selected bud.
    # WARNING! Any modifications of the following code should be thoroughly tested!
    filtered = []
    for bud in buds[1:]:
        if left(tested) >= tested.height:
            if right(tested) >= tested.height:
                if left(bud) >= bud.height + offset and right(bud) >= bud.height:
                    continue
            elif left(bud) >= bud.height + offset and right(bud) < bud.height:
                continue
        elif left(bud) < bud.height + offset:
            if right(tested) >= tested.height:
                if right(bud) >= bud.height:
                    continue
            elif right(bud) < bud.height:
                continue
        filtered.append(bud)
    return [tested] + get_reachable(selected, filtered)


def solve_quadratic(a, b, c):
    """Return all solutions for the given quadratic equation."""
    discr = b * b - 4 * a * c
    if discr < 0:
        return None, None
    elif discr == 0:
        x = - 0.5 * b / a
        return (x, x)
    elif b > 0:
        q = -0.5 * (b + math.sqrt(discr))
    else:
        q = -0.5 * (b - math.sqrt(discr))
    x0, x1 = q / a, c / q
    return (x0, x1) if x0 > x1 else (x1, x0)


class Bud(MeshDrawable):
    SPHERE_MODEL = OBJReader('sphere.obj').objects['sphere']

    def __init__(self, *args, **kwargs):
        """Initialse this bud, positioning it appropriately upon the meristem.

        :param float radius: how far away the bud is from the center.
        :param float angle: the buds clockwise rotation around the meristem. 0 is the far side.
        :param float height: this buds height upon the meristem
        :param MeshData mesh: the mesh used for displaying. The default is a simple sphere
        """
        self.radius = kwargs.pop('radius', 1)
        self.angle = math.radians(-kwargs.pop('angle', 0))
        self.height = kwargs.pop('height', 0)

        if 'mesh' not in kwargs:
            kwargs['mesh'] = self.SPHERE_MODEL
        kwargs.pop('offset', None)
        super(Bud, self).__init__(*args, **kwargs)

    @property
    def offset(self):
        """Calculate the buds offset from the meristems origin.

        The bud is positioned on a simple circle on the XZ axis, so
        simple trigonometry does the trick.
        """
        x = math.sin(self.angle) * self.radius
        z = math.cos(self.angle) * self.radius
        return (x, self.height, z)

    def angle2x(self, angle):
        """Return the given angle in pseudo 2D coordinates.

        In these coordinates, x is the bud's angle, while y is its height. To make calculations
        work, the angle has to be scaled by the radius. Otherwise 2 buds with the same angle would
        have the same x value, regardless of their radius. This would mean that there would be no way
        to e.g. check which is wider.
        """
        return ((angle + math.pi) % (2 * math.pi) - math.pi) * self.radius

    def distance(self, bud):
        """Calculate the distance between this bud and the provided one."""
        return math.sqrt(self.angle2x(self.angle - bud.angle)**2 + (self.height - bud.height)**2)

    def select(self):
        """Select this bud."""
        return self

    def ray_pick_test(self, origin, direction):
        """Check whether the given ray intersects this object.

        :param QVector3D origin: the camera position
        :param QVector3D direction: the direction vector. This MUST be normalized.
        :returns: the distance to the closest point of this object along the ray. Negative values if no intersection
        """
        L = origin - QVector3D(*self.offset)
        t0, t1 = solve_quadratic(
            1, 2 * QVector3D.dotProduct(direction, L), QVector3D.dotProduct(L, L) - self.scale**2
        )
        if t0 is None or (t0 <= 0 and t1 <= 0):
            return -1
        elif t0 > 0 and t0 < t1:
            return t0
        else:
            return t1


class Meristem(MultiDrawable):
    def add_bud(self, **kwargs):
        """radius, angle, height, scale=1, fill_colour=None"""
        self.add(Bud(**kwargs))

    def closest(self, bud):
        """Get all buds, sorted by their proximity to the provided bud.

        The provided bud is not in the resulting list.
        """
        buds = sorted(self.objects, key=lambda b: bud.distance(b))
        return buds[1:]
