import math

from PyQt5.QtGui import QVector3D

from ui import MultiDrawable, MeshDrawable, OBJReader


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

    def select(self):
        """Select this bud."""
        import array
        self.colours = array.array('f', [1, 1, 1] * int(len(self.vertices)/3))

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
