import array

from qtpy.QtCore import QObject, Signal, Qt


class Drawable(QObject):
    """This represents something that can be rendered by OpenGL."""

    needsRefresh = Signal(str)
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
        self._normals = normals or array.array('f', [])

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

        Negative values mean that there was no intersection, otherwise the distance to
        the closest item.
        """
        return -1

    def bounds_test(self, x, y, offset):
        """Check whether the provided point lies in the bounds of this instance.

        This is a 2D test.
        """
        return -1

    def select(self):
        """Select this object"""
        return self


class LineDrawable(Drawable):
    """A single straight line."""

    def __init__(self, p1, p2, colour):
        """Setup the line.

        :param tuple p1: the start point of the line
        :param tuple p2: the end point of the line
        :param tuple colour: the colour of the line
        """
        super(LineDrawable, self).__init__(points=[p1, p2], colours=array.array('f', colour * 2))


class MeshDrawable(Drawable):
    """A container for a model mesh."""

    def __init__(self, mesh, offset=None, scale=1, fill_colour=None, colours=None):
        """Initialise the object, setting the colour to light gray.

        :param MeshData mesh: the mesh to be rendered.
        :param [x, y, z] offset: the whole mesh will be translated by the given values
        :param list fill_colour: a 3 part colour list. Each part should be between 0.0 and 1.0
        :param list colours: colours for each vertice
        """
        self.mesh = mesh
        self._offset = offset or (0, 0, 0)
        self.scale = scale
        if not fill_colour:
            fill_colour = [0.7, 0.7, 0.7]
        if not colours:
            colours = array.array('f', fill_colour * int(len(self.vertices)/3))

        super(MeshDrawable, self).__init__(colours=colours)

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
        objects = kwargs.pop('objects', [])
        super(MultiDrawable, self).__init__(*args, **kwargs)

        self.selected = []
        self.objects = []
        self.add(*objects)

    def register_refresh(self, items):
        for item in items:
            item.needsRefresh.connect(self.refresh_field)
        self.calculate_lists()

    def add(self, *items):
        """Append the provided items to the list of items."""
        self.register_refresh(items)
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

    def _test_intersection(self, func, *args, **kwargs):
        """Return the distance from this instance to a point.

        Negative values mean that there was no intersection.
        By default this returns the distance to the nearest object in the whole container.

        :param str func: the name of a test function that can be found in each item
        """
        smallest_dist, self.selected = -1, None
        for obj in self.objects:
            dist = getattr(obj, func)(*args, **kwargs)
            if dist > 0 and (dist < smallest_dist or smallest_dist < 0):
                smallest_dist, self.selected = dist, obj
        return smallest_dist

    def ray_pick_test(self, origin, direction):
        """Return the distance from the given point to its nearest point on this object.

        Negative values mean that there was no intersection.
        By default this returns the distance to the nearest object in the whole container.
        """
        return self._test_intersection('ray_pick_test', origin, direction)

    def bounds_test(self, x, y, offset):
        """Check whether the provided point lies in the bounds of this instance.

        This is a 2D test.
        """
        return self._test_intersection('bounds_test', x, y, offset)

    def select(self):
        """Select this container - if a single object was selected with the mouse, then select that."""
        if self.selected:
            self.selected = self.selected.select()
        return self.selected


class MeristemActions(object):
    """An interface to unify various ways of displaying meristems.

    The main point of this is for various views to be interconnected so
    that modifying one view will be reflected in all other ones.
    """
    drawable_selected = Signal(Drawable, name="drawableSelected")
    view_rotated = Signal(float, float, name="viewRotated")
    refresh_needed = Signal(name="refreshNeeded")

    def __init__(self, *args, **kwargs):
        super(MeristemActions, self).__init__(*args, **kwargs)
        self.objects = MultiDrawable([])
        self.viewing_angle = [0.0, 0.0]

        # set default settings
        self.can_move_camera = True
        self.can_select = True
        self.zoom = 10

    def add(self, drawable):
        """Add the provided drawable to the list of objects."""
        self.objects.add(drawable)

    def register_refresh(self, items):
        self.objects.register_refresh(items)
        self.redraw()

    def redraw(self):
        """Notify the drawer that it should be redrawn."""

    def select(self, event):
        """Select the item that is under the cursor (if enabled)."""

    def allowSelection(self, state):
        self.can_select = state

    def allowMovement(self, state):
        self.can_move_camera = state

    def setZoom(self, value):
        self.zoom = value
        self.redraw()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.NoButton:
            pass
        elif event.buttons() == Qt.LeftButton:
            offset = event.pos() - self.mouse_pos
            self.mouse_pos = event.pos()
            self.view_rotated.emit(offset.x(), offset.y())
        elif event.buttons() == Qt.RightButton:
            pass
        super(MeristemActions, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pos = event.pos()
            self.select(event)
        super(MeristemActions, self).mousePressEvent(event)

    def rotate_view(self, x, y):
        """Rotate the current view by the given values on the respective axes."""
        if self.can_move_camera:
            self.viewing_angle = [self.viewing_angle[0] + x, self.viewing_angle[1] + y]
            self.redraw()
