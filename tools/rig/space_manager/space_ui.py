from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import pymel.core as pm






class SpaceUI(QtWidgets.QDialog):

    MAYA = MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self, parent=MAYA):
        super(SpaceUI, self).__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()

    def showUI(self):

        try:
            space = SpaceUI()
            spa

    def create_widgets(self):
        self.list_wdg = QtWidgets.QListWidget()

    def create_layout(self):
        self.main_ly = QtWidgets.QHBoxLayout(self)

    def make_connections(self):
        pass

    def add_to_layout(self):
        self.main_ly.addWidget(self.list_wdg)


