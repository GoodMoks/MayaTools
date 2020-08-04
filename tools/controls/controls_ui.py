from PySide2 import QtWidgets
from PySide2 import QtCore
import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaTools.tools.controls.controls_shape as controls
import MayaTools.core.curve as curve
import MayaTools.core.base as base

reload(curve)
reload(controls)


class ControlManagerController(object):
    def __init__(self):
        pass

    def get_all_control_names(self):
        controls_data = controls.ControlShape()
        names = controls_data.get_all_shapes().keys()
        return names

    def create_control(self, name):
        controls_data = controls.ControlShape()
        shape_data = controls_data.get_shape(name)
        shape = curve.CurveShape()
        shape.add_data(shape_data)
        print name, 'new curve'
        curve_main = curve.Curve(shape)
        curve_node = curve_main.create(name=name)


    def export_control(self, control):
        shape = curve.CurveShape()
        shape.add_control(control)
        shape_data = controls.ControlShape()
        shape_data.add_shape(key=control, value=shape.get_data())
        print 'export {}'.format(control)


class ControlsUI(QtWidgets.QDialog):
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self):
        super(ControlsUI, self).__init__(self.MAYA)
        self.setWindowTitle('Controls')
        self.setMinimumSize(200, 380)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()
        self.make_connections()

        self.controller = ControlManagerController()
        self.fill_list()

    def create_widgets(self):
        self.control_list_wdg = QtWidgets.QListWidget()
        self.control_list_wdg.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sorted_comboBox_wdg = QtWidgets.QComboBox()
        self.sorted_comboBox_wdg.addItem('Alphabet')
        self.sorted_comboBox_wdg.addItem('Letters')
        self.sorted_comboBox_wdg.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.search_text_le = QtWidgets.QLineEdit()
        self.create_btn = QtWidgets.QPushButton('Create')
        self.export_btn = QtWidgets.QPushButton('Export')

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.sorted_form_ly = QtWidgets.QFormLayout()
        self.sorted_form_ly.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.sorted_form_ly.addRow('Filter', self.sorted_comboBox_wdg)
        self.sorted_form_ly.addRow('Search', self.search_text_le)
        self.button_ly = QtWidgets.QHBoxLayout()

    def add_to_layout(self):
        self.main_ly.addLayout(self.button_ly)
        self.main_ly.addLayout(self.sorted_form_ly)
        self.button_ly.addWidget(self.create_btn)
        self.button_ly.addWidget(self.export_btn)
        self.main_ly.addWidget(self.control_list_wdg)

    def make_connections(self):
        self.create_btn.clicked.connect(self.create_control)
        self.export_btn.clicked.connect(self.export_control)

    def fill_list(self):
        self.control_list_wdg.clear()
        names = self.controller.get_all_control_names()
        for name in names:
            item = QtWidgets.QListWidgetItem(name)
            self.control_list_wdg.addItem(item)

    def export_control(self):
        sel = cmds.ls(sl=True)[0]
        self.controller.export_control(sel)
        self.fill_list()

    def create_control(self):
        selected_item = self.control_list_wdg.selectedItems()
        if not selected_item:
            om2.MGlobal.displayError('Nothing selected')
            return

        for item in selected_item:
            self.controller.create_control(item.text())

    def showUI(self):
        try:
            ui.deleteLater()  # pylint: disable=used-before-assignment
        except:
            pass

        ui = ControlsUI()
        ui.show()
