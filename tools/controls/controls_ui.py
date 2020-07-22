from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import pymel.core as pm
import maya.cmds as cmds


class ControlsController(object):
    def __init__(self):
        pass

class ControlsUI(QtWidgets.QDialog):
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self):
        super(ControlsUI, self).__init__(self.MAYA)
        self.setWindowTitle('Controls')
        self.setMinimumSize(200, 300)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()
        self.make_connections()

    def create_widgets(self):
        self.control_list_wdg = QtWidgets.QListWidget()
        self.create_btn = QtWidgets.QPushButton('Create')
        self.export_btn = QtWidgets.QPushButton('Export')

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.button_ly = QtWidgets.QHBoxLayout()

    def add_to_layout(self):
        self.main_ly.addLayout(self.button_ly)
        self.button_ly.addWidget(self.create_btn)
        self.button_ly.addWidget(self.export_btn)
        self.main_ly.addWidget(self.control_list_wdg)

    def make_connections(self):
        self.create_btn.clicked.connect(self.create_control)
        self.export_btn.clicked.connect(self.export_control)

    def export_control(self):
        print 'Export'

    def create_control(self):
        print 'Create'

    def showUI(self):
        try:
            ui.deleteLater()
        except:
            pass

        ui = ControlsUI()
        ui.show()
