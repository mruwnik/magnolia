import math

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QPushButton, QLineEdit, QCheckBox,
)


class Segment(QWidget):
    """A widget to handle meristem settings."""

    name = 'base_segment'

    def __init__(self, positioner_class, *args, **kwargs):
        """Initialise this segment."""
        super().__init__(*args, **kwargs)

        self.positioner_class = positioner_class

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.init_container()
        self.init_controls()

    def init_container(self):
        """Initialise the actual container."""
        self.main_box = QVBoxLayout(self)
        self.main_box.setObjectName('main_box')

        self.label_box = QHBoxLayout()

        self.label = self.make_label('label', self.name)
        self.label_box.addWidget(self.label)
        self.make_delete_button()

        self.main_box.addLayout(self.label_box)

    def init_controls(self):
        """Add all controls needed for a given meristem to be set up."""
        self.to_add_input = None

        self.controls = QHBoxLayout()
        self.controls.setObjectName('controls')
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls.addItem(spacerItem)

        self.main_box.addLayout(self.controls)

    def make_delete_button(self):
        """Add a delete button that will remove this segment."""
        # put a spacer between the button and the controls
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_box.addItem(spacerItem)

        # create the actual button
        self.delete_button = QPushButton(self)
        self.delete_button.setObjectName('delete_button')
        self.delete_button.setText('X')
        self.delete_button.setFixedWidth(20)

        self.label_box.addWidget(self.delete_button)

    def checkbox(self, name, is_checked=False):
        checkBox = QCheckBox(self)
        checkBox.setObjectName(name)
        checkBox.setChecked(is_checked)
        return checkBox

    @property
    def to_add(self):
        """Return how many buds should be modified according to the settings of this postioner."""
        return int(self.to_add_input.text() or 0)

    def text_line(self, name, default=None, width=30):
        """Make a text input with the given name and default value."""
        text_line = QLineEdit(self)
        text_line.setObjectName(name)
        if default:
            text_line.setText(str(default))

        text_line.setFixedWidth(width)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(text_line.sizePolicy().hasHeightForWidth())
        text_line.setSizePolicy(sizePolicy)
        return text_line

    def make_label(self, name, text):
        """Make a label with the given name and text."""
        label = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        label.setSizePolicy(sizePolicy)
        label.setObjectName(name)
        label.setText(text)
        return label


class RingSegment(Segment):

    name = 'Ring positioner'

    def init_controls(self):
        """Add all controls needed for a given meristem to be set up."""
        self.controls = QHBoxLayout()
        self.controls.setObjectName('controls')
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls.addItem(spacerItem)

        self.controls.addWidget(self.make_label('angle_label', 'angle:'))
        self.angle = self.text_line('set_angle', 60)
        self.controls.addWidget(self.angle)

        self.controls.addWidget(self.make_label('per_ring_label', 'per ring:'))
        self.per_ring = self.text_line('per_ring', 12)
        self.controls.addWidget(self.per_ring)

        self.controls.addWidget(self.make_label('rings_label', 'rings:'))
        self.to_add_input = self.text_line('set_rings', 5)
        self.controls.addWidget(self.to_add_input)

        self.main_box.addLayout(self.controls)

    def positioner(self, start_angle, start_height):
        """Get a positioner for the current settings."""
        return self.positioner_class(
            math.radians(float(self.angle.text() or 0)),
            int(self.per_ring.text() or 0),
            start_angle=start_angle,
            start_height=start_height,
        )

    @property
    def to_add(self):
        """The amount of buds to add."""
        return int(self.to_add_input.text() or 0) * int(self.per_ring.text() or 0)


class DecreasingRingSegment(RingSegment):

    name = 'Decreasing ring positioner'

    def init_controls(self):
        """Add all controls needed for a given meristem to be set up."""
        super().init_controls()

        self.controls2 = QHBoxLayout()
        self.controls2.setObjectName('controls2')
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls2.addItem(spacerItem)

        self.controls2.addWidget(self.make_label('delta_label', 'decrease by (%):'))
        self.delta = self.text_line('set_delta', 10, 35)
        self.controls2.addWidget(self.delta)

        self.controls2.addWidget(self.make_label('z_scale_label', 'scale radius:'))
        self.scale_radius = self.checkbox('scale_radius')
        self.controls2.addWidget(self.scale_radius)

        self.main_box.addLayout(self.controls2)

    def positioner(self, start_angle, start_height):
        """Get a positioner for the current settings."""
        return self.positioner_class(
            math.radians(float(self.angle.text() or 0)),
            int(self.per_ring.text() or 0),
            scale=float(self.delta.text() or 0.0),
            scale_radius=self.scale_radius.isChecked(),
            start_angle=start_angle,
            start_height=start_height,
        )


class LowestAvailableSegment(Segment):

    name = 'Lowest available space positioner'

    def init_controls(self):
        """Add all controls needed for a given meristem to be set up."""
        self.controls = QHBoxLayout()
        self.controls.setObjectName('controls')
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls.addItem(spacerItem)

        self.controls.addWidget(self.make_label('buds_to_add_label', 'buds to add:'))
        self.to_add_input = self.text_line('buds_to_add', 6)
        self.controls.addWidget(self.to_add_input)

        self.controls.addWidget(self.make_label('size_label', 'bud size (as fraction of R):'))
        self.bud_size = self.text_line('bud_size', 2)
        self.controls.addWidget(self.bud_size)

        self.main_box.addLayout(self.controls)

    def positioner(self, start_angle, start_height):
        """Get a positioner for the current settings."""
        return self.positioner_class(
            start_size=float(self.bud_size.text() or 0),
            start_angle=start_angle,
            start_height=start_height,
        )
