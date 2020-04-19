import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from MayaTools.core.ui import qtFloatSlider

import goal_contoller

"""
import sys
sys.path.append(r'E:\Work\Pipeline\Projects\Tools')
import MayaTools.tools.twister.twister_ui as ui

reload(ui)
ui.TwisterUI.showUI()

import sys
sys.path.append(r'E:\Work\Pipeline\Projects\Tools')
from MayaTools.tools.twister.twister_ui import TwisterUI
TwisterUI.showUI()

"""


class TwisterUI(QtWidgets.QDialog):
    MAYA_WINDOW = pm.ui.PyUI('MayaWindow').asQtObject()

    WINDOW_INSTANCE = None

    ICONS = dict(
        point=':pointConstraint.svg',
        twist=':orientConstraint.svg'
    )

    def __init__(self, parent=MAYA_WINDOW):
        super(TwisterUI, self).__init__(parent)
        self.axis = 'X'
        self.type_system = 'all'
        self.item = goal_contoller.GoalItem()
        self.goal_class = goal_contoller.GoalMain()
        # self.item = GoalItem()

        self.setWindowTitle('Mr. Twister')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        # self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        # self.setFixedSize(400, 250)

        # make widgets
        self.create_widgets()

        # make layouts
        self.create_layout()

        # add to widgets to layout
        self.add_to_layout()

        # make connect widgets to
        self.make_connect()
        self.fill_list(self.type_system)
        self.update_selection()
        self.enable_ui(state=False)

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = TwisterUI()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()

    def create_widgets(self):

        self.add_btn = QtWidgets.QPushButton('Add')
        self.del_btn = QtWidgets.QPushButton('Delete')

        self.list_wdg = QtWidgets.QListWidget()
        self.list_wdg.setFixedWidth(150)
        self.list_wdg.setFixedHeight(150)

        self.list_wdg.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.visibility_check = QtWidgets.QCheckBox('Visibility')
        self.dynamic_check = QtWidgets.QCheckBox('Dynamic')
        self.refresh_btn = QtWidgets.QPushButton('Refresh')

        self.sld_label = QtWidgets.QLabel('Simulate propeties')
        self.sld_label.setFixedHeight(20)

        self.sim_cb = QtWidgets.QComboBox()
        self.sim_cb.addItem('All')
        self.sim_cb.addItem('Twist')
        self.sim_cb.addItem('Point')
        self.sim_cb.setFixedWidth(120)
        self.sim_cb.setCurrentIndex(0)

        self.filter_label = QtWidgets.QLabel('Filter')
        self.sld_label.setAlignment(QtCore.Qt.AlignCenter)
        self.x_btn = QtWidgets.QRadioButton('X')
        self.x_btn.setChecked(True)
        self.y_btn = QtWidgets.QRadioButton('Y')
        self.z_btn = QtWidgets.QRadioButton('Z')

        self.create_sld_form()

    def create_sld_form(self):
        self.form_sld = QtWidgets.QFormLayout()
        self.form_sld.setVerticalSpacing(13)

        self.overlap_sld = qtFloatSlider.FloatSlider(QtCore.Qt.Horizontal, min=0, max=1, dv=1)
        self.overlap_ly = QtWidgets.QHBoxLayout()
        self.overlap_ly.addWidget(self.overlap_sld)
        self.overlap_ly.addWidget(self.overlap_sld.spin_num)

        self.stiffness_sld = qtFloatSlider.FloatSlider(QtCore.Qt.Horizontal, min=0, max=1, dv=0.8)
        self.stiffness_ly = QtWidgets.QHBoxLayout()
        self.stiffness_ly.addWidget(self.stiffness_sld)
        self.stiffness_ly.addWidget(self.stiffness_sld.spin_num)

        self.smooth_sld = qtFloatSlider.FloatSlider(QtCore.Qt.Horizontal, min=0, max=10, dv=3, decimals=1)
        self.smooth_ly = QtWidgets.QHBoxLayout()
        self.smooth_ly.addWidget(self.smooth_sld)
        self.smooth_ly.addWidget(self.smooth_sld.spin_num)

        self.dynamic_sld = qtFloatSlider.FloatSlider(QtCore.Qt.Horizontal, min=0, max=1, dv=1)
        self.dynamic_ly = QtWidgets.QHBoxLayout()
        self.dynamic_ly.addWidget(self.dynamic_sld)
        self.dynamic_ly.addWidget(self.dynamic_sld.spin_num)

        self.position_sld = qtFloatSlider.FloatSlider(QtCore.Qt.Horizontal, min=0.01, max=2, dv=1)
        self.position_ly = QtWidgets.QHBoxLayout()
        self.position_ly.addWidget(self.position_sld)
        self.position_ly.addWidget(self.position_sld.spin_num)

        self.form_sld.addRow('Overlap', self.overlap_ly)
        self.form_sld.addRow('Stiffness', self.stiffness_ly)
        self.form_sld.addRow('Smooth', self.smooth_ly)
        self.form_sld.addRow('Dynamic', self.dynamic_ly)
        self.form_sld.addRow('Position', self.position_ly)

    def create_layout(self):
        self.main_ly = QtWidgets.QVBoxLayout(self)
        self.items_ly = QtWidgets.QHBoxLayout()
        self.list_ly = QtWidgets.QVBoxLayout()
        self.sld_ly = QtWidgets.QVBoxLayout()
        self.check_ly = QtWidgets.QHBoxLayout()
        self.button_ly = QtWidgets.QHBoxLayout()
        self.axis_ly = QtWidgets.QHBoxLayout()
        self.axis_ly.setAlignment(QtCore.Qt.AlignCenter)
        self.axis_ly.setSpacing(40)
        self.filter_ly = QtWidgets.QHBoxLayout()
        self.check_ly.setAlignment(QtCore.Qt.AlignCenter)

    def add_to_layout(self):
        self.main_ly.addLayout(self.items_ly)
        self.main_ly.addWidget(self.add_btn)
        self.main_ly.addWidget(self.del_btn)
        self.items_ly.addLayout(self.list_ly)
        self.items_ly.addLayout(self.sld_ly)

        self.filter_ly.addWidget(self.filter_label)
        self.filter_ly.addWidget(self.sim_cb)

        self.list_ly.addLayout(self.filter_ly)
        self.list_ly.addWidget(self.list_wdg)
        self.list_ly.addLayout(self.check_ly)

        self.sld_ly.addWidget(self.sld_label)
        self.sld_ly.addLayout(self.form_sld)
        self.sld_ly.addLayout(self.axis_ly)
        self.form_sld.addWidget(self.refresh_btn)

        self.button_ly.addWidget(self.add_btn)
        self.button_ly.addWidget(self.refresh_btn)
        self.button_ly.addWidget(self.del_btn)
        self.check_ly.addWidget(self.visibility_check)
        self.check_ly.addWidget(self.dynamic_check)
        self.main_ly.addLayout(self.button_ly)

        self.axis_ly.addWidget(self.x_btn)
        self.axis_ly.addWidget(self.y_btn)
        self.axis_ly.addWidget(self.z_btn)

    def make_connect(self):
        self.add_btn.clicked.connect(self.add_system)
        self.del_btn.clicked.connect(self.delete_system)
        self.refresh_btn.clicked.connect(self.refresh)

        self.list_wdg.itemSelectionChanged.connect(self.update_selection)

        self.overlap_sld.valueChanged.connect(lambda: self.item.set_overlap(self.overlap_sld.value()))
        self.stiffness_sld.valueChanged.connect(lambda: self.item.set_stiffness(self.stiffness_sld.value()))
        self.smooth_sld.valueChanged.connect(lambda: self.item.set_smooth(self.smooth_sld.value()))
        self.dynamic_sld.valueChanged.connect(lambda: self.item.set_dynamic(self.dynamic_sld.value()))
        self.position_sld.valueChanged.connect(lambda: self.item.set_position(self.position_sld.value()))

        self.visibility_check.clicked.connect(lambda: self.item.set_visibility(self.visibility_check.isChecked()))
        self.dynamic_check.clicked.connect(lambda: self.set_dynamic_particle(self.dynamic_check.isChecked()))

        self.x_btn.clicked.connect(lambda: self.set_axis(self.x_btn))
        self.y_btn.clicked.connect(lambda: self.set_axis(self.y_btn))
        self.z_btn.clicked.connect(lambda: self.set_axis(self.z_btn))

        self.sim_cb.currentIndexChanged.connect(self.set_type_system)

    def refresh(self):
        self.item.refresh_goal()

    def set_dynamic_particle(self, value):
        self.item.set_dynamic_particle(value)
        self.dynamic_sld.setValue(value)
        self.dynamic_sld.setEnabled(False)

    def update_selection(self):
        self.get_selected_items()
        pm.select(self.item.object)
        self.enable_update()

    def enable_update(self):
        if self.item.object:
            self.enable_ui(state=True)
            self.update_slider_value()
        else:
            self.enable_ui(state=False)

    def enable_ui(self, state=False):
        for u in [self.overlap_sld, self.overlap_sld.spin_num, self.stiffness_sld, self.stiffness_sld.spin_num,
                  self.smooth_sld, self.smooth_sld.spin_num, self.dynamic_sld, self.dynamic_sld.spin_num,
                  self.position_sld, self.position_sld.spin_num, self.visibility_check, self.dynamic_check,
                  self.refresh_btn, self.del_btn]:
            u.setEnabled(state)

        if self.item.system == 'point':
            self.position_sld.setEnabled(False)

    def update_slider_value(self):
        """ update value on sliders """
        self.overlap_sld.setValue(self.item.get_overlap())
        self.stiffness_sld.setValue(self.item.get_stiffness())
        self.smooth_sld.setValue(self.item.get_smooth())
        self.dynamic_sld.setValue(self.item.get_dynamic())
        self.position_sld.setValue(self.item.get_position())

        if self.item.get_visibility() == True:
            self.visibility_check.setChecked(QtCore.Qt.Checked)
        else:
            self.visibility_check.setChecked(QtCore.Qt.Unchecked)

        if self.item.get_dynamic_particle() == True:
            self.dynamic_check.setChecked(QtCore.Qt.Checked)
        else:
            self.dynamic_check.setChecked(QtCore.Qt.Unchecked)

    def fill_list(self, filter):
        if pm.objExists(self.goal_class.SIMULATION_GROUP):
            child = pm.PyNode(self.goal_class.SIMULATION_GROUP).getChildren()
            if child:
                self.list_wdg.clear()
                for c in child:
                    jnt = c.split('_dyn_')[0]
                    system = c.split('_dyn_')[1][:-4].lower()
                    if filter == system or filter == 'all':
                        item = QtWidgets.QListWidgetItem('{}: {}'.format(system.capitalize(), jnt))
                        item.setIcon(QtGui.QIcon(self.ICONS[system]))
                        self.list_wdg.addItem(item)
            else:
                self.list_wdg.clear()
        else:
            self.list_wdg.clear()

    def get_selected_items(self):
        """ get selected items in listWidget """
        items = self.list_wdg.selectedItems()
        if not items:
            self.item = goal_contoller.GoalItem()
            return

        self.many_selected = []
        for item in items:
            Item = goal_contoller.GoalItem()
            Item.set_item(item.text())
            self.many_selected.append(Item)

        if len(items) == 1:
            self.item = goal_contoller.GoalItem()
            self.item.set_item(items[0].text())
        else:
            self.item = goal_contoller.GoalItem()
            self.item.set_item(items[:-1][0].text())

    def add_system(self):
        """ add goal """
        pm.undoInfo(openChunk=True)
        if self.type_system == 'twist':
            self.goal_class.add_system(axis=self.axis, point=False, twist=True)
        if self.type_system == 'point':
            self.goal_class.add_system(axis=self.axis, point=True, twist=False)
        if self.type_system == 'all':
            self.goal_class.add_system(axis=self.axis, point=True, twist=True)
        pm.undoInfo(closeChunk=True)
        self.fill_list(self.type_system)

    def delete_system(self):
        """ delete selected system """
        if self.many_selected:
            for item in self.many_selected:
                self.goal_class.delete_system(item.object, item.system)
                self.set_type_system()
                self.fill_list(self.type_system)

    def change_visibility(self):
        if self.vis_check.checkState() == QtCore.Qt.CheckState.Checked:
            pm.setAttr('{}_dyn_{}_grp.visibility'.format(self.sel_obj, self.sel_system), 1)

        elif self.vis_check.checkState() == QtCore.Qt.CheckState.Unchecked:
            pm.setAttr('{}_dyn_{}_grp.visibility'.format(self.sel_obj, self.sel_system), 0)

    def change_dynamic(self):
        if self.dynamic_check.checkState() == QtCore.Qt.CheckState.Checked:
            pm.setAttr('{}_{}_particleShape.isDynamic'.format(self.sel_obj, self.sel_system), 1)
            self.dynamic_sld.setEnabled(1)
            self.dynamic_sld.setValue(1)
        elif self.dynamic_check.checkState() == QtCore.Qt.CheckState.Unchecked:
            pm.setAttr('{}_{}_particleShape.isDynamic'.format(self.sel_obj, self.sel_system), 0)
            self.dynamic_sld.setEnabled(0)
            self.dynamic_sld.setValue(0)

    def set_axis(self, widget):
        """ set axis to class attribute """
        self.axis = widget.text()

    def set_type_system(self):
        """ update type system in type combo box"""
        self.type_system = self.sim_cb.currentText().lower()
        self.fill_list(self.type_system)

    def show_info_box(self, title='Info', information='Some info'):
        """ raise window with message """
        QtWidgets.QMessageBox.information(self, title, information)


def showUI_dev():
    try:
        twister.close()  # pylint: disable=E0601
        twister.deleteLater()
    except:
        pass

    twister = TwisterUI()
    twister.show()
