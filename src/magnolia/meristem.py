import array
import math
from itertools import count
from contextlib import contextmanager
from typing import List

from PyQt5.QtGui import QVector3D

from magnolia.math.geometry import Sphere
from magnolia.ui import MultiDrawable, MeshDrawable, OBJReader


class MathError(ValueError):
    """Raised when a bad mathematic operation is used."""


def solve_quadratic(a, b, c):
    """Return all solutions for the given quadratic equation."""
    if not a:
        raise MathError('not a quatratic (%s, %s, %s)' % (a, b, c))

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


class Bud(Sphere, MeshDrawable):
    SPHERE_MODEL = OBJReader('sphere.obj').objects['sphere']
    VERTICE_COUNT = int(len(SPHERE_MODEL.vertices)/3)
    NORMALS = array.array('f', SPHERE_MODEL.normals)

    RED = (1, 0, 0)
    GREEN = (0, 0.8, 0)
    BLUE = (0, 0, 0.7)
    WHITE = (1, 1, 1)
    COLOURS = {}
    """A buffer of colour arrays to speed things up (rather than recreate one for each colour change)."""
    ids_generator = count()

    def __init__(self, *args, **kwargs):
        """Initialse this bud, positioning it appropriately upon the meristem.

        :param float radius: how far away the bud is from the center.
        :param float angle: the buds clockwise rotation (in radians) around the meristem. 0 is the far side.
        :param float height: this buds height upon the meristem
        :param MeshData mesh: the mesh used for displaying. The default is a simple sphere
        """
        self.bud_id = next(self.ids_generator)

        kwargs['colours'] = kwargs.pop('fill_colour', self.BLUE)
        if 'mesh' not in kwargs:
            kwargs['mesh'] = self.SPHERE_MODEL
        kwargs.pop('offset', None)
        super(Bud, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Bud (angle=%s, height=%s, radius=%s, scale=%s)' % (self.angle, self.height, self.radius, self.scale)

    def update_pos(self, angle, height, radius, scale):
        """Overwrite the current position with the provided values."""
        self.angle, self.height, self.radius, self.scale = angle, height, radius, scale

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
        return [max(min(int(c * 255), 255), 0) for c in self._colour]

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

    def __hash__(self):
        return self.bud_id


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

    def move_bud(self, bud: Bud, to: Sphere, front: List[Sphere]):
        """Move the given bud to the position at the given sphere."""
        bud.update_pos(to.angle, to.height, to.radius, to.scale)

    @contextmanager
    def buds_mover(self):
        """Get a context manager that will get or create buds that can then be positioned."""
        buds = self.next_or_new()

        def mover(pos, front):
            bud = next(buds)
            self.move_bud(bud, pos, front)

        yield mover

    def next_or_new(self):
        """
        Iterate through all the objects of this collection, and when they are exhausted, yield new buds.

        Existing buds aren't modified in any way, new ones only get registered - no vertice calculations
        or any such things are done.
        """
        for bud in self.displayables:
            yield bud

        while True:
            bud = Bud()
            self.add(bud)
            yield bud

    @property
    def radius(self):
        """Get the actual radius of the meristem.

        The meristem's radius is defined as the max radius of all its buds.
        """
        if not self.objects:
            return 0
        return max(bud.radius for bud in self.objects)

    @property
    def height(self):
        """Get the height of the meristem.

        The meristem's height is defined as the max height of all its buds.
        """
        if not self.objects:
            return 0
        return max(bud.height + bud.scale for bud in self.objects)

    def bounds_test(self, x, y, offset):
        """Check if the provided point intersects with a bud."""
        # there is no point in checking specific buds if the point is outside the boundaries
        # of the meristem
        if -self.radius * math.pi < x < self.radius * math.pi and 0 < y < self.height:
            return super(Meristem, self).bounds_test(x, y, offset)
        return -1
