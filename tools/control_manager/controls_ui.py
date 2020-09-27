import pymel.core as pm
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtWidgets
import maya.api.OpenMaya as om2
import MayaTools.core.data as data
import MayaTools.core.ui.QMessageBox as message
import MayaTools.tools.control_manager.controls as controls
import MayaTools.core.curve as curve

reload(controls)
reload(message)
reload(curve)
reload(data)


class ControlsController(object):
    def __init__(self):
        pass

    @staticmethod
    def get_all_control_names():
        controls_data = data.CurveShapeData()
        names = controls_data.get_all_shapes().keys()
        return names

    @staticmethod
    def create_control(items):
        cmds.undoInfo(openChunk=True)

        selection = cmds.ls(sl=True)
        if selection:
            for sel in selection:
                for i in items:
                    control_curve = controls.ControlCurve(control=i.text(), align=sel)
                    control_curve.create()

        else:
            for i in items:
                control_curve = controls.ControlCurve(control=i.text())
                control_curve.create()

        cmds.undoInfo(closeChunk=True)

    def exists_control(self, control):
        all_controls = self.get_all_control_names()
        if control in all_controls:
            return True
        return False

    @staticmethod
    def export_control(control):
        manager = curve.CurveManager()
        manager.export(control, overwrite=True)

    @staticmethod
    def delete_control(items):
        manager = curve.CurveManager()
        for i in items:
            manager.delete(i.text())

    def edit_item_name(self, old, new):
        if self.exists_control(new):
            return
        manager = curve.CurveManager()
        manager.change_name(old, new)


class ControlsUI(QtWidgets.QDialog):
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    WINDOW_INSTANCE = None

    def __init__(self):
        super(ControlsUI, self).__init__(self.MAYA)
        self.setWindowTitle('Controls')
        self.setMinimumSize(200, 380)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()
        self.make_connections()

        self.names = None
        self.prev_item_name = None

        self.controller = ControlsController()
        self.update_list()

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
        self.delete_btn = QtWidgets.QPushButton('Delete')

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
        self.button_ly.addWidget(self.delete_btn)
        self.button_ly.addWidget(self.export_btn)
        self.main_ly.addWidget(self.control_list_wdg)
        self.main_ly.addWidget(self.create_btn)

    def make_connections(self):
        self.create_btn.clicked.connect(self.create_control)
        self.export_btn.clicked.connect(self.export_control)
        self.sorted_comboBox_wdg.currentIndexChanged.connect(self.set_sorting)
        self.search_text_le.textChanged.connect(self.filter_search_letter)
        self.delete_btn.clicked.connect(self.delete_control)
        self.control_list_wdg.itemDoubleClicked.connect(self.item_clicked)
        self.control_list_wdg.itemChanged.connect(self.edit_item)

    def get_all_items_name(self):
        items = []
        for item in xrange(self.control_list_wdg.count()):
            items.append(self.control_list_wdg.item(item).text())
        return items

    def filter_search_letter(self, letter):
        if letter:
            filter = []
            names = self.get_all_items_name()
            if names:
                for name in names:
                    if name.startswith(letter):
                        filter.append(name)

            self.filter_list(filter)
        else:
            self.filter_list(self.names)

    def update_list(self):
        self.names = self.controller.get_all_control_names()
        self.filter_list(self.names)

    def filter_list(self, names):
        if self.sorted_comboBox_wdg.currentIndex() == 0:
            self.fill_list(sorted(names))
        if self.sorted_comboBox_wdg.currentIndex() == 1:
            self.fill_list(sorted(names, key=len))

    def set_sorting(self, index):
        if index == 0:
            self.filter_alphabet_letters()
        if index == 1:
            self.filter_count_letters()

    def filter_count_letters(self):
        items = self.get_all_items_name()
        self.fill_list(sorted(items, key=len))

    def filter_alphabet_letters(self):
        items = self.get_all_items_name()
        self.fill_list(sorted(items))

    def fill_list(self, names):
        self.control_list_wdg.clear()
        for name in names:
            item = QtWidgets.QListWidgetItem(name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.control_list_wdg.addItem(item)

    def export_control(self):
        selected = cmds.ls(sl=True)
        if not selected:
            om2.MGlobal.displayError('Nothing selected')
            return

        for s in selected:
            if self.controller.exists_control(s):
                msg = message.MessageQuestion(title='Information',
                                              text="{} already exists, overwrite it".format(s),
                                              parent=self)
                if not msg.showUI():
                    continue

            self.controller.export_control(s)

        self.update_list()

    def create_control(self):
        selected_item = self.control_list_wdg.selectedItems()
        if not selected_item:
            om2.MGlobal.displayError('Nothing selected')
            return

        self.controller.create_control(selected_item)

    def delete_control(self):
        selected_item = self.control_list_wdg.selectedItems()
        if not selected_item:
            om2.MGlobal.displayError('Nothing selected')
            return

        msg = message.MessageQuestion(title='Information',
                                      text='Delete control_manager? Are you sure?',
                                      parent=self)
        if msg.showUI():
            self.controller.delete_control(selected_item)

        self.update_list()

    def edit_item(self, args):
        self.controller.edit_item_name(self.prev_item_name, args.text())
        self.update_list()

    def item_clicked(self, args):
        self.prev_item_name = args.text()

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = ControlsUI()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()

    def showUI_dev(self):
        try:
            ui.deleteLater()  # pylint: disable=used-before-assignment
        except:
            pass

        ui = ControlsUI()
        ui.show()
