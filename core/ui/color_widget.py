from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui


class ColorWidget(QtWidgets.QLabel):
    color_changed = QtCore.Signal()

    def __init__(self, color=None, parent=None):
        super(ColorWidget, self).__init__(parent)

        self._color = color

        self.set_size(50, 14)
        if not color:
            self.set_color_none()
        self.set_color(color)



    def set_size(self, width, height):
        self.setFixedSize(width, height)

    def set_color_none(self):
        image = QtGui.QImage(':/RS_disabled_tile.png')
        pixmap = QtGui.QPixmap.fromImage(image)
        self.setPixmap(pixmap)

    def set_color(self, color):
        color = QtGui.QColor(color)

        if self._color != color:
            self._color = color

            pixmap = QtGui.QPixmap(self.size())
            pixmap.fill(self._color)
            self.setPixmap(pixmap)

            self.color_changed.emit()

    def get_color(self):
        return self._color

    def select_color(self):
        color = QtWidgets.QColorDialog.getColor(self.get_color(), self,
                                                options=QtWidgets.QColorDialog.DontUseNativeDialog)

        if color.isValid():
            self.set_color(color)

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.select_color()
