from PySide2 import QtWidgets
from PySide2 import QtCore
import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.base as base
import instance_shape_controller
import instance_shape
import PySide2

reload(base)
reload(instance_shape_controller)

class InstanceShapeUI(QtWidgets.QDialog):
    WINDOW_INSTANCE = None
    MAYA = pm.ui.PyUI('MayaWindow').asQtObject()

    def __init__(self, parent=MAYA):
        super(InstanceShapeUI, self).__init__(parent)

        self.setWindowTitle('Instance Shape')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setBaseSize(400, 250)

        self.create_widgets()
        self.create_layout()
        self.add_to_layout()
        self.make_connections()

        self.controller = instance_shape_controller.InstanceShapeController()

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

        # Splitter
        self.splitter = QtWidgets.QSplitter(self)

    def create_layout(self):
        # Main layout
        self.main_v_ly = QtWidgets.QVBoxLayout(self)
        self.main_v_ly.setMargin(5)

        # List Widget Layout
        self.instance_base_ly = QtWidgets.QVBoxLayout()
        self.instance_base_ly.setContentsMargins(0, 0, 0, 0)
        self.object_base_ly = QtWidgets.QVBoxLayout()
        self.object_base_ly.setContentsMargins(0, 0, 0, 0)

        # Main Items Layout
        self.items_wdg_ly = QtWidgets.QHBoxLayout()

    def add_to_layout(self):
        self.main_v_ly.addLayout(self.items_wdg_ly)

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


    def make_connections(self):
        self.instance_list_wdg.itemSelectionChanged.connect(self.item_instance_click)
        self.object_list_wdg.itemSelectionChanged.connect(self.item_object_click)
        self.add_instance_btn.clicked.connect(self.add_instance)
        self.del_instance_btn.clicked.connect(self.delete_instance)
        self.add_object_btn.clicked.connect(self.add_object)
        self.del_object_btn.clicked.connect(self.delete_object)

    @classmethod
    def showUI(cls):
        if not cls.WINDOW_INSTANCE:
            cls.WINDOW_INSTANCE = InstanceShapeUI()

        if cls.WINDOW_INSTANCE.isHidden():
            cls.WINDOW_INSTANCE.show()
        else:
            cls.WINDOW_INSTANCE.raise_()
            cls.WINDOW_INSTANCE.activateWindow()

    """ ======================== functional ================================= """

    def add_instance(self):
        """ add instance """
        self.controller.make_instance(self)
        self.update_instance()

    def delete_instance(self):
        """ delete instance """
        items = self.instance_list_wdg.selectedItems()
        if items:
            self.controller.delete_instance(items)
            self.update_instance()
            self.object_list_wdg.clear()

    def add_object(self):
        """ add instance to selected objects """
        instance = self.instance_list_wdg.selectedItems()
        if instance:
            instance = instance[-1].text()
            selected_objects = self.controller.get_selected()
            if selected_objects:
                self.controller.add_instance(selected_objects, instance)
                self.update_object(self.instance_list_wdg.selectedItems()[-1])
                pm.select(instance)


    def delete_object(self):
        """ delete instance from object """
        objects = self.object_list_wdg.selectedItems()
        instance = self.instance_list_wdg.selectedItems()
        if instance and objects:
            instance_name = instance[-1].text()
            self.controller.delete_object(objects, instance_name)
            self.update_object(instance[-1])
            if not len(self.controller.get_full_path(instance_name)):
                self.update_instance()

    def update_instance(self):
        """ update instance list widget """
        all_instances = base.get_objects_with_attr(om.MFn.kLocator, instance_shape.InstanceShape.ATTR_NAME)
        instances_shape = base.get_instances()
        instances = all_instances + instances_shape
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
            object_name = obj.split('|{}'.format(instance.text()))[0]
            item = QtWidgets.QListWidgetItem(object_name)
            self.object_list_wdg.addItem(item)

    def item_instance_click(self, *args):
        """ select instance in scene """
        selected_instance = self.instance_list_wdg.selectedItems()
        selected_objects = self.object_list_wdg.selectedItems()
        if selected_instance:
            self.update_object(selected_instance[-1])
            self.controller.select_item(selected_instance)
        else:
            if selected_objects:
                #self.item_object_click()
                pm.select(cl=True)
                self.object_list_wdg.clear()
            else:
                pm.select(cl=True)
                self.object_list_wdg.clear()

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
        print item, 'item'
        print widget
        if widget.findItems(item, QtCore.Qt.MatchFlag):
            return True
        else:
            return False

    def showEvent(self, *args, **kwargs):
        """ update at startup  """
        self.update_instance()