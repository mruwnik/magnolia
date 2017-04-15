import array
from ui import MeshDrawable, OBJReader


class Meristem(MeshDrawable):
    SPHERE_MODEL = OBJReader('sphere.obj').objects['sphere']
    def __init__(self, *args, **kwargs):
        super(Meristem, self).__init__(mesh=self.SPHERE_MODEL)
