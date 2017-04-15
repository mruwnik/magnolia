import array


class Drawable(object):
    """This represents something that can be rendered by OpenGL."""

    def __init__(self, points=None, vertices=None, colours=None, normals=None):
        """Initialise this drawable.

        :param list[tuple] points: a list of points representing the object
        :param list[float] vertices: a list of raw vertices (3 to a point)
        :param list[float] colours: a raw list of colours for each point
        :param normals: a list of normals for each point
        """
        self.points = points
        self.normals = normals

        if self.points:
            self.vertices = array.array('f', [coord for point in self.points for coord in point])
        else:
            self.vertices = vertices

        if not colours and self.vertices:
            colours = array.array('f', [1.0] * len(self.vertices))
        self.colours = colours


class MeshDrawable(object):
    """A container for a model mesh."""

    def __init__(self, mesh):
        """Initialise the object, setting the colour to light gray.

        :param MeshData mesh: the mesh to be rendered.
        """
        self.mesh = mesh
        self.colours = array.array('f', [0.7] * len(self.vertices))

    @property
    def vertices(self):
        """Get a list of raw indecies for this object."""
        return array.array('f', self.mesh.vertices)

    @property
    def normals(self):
        """Get a list of normals from the mesh."""
        return array.array('f', self.mesh.normals)
