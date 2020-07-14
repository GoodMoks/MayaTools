import pymel.core as pm
from PySide2 import QtWidgets


class Separator(object):
    def __init__(self, label, parent, w, h):
        self.label = label
        self.parent = parent
        self.width = w
        self.height = h
        self.create_separator()

    def create_separator(self):
        with pm.horizontalLayout(p=self.parent, w=self.width, h=self.height) as layout:
            pm.separator()
            pm.text(self.label)
            pm.separator()
        return layout


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
