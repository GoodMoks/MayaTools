from PySide2 import QtWidgets
from PySide2 import QtCore
import pymel.core as pm


class FloatSlider(QtWidgets.QSlider):
    def __init__(self, parent, decimals=2, min=0, max=1, dv=0.8, *args, **kwargs):
        super(FloatSlider, self).__init__(parent, *args, **kwargs)
        self.min = min
        self.max = max
        self.multi = 10 ** decimals
        self.setMinimum(self.min)
        self.setMaximum(self.max)

        self.setFixedWidth(120)

        self.create_spin()
        self.make_connect()
        self.setValue(dv)

    def create_spin(self):
        self.spin_num = QtWidgets.QDoubleSpinBox()
        self.spin_num.setRange(self.min, self.max)
        self.spin_num.setSingleStep(0.05)
        self.spin_num.setFixedWidth(50)
        self.spin_num.setAlignment(QtCore.Qt.AlignRight)

    def make_connect(self):
        self.valueChanged.connect(self.update_spin)
        self.spin_num.valueChanged.connect(self.update_sld)

    def update_sld(self, value):
        self.setValue(value)

    def update_spin(self):
        self.spin_num.setValue(self.value())

    def value(self):
        return float(super(FloatSlider, self).value()) / self.multi

    def setMinimum(self, value):
        return super(FloatSlider, self).setMinimum(value * self.multi)

    def setMaximum(self, value):
        return super(FloatSlider, self).setMaximum(value * self.multi)

    def setValue(self, value):
        super(FloatSlider, self).setValue(int(value * self.multi))

    def mousePressEvent(self, *args, **kwargs):
        super(FloatSlider, self).mousePressEvent(*args, **kwargs)
        pm.undoInfo(openChunk=True)

    def mouseReleaseEvent(self, *args, **kwargs):
        super(FloatSlider, self).mouseReleaseEvent(*args, **kwargs)
        pm.undoInfo(closeChunk=True)