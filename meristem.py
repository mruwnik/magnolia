import array
from ui import Drawable
from objloader import OBJReader


class Meristem(Drawable):
    def __init__(self, *args, **kwargs):
        reader = OBJReader('sphere.obj')
        mesh = reader.objects['sphere1']
        from itertools import zip_longest
        def grouper(n, iterable, padvalue=None):
            "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
            return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

        super(Meristem, self).__init__(
            points=[gr[:3] for gr in grouper(8, mesh.vertices)],
            vertices=array.array('f', mesh.raw_vertices),
            normals=array.array('f', mesh.normals)
        )
