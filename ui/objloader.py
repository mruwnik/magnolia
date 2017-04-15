from collections import OrderedDict
from path import Path


class MeshData(object):
    VERTEX_FORMAT = OrderedDict((
        ('v_pos', (0, 3)),
        ('v_normal', (3, 3)),
        ('v_tc0', (6, 2)),
    ))
    """A mapping of attributes to their positions in each point"""
    VERTEX_LEN = sum(i[1] for i in VERTEX_FORMAT.values())
    """The total amount of floats per point."""

    def __init__(self, name=None, points=None, indices=None):
        self.name = name
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self.points = points or []
        self.indices = indices or []

    @property
    def vertices(self):
        """Return a flattend list of all vertices."""
        offset, length = self.VERTEX_FORMAT['v_pos']
        return [v for point in self.points for v in point[offset:offset + length]]

    @property
    def normals(self):
        """Return a flattend list of all normals."""
        offset, length = self.VERTEX_FORMAT['v_normal']
        return [v for point in self.points for v in point[offset:offset + length]]

    def calculate_normals(self):
        for i in range(len(self.indices) / (3)):
            fi = i * 3
            v1i = self.indices[fi]
            v2i = self.indices[fi + 1]
            v3i = self.indices[fi + 2]

            vs = self.vertices
            p1 = [vs[v1i + c] for c in range(3)]
            p2 = [vs[v2i + c] for c in range(3)]
            p3 = [vs[v3i + c] for c in range(3)]

            u, v = [0, 0, 0], [0, 0, 0]
            for j in range(3):
                v[j] = p2[j] - p1[j]
                u[j] = p3[j] - p1[j]

            n = [0, 0, 0]
            n[0] = u[1] * v[2] - u[2] * v[1]
            n[1] = u[2] * v[0] - u[0] * v[2]
            n[2] = u[0] * v[1] - u[1] * v[0]

            for k in range(3):
                self.vertices[v1i + 3 + k] = n[k]
                self.vertices[v2i + 3 + k] = n[k]
                self.vertices[v3i + 3 + k] = n[k]


def default_list(items, num, default=None):
    """Return a list of num length, starting with the provided items.

    If default is None, then this raises an exception if the amount of items is less than num.
    """
    if default is None and len(items) < num:
        raise ValueError('not enough items provided for: "%s"' % ' '.join(items))
    return items + ([default] * (num - len(items)))


class OBJReader(object):
    """Parse an *.obj file."""

    def __init__(self, filename, file_path=None):
        """Initialise the object with data from the given file

        :param str/Path filename: the name of the file to be loaded
        :param str/Path file_path: an optional path to the file. If None, the default models dir will be used."""
        if not file_path:
            file_path = Path(__file__).parent / 'models'

        self.filename = Path(file_path) / filename
        self.load_file(self.filename)

    def _clear_lists(self):
        """Clear all data buffors."""
        self.vertices = []
        self.tex_coords = []
        self.normals = []
        self.faces = []
        self._object_name = None

    def _parse_v(self, line):
        """Parse all vertices from the given line.

        There should be 3 or 4 values - if only 3 are provided, w is set to 1.0.
        """
        self.vertices.append(list(map(float, default_list(line, 4, 1.0))))

    def _parse_vt(self, line):
        """Parse all texture vertices from the given line.

        There should be up to 3 values between 0 and 1.0 - the default is 0.
        """
        self.tex_coords.append(list(map(int, default_list(line, 3, 0))))

    def _parse_vn(self, line):
        """Parse all normal vertices from the given line.

        There should be 3 floats.
        """
        self.normals.append(list(map(float, default_list(line, 3))))

    def _parse_face_point(self, point):
        """Parse a single face point.

        The format is <vertice index>/<texture index>/<normal index> and only the first one is required.
        """
        def int_or_none(val):
            return int(val) if val else None

        v, t, n = (point + '///').split('/')[:3]
        return [int(v), int_or_none(t), int_or_none(n)]

    def _parse_f(self, line):
        """Parse a face line.

        A face consists of 3 <vertice index>/<texture index>/<normal index> tuples, where only the first
        item in each tuple is required.
        """
        self.faces.append(list(map(self._parse_face_point, line)))

    def _parse_o(self, line):
        """Parse an object line.

        This means a new object, so start off by adding the previously processed object to the list of objects.
        """
        obj = self.add_mesh(self._object_name, self.vertices, self.tex_coords, self.normals, self.faces)
        self._clear_lists()
        self._object_name = ' '.join(line) or None

    def _noop(self, *args):
        """Do nothing - if a non recognized command is found."""
        pass

    def add_mesh(self, name, vertices, tex_coords, normals, faces):
        """Add a new mesh object on the basis of the provided data."""
        if not faces:
            return

        def values(source, index, amount=3):
            """Return the data at the provided index, or a list of 0 if none available."""
            if index is None or len(source) < index:
                return [0.0] * amount
            else:
                return source[index - 1][:amount]

        mesh = MeshData(
            name=name,
            points=[
                values(vertices, v) + values(normals, n) + values(tex_coords, t, 2) for points in faces for v, t, n in points
            ],
            indices=list(range(len(faces) * 3))
        )
        self.objects[name] = mesh
        return mesh

    def load_file(self, filename):
        """Load all objects from the given file."""
        self.objects = {}
        self._clear_lists()
        for line in open(filename):
            parts = line.split()
            getattr(self, '_parse_' + parts[0], self._noop)(parts[1:])
        self._parse_o([])
