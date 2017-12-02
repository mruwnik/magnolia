from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QPushButton,
)


class Segment(QWidget):
    """A widget to handle meristem settings."""

    def __init__(self, *args, **kwargs):
        """Initialise this segment."""
        super().__init__(*args, **kwargs)

        self.init_container()
        self.init_controls()

    def init_container(self):
        """Initialise the actual container."""
        self.main_box = QVBoxLayout(self)
        self.main_box.setObjectName('main_box')

        self.label = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.label.setText("Segment")
        self.main_box.addWidget(self.label)

    def init_controls(self):
        """Add all controls."""
        self.controls = QHBoxLayout()
        self.controls.setObjectName('controls')
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.controls.addItem(spacerItem)

        self.make_controls()
        self.make_delete_button()

        self.main_box.addLayout(self.controls)

    def make_delete_button(self):
        """Add a delete button that will remove this segment."""
        # put a spacer between the button and the controls
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.controls.addItem(spacerItem)

        # create the actual button
        self.delete_button = QPushButton(self)
        self.delete_button.setObjectName('delete_button')
        self.delete_button.setText('X')
        self.delete_button.setFixedWidth(20)

        self.controls.addWidget(self.delete_button)

    def make_controls(self):
        """Add all controls needed for a given meristem to be set up."""
        pass
