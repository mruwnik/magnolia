import array

from PyQt5.QtCore import QObject, pyqtSignal


class Drawable(QObject):
    """This represents something that can be rendered by OpenGL."""

    needsRefresh = pyqtSignal(str)
    """Signal that something has changed and so the signaled object should refresh the given field (None for all)."""

    def __init__(self, points=None, vertices=None, colours=None, normals=None):
        """Initialise this drawable.

        :param list[tuple] points: a list of points representing the object
        :param list[float] vertices: a list of raw vertices (3 to a point)
        :param list[float] colours: a raw list of colours for each point
        :param normals: a list of normals for each point
        """
        super(Drawable, self).__init__()
        self.points = points
        self._normals = normals

        if self.points:
            self._vertices = array.array('f', [coord for point in self.points for coord in point])
        else:
            self._vertices = vertices

        if not colours and self.vertices:
            colours = array.array('f', [1.0] * len(self.vertices))
        self.colours = colours

    @property
    def vertices(self):
        return self._vertices

    @property
    def normals(self):
        return self._normals

    @normals.setter
    def normals(self, normals):
        self._normals = normals

    def ray_pick_test(self, origin, direction):
        """Return the distance from the given point to its nearest point on this object.

        Negative values mean that there was no intersection.
        """
        return -1

    def select(self):
        """Select this object"""
        return self


class MeshDrawable(Drawable):
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
        super(MeshDrawable, self).__init__(colours=array.array('f', fill_colour * int(len(self.vertices)/3)))

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


class MultiDrawable(Drawable):
    """Handle multiple drawables as a single object."""

    def __init__(self, *args, **kwargs):
        """Initialise the collection with a list of objects."""
        self.objects = kwargs.pop('objects', [])
        super(MultiDrawable, self).__init__(*args, **kwargs)

        self.selected = []
        self.calculate_lists()

    def add(self, *items):
        """Append the provided items to the list of items."""
        for item in items:
            item.needsRefresh.connect(self.refresh_field)
        self.objects += items
        self.calculate_lists()

    def concat(self, field):
        """Return a float array containing all the values found in the given field.

        :param str field: the name of the property to be accessed
        """
        values = array.array('f', [])
        for obj in self.objects:
            values += getattr(obj, field)
        return values

    def refresh_field(self, field):
        """Refresh the given field + notify any listeners that the data is stale."""
        if not field:
            self.calculate_lists()
        else:
            setattr(self, field, self.concat(field))

        if field == 'vertices':
            self.points_count = len(self.vertices) / 3

        # notify any listeners
        self.needsRefresh.emit(field)

    def calculate_lists(self):
        """Calculate lists of data to be rendered.

        This is as an optimalisation - the operations are very slow,
        and only needed when new data is added, so it might as well be buffored.
        """
        self._vertices = self.concat('vertices')
        self.normals = self.concat('normals')
        self.colours = self.concat('colours')
        self.points_count = len(self.vertices) / 3

    def ray_pick_test(self, origin, direction):
        """Return the distance from the given point to its nearest point on this object.

        Negative values mean that there was no intersection.
        By default this returns the distance to the nearest object in the whole container.
        """
        smallest_dist, self.selected = -1, None
        for obj in self.objects:
            dist = obj.ray_pick_test(origin, direction)
            if dist > 0 and (dist < smallest_dist or smallest_dist < 0):
                smallest_dist, self.selected = dist, obj
        return smallest_dist

    def select(self):
        """Select this container - if a single object was selected with the mouse, then select that."""
        if self.selected:
            self.selected = self.selected.select()
        return self.selected
