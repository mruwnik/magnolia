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

    def __init__(self, mesh, offset=None, scale=1, fill_colour=None):
        """Initialise the object, setting the colour to light gray.

        :param MeshData mesh: the mesh to be rendered.
        :param [x, y, z] offset: the whole mesh will be translated by the given values
        :param list fill_colour: a 3 part colour list. Each part should be between 0.0 and 1.0
        """
        self.mesh = mesh
        self._offset = offset or (0, 0, 0)
        self.scale = scale
        if not fill_colour:
            fill_colour = [0.7, 0.7, 0.7]
        self.colours = array.array('f', fill_colour * int(len(self.vertices)/3))

    @property
    def offset(self):
        """Get this objects offset from the origin."""
        return self._offset

    @property
    def vertices(self):
        """Get a list of raw indecies for this object.

        Each point is transformed by the objects translation offset and scale
        """
        return array.array('f', [
            ver * self.scale + self.offset[i % 3]
            for i, ver in enumerate(self.mesh.vertices)
        ])

    @property
    def normals(self):
        """Get a list of normals from the mesh."""
        return array.array('f', self.mesh.normals)


class MultiDrawable(object):
    """Handle multiple drawables as a single object."""

    def __init__(self, objects=None):
        """Initialise the collection with a list of objects."""
        self.objects = objects or []
        self.calculate_lists()

    def add(self, *items):
        """Append the provided items to the list of items."""
        self.objects += items
        self.calculate_lists()

    def concat(self, field):
        """Return a float array containing all the values found in the given field.

        :param str field: the name of the property to be accessed
        """
        values = array.array('f', [])
        for obj in self.objects:
            values += getattr(obj,field)
        return values

    def calculate_lists(self):
        """Calculate lists of data to be rendered.

        This is as an optimalisation - the operations are very slow,
        and only needed when new data is added, so it might as well be buffored.
        """
        self.vertices = self.concat('vertices')
        self.normals = self.concat('normals')
        self.colours = self.concat('colours')
