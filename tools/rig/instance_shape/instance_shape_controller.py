import pymel.core as pm
import maya.OpenMaya as om
import MayaTools.core.dag as dag
import MayaTools.core.attribute as attribute
import instance_shape
from PySide2 import QtWidgets


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
    def get_full_path(instance):
        objects = pm.ls(instance, ap=True)
        if len(objects) == 1:
            parent = dag.get_parent('{}'.format(objects[0]))
            if parent:
                return ['{}|{}'.format(parent[0], instance)]
        return objects

    @staticmethod
    def delete_instance(items):
        for i in items:
            pm.delete(i.text())

    @staticmethod
    def select_item(items):
        pm.select(cl=True)
        for item in items:
            try:
                pm.select(item.text(), add=True)
            except:
                pass

    @staticmethod
    def get_shapes_instance(obj):
        return [x.split('|')[-1] for x in dag.get_shapes('{}'.format(obj))]

    def __init__(self):
        pass

    def make_instance(self, parent):
        selected = self.get_selected()
        if selected:
            name, ok = QtWidgets.QInputDialog().getText(parent, "Input Name",
                                                        "Instance Name:", QtWidgets.QLineEdit.Normal)
            if name and ok:
                instance_shape.InstanceShape(selected, name)

    def delete_object(self, objects, instance):
        for obj in objects:
            if instance in self.get_shapes_instance(obj.text()):
                path = '{}|{}'.format(obj.text(), instance)
                pm.parent(path, rm=True, s=True)

    def add_instance(self, objects, instance):
        for obj in objects:
            obj_instance = obj.split('|')
            if len(obj_instance) > 1:
                obj_instance = obj_instance[1]

            if not obj_instance == instance:
                shapes = self.get_shapes_instance(obj)
                if instance not in shapes:
                    if not attribute.has_attr(str(obj), instance_shape.InstanceShape.ATTR_NAME):
                        pm.undoInfo(openChunk=True)
                        instance_shape.Instance(obj, instance)
                        pm.undoInfo(closeChunk=True)