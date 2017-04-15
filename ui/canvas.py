import array

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QMatrix4x4, QOpenGLVersionProfile, QVector3D
from PyQt5 import QtCore


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
        self._vertices = vertices
        if not colours and self.vertices:
            colours = array.array('f', [1.0] * len(self.vertices))
        self.colours = colours
        self.normals = normals

    @property
    def vertices(self):
        """Get a list of raw indecies for this object."""
        if self._vertices:
            return self._vertices
        if self.points:
            return array.array('f', [coord for point in self.points for coord in point])


class OGLCanvas(QOpenGLWidget):
    """A class to handle displaying OpenGL things on the screen."""

    def __init__(self, *args, **kwargs):
        """Initialise a new object."""
        super(OGLCanvas, self).__init__(*args, **kwargs)
        self.objects = []
        self.viewing_angle = [0.0, 0.0]

    def _load_program(self, vertex_shader, fragment_shader):
        """Load the given shader programs."""
        self.program = QOpenGLShaderProgram(self)
        if not self.program.addShaderFromSourceFile(QOpenGLShader.Vertex, vertex_shader):
            raise ImportError('Could not compile %s' % vertex_shader)
        if not self.program.addShaderFromSourceFile(QOpenGLShader.Fragment, fragment_shader):
            raise ImportError('Could not compile %s' % fragment_shader)
        if not self.program.link():
            raise ImportError('Could not link the shader program')

    def initializeGL(self):
        version = QOpenGLVersionProfile()
        self._load_program('ui/shaders/vshader.glsl', 'ui/shaders/fshader.glsl')

        # FIXME: this should check which versions are available and then apply the appropriate one
        version.setVersion(2, 0)
        self.gl = self.context().versionFunctions(version)
        self.gl.initializeOpenGLFunctions()

        self.m_posAttr = self.program.attributeLocation('position')
        self.m_colAttr = self.program.attributeLocation('colour')
        self.m_normAttr = self.program.attributeLocation('normal')
        self.mv_matrixUniform = self.program.uniformLocation('mv_matrix')
        self.p_matrixUniform = self.program.uniformLocation('p_matrix')
        self.norm_matrixUniform = self.program.uniformLocation('norm_matrix')

        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_CULL_FACE)

    def add(self, drawable):
        """Add the provided drawable to the list of objects."""
        self.objects.append(drawable)

    @property
    def p_matrix(self):
        matrix = QMatrix4x4()
        matrix.perspective(60, 4.0/3.0, 0.1, 100.0)
        return matrix

    @property
    def mv_matrix(self):
        """Return the current model-view matrix."""
        matrix = QMatrix4x4()
        matrix.lookAt(QVector3D(0, 0, -10), QVector3D(0, 0, 0), QVector3D(0, 1, 0))
        matrix.translate(0, 0, -2)
        matrix.rotate(self.viewing_angle[0], 0, 1, 0)
        matrix.rotate(self.viewing_angle[1], 1, 0, 0)
        return matrix

    def loadAttrArray(self, attr, array):
        """Load the given array to the provided attribute."""
        self.gl.glVertexAttribPointer(attr, 3, self.gl.GL_FLOAT, False, 0, array)
        self.gl.glEnableVertexAttribArray(attr)

    def paintGL(self):
        """Paint all objects."""
        self.gl.glViewport(0, 0, self.width(), self.height())
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT)

        self.program.bind()
        self.program.setUniformValue(self.mv_matrixUniform, self.mv_matrix)
        self.program.setUniformValue(self.norm_matrixUniform, self.mv_matrix.inverted()[0])
        self.program.setUniformValue(self.p_matrixUniform, self.p_matrix)

        vertices = array.array('f', [])
        colours = array.array('f', [])
        normals = array.array('f', [])
        for obj in self.objects:
            vertices += obj.vertices
            colours += obj.colours
            normals += obj.normals

        self.loadAttrArray(self.m_posAttr, vertices)
        self.loadAttrArray(self.m_colAttr, colours)
        self.loadAttrArray(self.m_normAttr, normals)

        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, len(vertices) / 3)

        self.program.release()

    def move_view(self, x, y):
        """Rotate the current view by the given values on the respective axes."""
        self.viewing_angle = [self.viewing_angle[0] + x, self.viewing_angle[1] + y]

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.NoButton:
            pass
        elif event.buttons() == QtCore.Qt.LeftButton:
            offset = event.pos() - self.mouse_pos
            self.mouse_pos = event.pos()
            self.move_view(offset.x(), offset.y())
        elif event.buttons() == QtCore.Qt.RightButton:
            pass
        super(OGLCanvas, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.pos()
        super(OGLCanvas, self).mousePressEvent(event)
