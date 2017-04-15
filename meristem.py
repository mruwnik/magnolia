import math

from ui import MultiDrawable, MeshDrawable, OBJReader


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


class Meristem(MultiDrawable):
    def add_bud(self, **kwargs):
        """radius, angle, height, scale=1, fill_colour=None"""
        self.add(Bud(**kwargs))
