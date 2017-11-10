import array
import math
from itertools import count

from PyQt5.QtGui import QVector3D

from magnolia.ui import MultiDrawable, MeshDrawable, OBJReader


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
    VERTICE_COUNT = int(len(SPHERE_MODEL.vertices)/3)
    NORMALS = array.array('f', SPHERE_MODEL.normals)

    RED = (1, 0, 0)
    GREEN = (0, 0.8, 0)
    BLUE = (0, 0, 0.7)
    WHITE = (1, 1, 1)
    COLOURS = {}
    """A buffer of colour arrays to speed things up (rather than recreate one for each colour change)."""

    def __init__(self, *args, **kwargs):
        """Initialse this bud, positioning it appropriately upon the meristem.

        :param float radius: how far away the bud is from the center.
        :param float angle: the buds clockwise rotation around the meristem. 0 is the far side.
        :param float height: this buds height upon the meristem
        :param MeshData mesh: the mesh used for displaying. The default is a simple sphere
        """
        self.ids_generator = count()
        self.bud_id = next(self.ids_generator)
        self.radius = kwargs.pop('radius', 1)
        self.angle = math.radians(-kwargs.pop('angle', 0))
        self.height = kwargs.pop('height', 0)

        kwargs['colours'] = kwargs.pop('fill_colour', self.WHITE)
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

    @property
    def normals(self):
        """Get a list of normals from the mesh."""
        return self.NORMALS

    @property
    def colours(self):
        """Get an array of colours for each vertex."""
        return self.COLOURS.get(self._colour)

    @colours.setter
    def colours(self, colour):
        """Set the colour of each vertex to the given color."""
        self._colour = tuple(colour) or self.WHITE
        if self._colour not in self.COLOURS:
            self.COLOURS[self._colour] = array.array('f', self._colour * self.VERTICE_COUNT)

    @property
    def html_colour(self):
        """Return the colour mapped to [0-255]"""
        return [int(c * 255) for c in self._colour]

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

    def opposite(self, b1, b2):
        """Check whether the given buds are on the opposite sides of this bud.

        This checks to a precision of 1% of the radius.
        """
        angles_diff = abs(self.angle2x(b1.angle - self.angle) + self.angle2x(b2.angle - self.angle))
        height_diff = abs(abs(b1.height + b2.height)/2 - abs(self.height))
        return angles_diff < self.radius / 100 and height_diff < self.radius / 100

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

    def bounds_test(self, angle, h, offset):
        """Check whether the provided point lies in this bud.

        This is a 2D test, for use when a meristem is rolled out.
        """
        dist = self.angle2x(angle / self.radius - offset[0] - self.angle)**2 + (h - self.height)**2
        if dist < self.scale**2:
            return math.sqrt(dist)
        return -1


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

    @property
    def radius(self):
        """Get the actual radius of the meristem.

        The meristem's radius is defined as the max radius of all its buds."""
        return max(bud.radius for bud in self.objects)

    @property
    def height(self):
        """Get the height of the meristem.

        The meristem's height is defined as the max height of all its buds."""
        return max(bud.height + bud.scale for bud in self.objects)

    def bounds_test(self, x, y, offset):
        """Check if the provided point intersects with a bud."""
        # there is no point in checking specific buds if the point is outside the boundaries
        # of the meristem
        if -self.radius * math.pi < x < self.radius * math.pi and 0 < y < self.height:
            return super(Meristem, self).bounds_test(x, y, offset)
        return -1
