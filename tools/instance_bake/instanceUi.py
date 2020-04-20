from PySide2 import QtWidgets
from PySide2 import QtCore
import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.base as base
import MayaTools.core.dag as dag

reload(dag)
import bake_chain

reload(bake_chain)

"""
import sys
sys.path.append(r'E:\Work\Pipeline\Projects\Tools')
import MayaTools.tools.instance_bake.instanceUi as ui
reload(ui)
ui.show_dev()
"""


def show_dev():
    try:
        instance.close()  # pylint: disable=E0601
        instance.deleteLater()
    except:
        pass

    instance = InstanceShapeUI()
    instance.show()


class Instance:
    def __init__(self, obj, instance):
        self.obj = obj
        self.instance = instance
        self.add_instance()

    def add_instance(self):
        obj_instance = pm.instance(self.instance)[0]
        obj_instance.getShape().setParent(self.obj, r=True)
        pm.delete(obj_instance)
        return True

    def get_instance(self):
        return self.instance


class InstanceShape:
    MAIN_INST_NAME = 'main_instance'

    def __init__(self, objects, shape_name, shape_vis=False):
        self.objects = objects
        self.shape_name = shape_name
        self.shape_vis = shape_vis

        if not isinstance(self.objects, list):
            self.objects = list(self.objects)

        if pm.objExists(self.shape_name):
            om.MGlobal.displayError('Shape "{}" already exist'.format(self.shape_name))
            return

        self.create_main_instance()
        self.add_instance()
        self.add_instance_attr()
        self.hide_attr()

        try:
            pm.delete(self.MAIN_INST_NAME)
        except:
            pass

    def create_main_instance(self):
        self.instance_obj = pm.spaceLocator(n=self.MAIN_INST_NAME)
        self.instance_obj.getShape().visibility.set(self.shape_vis)
        pm.rename(self.instance_obj.getShape(), self.shape_name)

    def add_instance_attr(self):
        pm.addAttr(self.shape_name, ln='Instance', dt="string")

    def add_instance(self):
        for obj in self.objects:
            Instance(obj, self.instance_obj)

    def get_available_attributes(self, obj):
        return pm.listAttr(obj, cb=True)

    def hide_attr(self):
        for attr in self.get_available_attributes(self.shape_name):
            pm.setAttr('{}.{}'.format(self.shape_name, attr), keyable=False, cb=False)


class InstanceShapeController(object):
    @staticmethod
    def get_selected():
        selected = pm.selected()
        if not selected:
            om.MGlobal.displayError('Nothing selected')
            return
        return selected

    @staticmethod
    def input_shape_name():
        try:
            input = raw_input()
        except:
            om.MGlobal.displayError('You did not enter an object name')
            return None

        return input

    @staticmethod
    def get_full_path(obj):
        return pm.ls(obj, ap=True)

    @staticmethod
    def delete_instance(items):
        for i in items:
            pm.delete(i.text())

    @staticmethod
    def select_item(items):
        pm.select(cl=True)
        for item in items:
            pm.select(item.text(), add=True)


    @staticmethod
    def get_shapes_instance(obj):
        return [x.split('|')[-1] for x in dag.get_shapes(obj)]

    def __init__(self):
        pass

    def make_instance(self):
        selected = self.get_selected()
        if selected:
            name = self.input_shape_name()
            if not name:
                return

            InstanceShape(selected, name)


    def delete_object(self, objects, instance):
        for obj in objects:
            if instance in self.get_shapes_instance(obj.text()):
                path = '{}|{}'.format(obj.text(), instance)
                pm.parent(path, rm=True, s=True)


    def add_instance(self, objects, instance):
        for obj in objects:
            if instance not in self.get_shapes_instance(obj):
                Instance(obj, instance)


class InstanceShapeUI(QtWidgets.QDialog):
    MAYA = maya_window = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self, parent=MAYA):
        super(InstanceShapeUI, self).__init__(parent)

        self.setWindowTitle('Instance Attribute')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setBaseSize(400, 250)

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()
        self.make_connections()

        self.controller = InstanceShapeController()

    def create_widgets(self):
        # ListWidget
        self.instance_list_wdg = QtWidgets.QListWidget()
        self.object_list_wdg = QtWidgets.QListWidget()
        self.instance_list_wdg.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.object_list_wdg.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # Splitter Widget
        self.instance_base_wdg = QtWidgets.QWidget()
        self.object_base_wdg = QtWidgets.QWidget()

        # Label
        self.instance_label = QtWidgets.QLabel('Instance')
        self.instance_label.setAlignment(QtCore.Qt.AlignCenter)
        self.object_label = QtWidgets.QLabel('Objects')
        self.object_label.setAlignment(QtCore.Qt.AlignCenter)

        # Buttons
        self.add_instance_btn = QtWidgets.QPushButton('Add')
        self.del_instance_btn = QtWidgets.QPushButton('Delete')
        self.add_object_btn = QtWidgets.QPushButton('Add')
        self.del_object_btn = QtWidgets.QPushButton('Delete')
        self.add_attr_btn = QtWidgets.QPushButton('Add Attribute')
        self.del_attr_btn = QtWidgets.QPushButton('Delete Attribute')
        self.edit_attr_btn = QtWidgets.QPushButton('Edit Attribute')

        # Splitter
        self.splitter = QtWidgets.QSplitter(self)

    def create_layout(self):
        # Main layout
        self.main_h_ly = QtWidgets.QVBoxLayout(self)
        self.main_h_ly.setMargin(5)

        # List Widget Layout
        self.instance_base_ly = QtWidgets.QVBoxLayout()
        self.instance_base_ly.setContentsMargins(0, 0, 0, 0)
        self.object_base_ly = QtWidgets.QVBoxLayout()
        self.object_base_ly.setContentsMargins(0, 0, 0, 0)

        # Main Items Layout
        self.items_wdg_ly = QtWidgets.QHBoxLayout()

        # Buttons Layout
        self.buttons_wdg_ly = QtWidgets.QHBoxLayout()

    def add_to_layout(self):
        self.main_h_ly.addLayout(self.items_wdg_ly)
        self.main_h_ly.addLayout(self.buttons_wdg_ly)

        self.instance_base_wdg.setLayout(self.instance_base_ly)
        self.object_base_wdg.setLayout(self.object_base_ly)

        self.instance_base_ly.addWidget(self.instance_label)
        self.instance_base_ly.addWidget(self.instance_list_wdg)
        self.instance_base_ly.addWidget(self.add_instance_btn)
        self.instance_base_ly.addWidget(self.del_instance_btn)

        self.object_base_ly.addWidget(self.object_label)
        self.object_base_ly.addWidget(self.object_list_wdg)
        self.object_base_ly.addWidget(self.add_object_btn)
        self.object_base_ly.addWidget(self.del_object_btn)

        self.splitter.addWidget(self.instance_base_wdg)
        self.splitter.addWidget(self.object_base_wdg)
        self.items_wdg_ly.addWidget(self.splitter)

        self.buttons_wdg_ly.addWidget(self.add_attr_btn)
        self.buttons_wdg_ly.addWidget(self.edit_attr_btn)
        self.buttons_wdg_ly.addWidget(self.del_attr_btn)

    def make_connections(self):
        self.instance_list_wdg.itemSelectionChanged.connect(self.item_instance_click)
        self.object_list_wdg.itemSelectionChanged.connect(self.item_object_click)
        self.add_instance_btn.clicked.connect(self.add_instance)
        self.del_instance_btn.clicked.connect(self.delete_instance)
        self.add_object_btn.clicked.connect(self.add_object)
        self.del_object_btn.clicked.connect(self.delete_object)

    """ ======================== functional ================================= """

    def add_instance(self):
        """ add instance """
        self.controller.make_instance()
        self.update_instance()

    def delete_instance(self):
        """ delete instance """
        items = self.instance_list_wdg.selectedItems()
        if items:
            self.controller.delete_instance(items)
            self.update_instance()

    def add_object(self):
        """ add instance to selected objects """
        instance = self.instance_list_wdg.selectedItems()[-1].text()
        selected_objects = self.controller.get_selected()
        if not instance or not selected_objects:
            return

        self.controller.add_instance(selected_objects, instance)
        self.update_object(self.instance_list_wdg.selectedItems()[-1])

    def delete_object(self):
        """ delete instance from object """
        objects = self.object_list_wdg.selectedItems()
        instance = self.instance_list_wdg.selectedItems()[-1].text()
        self.controller.delete_object(objects, instance)
        self.update_object(self.instance_list_wdg.selectedItems()[-1])

    def update_instance(self):
        """ update instance list widget """
        instances = base.get_instances()
        if instances:
            self.instance_list_wdg.clear()
            for instance in instances:
                instance_item = instance.split('|')[-1]
                if not self.check_item(self.instance_list_wdg, instance_item):
                    item = QtWidgets.QListWidgetItem(instance_item)
                    self.instance_list_wdg.addItem(item)
        else:
            self.instance_list_wdg.clear()

    def update_object(self, instance):
        """ update objects list widget
        :param instance: 'item' instance item
        """
        self.object_list_wdg.clear()
        all_objects = self.controller.get_full_path(instance.text())
        for obj in all_objects:
            object_name = obj.split('|')[0]
            item = QtWidgets.QListWidgetItem(object_name)
            self.object_list_wdg.addItem(item)

    def item_instance_click(self, *args):
        """ select instance in scene """
        selected_items = self.instance_list_wdg.selectedItems()
        if selected_items:
            self.update_object(selected_items[-1])
            self.controller.select_item(selected_items)
        else:
            pm.select(cl=True)

    def item_object_click(self, *args):
        """ select object in scene """
        selected_items = self.object_list_wdg.selectedItems()
        if selected_items:
            self.controller.select_item(selected_items)
        else:
            # reset selected object in scene
            self.item_instance_click()

    def check_item(self, widget, item):
        """ check exist item """
        if widget.findItems(item, QtCore.Qt.MatchFlag):
            return True
        else:
            return False

    def showEvent(self, *args, **kwargs):
        """ update at startup  """
        self.update_instance()
