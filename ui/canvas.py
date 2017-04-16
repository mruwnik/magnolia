import math

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QMatrix4x4, QOpenGLVersionProfile, QVector3D
from PyQt5 import QtCore

from ui.drawables import MultiDrawable


class OGLCanvas(QOpenGLWidget):
    """A class to handle displaying OpenGL things on the screen."""
    PERSPECTIVE = (60, 0.1, 100.0)
    """The perspective matrix settings (angle, nearZ, farZ)"""

    def __init__(self, *args, **kwargs):
        """Initialise a new object."""
        super(OGLCanvas, self).__init__(*args, **kwargs)
        self.objects = MultiDrawable([])
        self.viewing_angle = [0.0, 0.0]

        # TODO: These are temp variables used for debugging purposes
        self.line_points = None
        self.click_pos = []

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
        self.objects.add(drawable)

    @property
    def viewport_proportions(self):
        """The proportions of the view port."""
        return self.width() / float(self.height())

    @property
    def p_matrix(self):
        """Get the perspective matrix."""
        matrix = QMatrix4x4()
        angle, near, far = self.PERSPECTIVE
        matrix.perspective(angle, self.viewport_proportions, near, far)
        return matrix

    @property
    def view_distance(self):
        """Get the distance from which things should be viewed."""
        return -math.sqrt(self.width() * self.height())/50.0

    @property
    def camera_pos(self):
        """Return the camera's position."""
        return QVector3D(0, 4, self.view_distance)

    @property
    def camera_look_at(self):
        """A point at which the camera is pointed."""
        return QVector3D(0, 4, 0)

    @property
    def camera_normal(self):
        """The camera's up vector."""
        return QVector3D(0, 1, 0)

    @property
    def v_matrix(self):
        """The view matrix in use."""
        matrix = QMatrix4x4()
        matrix.lookAt(self.camera_pos, self.camera_look_at, self.camera_normal)
        return matrix

    @property
    def mv_matrix(self):
        """Return the current model-view matrix."""
        matrix = self.v_matrix
        matrix.rotate(self.viewing_angle[0], 0, 1, 0)
        matrix.rotate(self.viewing_angle[1], 0, 0, 1)
        # matrix.translate(0, -5, 0)
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

        self.loadAttrArray(self.m_posAttr, self.objects.vertices)
        self.loadAttrArray(self.m_colAttr, self.objects.colours)
        self.loadAttrArray(self.m_normAttr, self.objects.normals)

        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.objects.points_count)

        # TODO: Debugging lines to check ray picking
        if self.line_points:
            R = [1, 0, 0]
            G = [0, 1, 0]
            B = [0, 0, 1]
            view_p = [0, 0, self.view_distance]
            x_ax = [10, 0, 0]
            y_ax = [0, 10, 0]
            zero = [0, 0, 0]

            self.loadAttrArray(self.m_posAttr, self.line_points + (zero + view_p) + (zero + x_ax) + (zero + y_ax))
            self.loadAttrArray(self.m_colAttr, [1] * len(self.line_points) + R * 2 + G * 2 + B * 2)
            self.loadAttrArray(self.m_normAttr, [0.0, 1.0, 0.0] * (int(len(self.line_points) / 3) + 6))
            self.gl.glDrawArrays(self.gl.GL_LINES, 0, int(len(self.line_points)/3) + 6)

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
            origin, direction = self.rayPick(event)
            self.draw_pick_ray(origin, direction)

            if self.objects.ray_pick_test(origin, direction) > 0:
                self.objects.select()
        super(OGLCanvas, self).mousePressEvent(event)

    def draw_pick_ray(self, origin, direction):
        """Draw a line along the provided ray function, along with a marker for the eye and picked point."""
        def ray_func(p):
            """Return points along the picking ray"""
            return origin + p * direction

        self.line_points = []
        l_prev = ray_func(220)
        for i in range(10):
            line = ray_func(i * 20)
            self.line_points += [
                line.x(), line.y(), line.z(), l_prev.x(), l_prev.y(), l_prev.z()]
            l_prev = line

        from ui import MeshDrawable
        from meristem import Bud
        self.click_pos = [
            MeshDrawable(Bud.SPHERE_MODEL, offset=origin, scale=0.5, fill_colour=[0, 1, 0]),
            MeshDrawable(Bud.SPHERE_MODEL, offset=ray_func(0.1), scale=0.5, fill_colour=[0, 0, 1]),
        ]
        return

    def rayPick(self, event):
        """Return a picking ray going from the camera through the mouse pointer."""
        self.mouse_pos = event.pos()
        x = (2.0 * event.x()) / self.width() - 1.0
        y = 1.0 - (2.0 * event.y()) / self.height()

        angle, nearZ, _ = self.PERSPECTIVE
        rad = angle * math.pi / 180
        vLength = math.tan(rad / 2) * nearZ
        hLength = vLength * self.viewport_proportions

        # get the camera position in world space
        camera_pos = (self.v_matrix * self.camera_pos.toVector4D()).toVector3D()

        view = (self.camera_look_at - camera_pos).normalized()
        h = view.crossProduct(view, self.camera_normal).normalized()
        v = view.crossProduct(h, view).normalized() * vLength

        # get the point that was clicked on the XY-plane for Z equal to the closer clip plane
        # The point is, of course, in model space
        pos = camera_pos + view * nearZ + h * x * hLength + v * y
        pos = (self.mv_matrix.inverted()[0] * pos.toVector4D()).toVector3D()

        # work out where the camera is in model space
        eye_pos = (self.mv_matrix.inverted()[0] * camera_pos.toVector4D()).toVector3D()

        # Return the origin and direction of the picking ray
        return eye_pos, (pos - eye_pos).normalized()
