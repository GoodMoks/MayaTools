from PySide2 import QtWidgets
from PySide2 import QtCore


class AxesCheckBox(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AxesCheckBox, self).__init__(parent)

        self.build()
        self.make_connections()

    def build(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.main_ly.setContentsMargins(0, 5, 5, 5)

        self.all = QtWidgets.QCheckBox('All')
        self.all.setCheckState(QtCore.Qt.Checked)
        self.main_ly.addWidget(self.all)

        self.axes_ly = QtWidgets.QHBoxLayout()

        self.main_ly.addLayout(self.axes_ly)

        self.x = QtWidgets.QCheckBox('X')
        self.y = QtWidgets.QCheckBox('Y')
        self.z = QtWidgets.QCheckBox('Z')

        self.axes_ly.addWidget(self.x)
        self.axes_ly.addWidget(self.y)
        self.axes_ly.addWidget(self.z)

    def make_connections(self):
        self.x.stateChanged.connect(self.update_axes)
        self.y.stateChanged.connect(self.update_axes)
        self.z.stateChanged.connect(self.update_axes)

        self.all.stateChanged.connect(self.update_all)

    def update_all(self, state):
        axes = [self.x, self.y, self.z]
        if state:
            for axis in axes:
                axis.setCheckState(QtCore.Qt.Unchecked)

    def update_axes(self, state):
        if state:
            if self.all.checkState():
                self.all.setCheckState(QtCore.Qt.Unchecked)

    def get_checked_axis(self):
        if self.all.isChecked():
            return ['x', 'y', 'z']

        return self.get_state_list(True)

    def get_unchecked_axis(self):
        if self.all.isChecked():
            return []

        return self.get_state_list(False)

    def get_state_list(self, state):
        axes = []
        for axis, obj in zip(('x', 'y', 'z'), (self.x, self.y, self.z)):
            if obj.isChecked() == state:
                axes.append(axis)
        return axes